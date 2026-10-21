"""Real ASGI/SQLite integration tests; requires requirements-dev.txt."""
import importlib.util
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

os.environ["SECRET_KEY"] = "test-only-shortform-secret-at-least-32"
os.environ["DATABASE_URL"] = "sqlite://"
os.environ["LLM_API_KEY"] = ""
os.environ["SESSION_HTTPS_ONLY"] = "false"
os.environ["ENABLE_API_DOCS"] = "false"

REQUIRED = ("fastapi", "sqlalchemy", "bcrypt", "httpx", "itsdangerous", "email_validator", "pydantic_settings", "jinja2")
AVAILABLE = all(importlib.util.find_spec(name) for name in REQUIRED)
if AVAILABLE:
    from fastapi.testclient import TestClient
    from sqlalchemy import select, update
    from sqlalchemy.orm import sessionmaker
    from app.database import Base, create_db_engine, get_db
    from app.models.shortform import Conversation, ConversationTurn, ScriptVersion
    from app.main import app
    from app.services import llm
    from app.services.shortform.knowledge import KnowledgeBase
    from app.services.shortform.schemas import Brief, ChatRequest
    from app.services.shortform import store
    from app.errors import APIError
    from test_core import complete_brief, draft


@unittest.skipUnless(AVAILABLE, "Web/DB dependencies are not installed")
class APITests(unittest.TestCase):
    def setUp(self):
        self.folder=tempfile.TemporaryDirectory(dir=os.environ.get("SHORTFORM_TEST_TMPDIR"))
        self.engine=create_db_engine(f"sqlite:///{Path(self.folder.name)/'test.db'}")
        Base.metadata.create_all(self.engine)
        self.sessions=sessionmaker(self.engine,autoflush=False)
        def db_override():
            with self.sessions() as db:
                yield db
        app.dependency_overrides[get_db]=db_override
        app.state.knowledge=KnowledgeBase()
        self.client=TestClient(app)
        self.other=TestClient(app)
        self.signin(self.client,"one@example.com")
        self.signin(self.other,"two@example.com")

    def tearDown(self):
        self.client.close();self.other.close()
        app.dependency_overrides.clear()
        self.engine.dispose();self.folder.cleanup()

    def signin(self,client,email):
        body={"email":email,"password":"Shortform-test-1234"}
        self.assertEqual(client.post("/api/auth/signup",json=body).status_code,201)
        self.assertEqual(client.post("/api/auth/login",json=body).status_code,200)

    def conversation(self):
        result=self.client.post("/api/conversations",json={})
        self.assertEqual(result.status_code,201,result.text)
        return result.json()

    def chat(self,conv,*,action="message",message="아침 메뉴",version=None,base_script_id=None):
        body={"conversation_id":conv["conversation_id"],"expected_version":conv["version"] if version is None else version,
              "action":action,"message":message}
        if base_script_id:body["base_script_id"]=base_script_id
        return self.client.post("/api/chat",json=body)

    def ready(self,conv):
        with self.sessions() as db:
            db.execute(update(Conversation).where(Conversation.id==conv["conversation_id"])
                       .values(brief_json=complete_brief().model_dump_json(),phase="ready"))
            db.commit()

    def test_login_required_and_logout(self):
        self.client.post("/api/auth/logout")
        with patch.object(llm,"ask_llm") as ask:
            self.assertEqual(self.client.post("/api/conversations",json={}).status_code,401)
            self.assertEqual(self.chat({"conversation_id":1,"version":0}).status_code,401)
            ask.assert_not_called()

    def test_owner_isolation_for_detail_history_and_chat(self):
        conv=self.conversation();cid=conv["conversation_id"]
        with patch.object(llm,"ask_llm") as ask:
            self.assertEqual(self.other.get(f"/api/conversations/{cid}").status_code,404)
            self.assertEqual(self.other.get(f"/api/me/chats?conversation_id={cid}").status_code,404)
            self.assertEqual(self.other.post("/api/chat",json={"conversation_id":cid,"expected_version":0,"message":"질문"}).status_code,404)
            ask.assert_not_called()

    def test_empty_input_rejected_before_ai(self):
        conv=self.conversation()
        with patch.object(llm,"ask_llm") as ask:
            self.assertEqual(self.chat(conv,message=" ").status_code,422)
            ask.assert_not_called()

    def test_success_saves_question_answer_and_request_id(self):
        conv=self.conversation()
        async def ask(*_): return json.dumps({"brief_patch":{"topic":"아침 메뉴"}})
        with patch.object(llm,"ask_llm",side_effect=ask):
            result=self.chat(conv)
        self.assertEqual(result.status_code,200,result.text)
        data=result.json()
        self.assertEqual(data["version"],1)
        self.assertEqual(data["request_id"],result.headers["X-Request-ID"])
        rows=self.client.get(f'/api/me/chats?conversation_id={conv["conversation_id"]}').json()["items"]
        self.assertEqual(rows[0]["answer"],data["answer"])
        self.assertEqual(rows[0]["question"],"아침 메뉴")

    def test_timeout_does_not_change_brief_or_version(self):
        conv=self.conversation();self.ready(conv)
        async def ask(*_): raise llm.AITimeoutError()
        with patch.object(llm,"ask_llm",side_effect=ask):
            result=self.chat(conv,action="generate")
        self.assertEqual(result.status_code,504,result.text)
        current=self.client.get(f'/api/conversations/{conv["conversation_id"]}').json()
        self.assertEqual(current["version"],0)
        self.assertEqual(current["phase"],"ready")
        self.assertFalse(current["processing"])
        self.assertIsNone(current["latest_script"])
        rows=self.client.get(f'/api/me/chats?conversation_id={conv["conversation_id"]}').json()["items"]
        self.assertEqual(rows[0]["error_code"],"AI_TIMEOUT")
        self.assertIsNone(rows[0]["answer"])

    def test_public_pdf_evidence_is_sent_returned_and_persisted(self):
        conv = self.conversation()
        async def ask(system, messages):
            data = json.loads(messages[0]["content"].split("\n", 1)[1])
            self.assertIn("suspense-anticipation", [c["card_id"] for c in data["reference_cards"]])
            return json.dumps({"intent":"explanation", "answer":"불확실성과 서스펜스는 구별됩니다.",
                               "card_ids":["suspense-anticipation"]})
        with patch.object(llm, "ask_llm", side_effect=ask):
            response = self.chat(conv, message="서스펜스 설명")
        self.assertEqual(response.status_code, 200, response.text)
        ref = response.json()["references"][0]
        self.assertEqual(ref["pdf_page_start"], 10)
        self.assertEqual(ref["license"], "CC BY 4.0")
        self.assertTrue(ref["limitations"])
        history = self.client.get(f'/api/me/chats?conversation_id={conv["conversation_id"]}').json()
        self.assertEqual(history["items"][0]["response"]["references"][0], ref)

    def test_provider_and_invalid_json_errors_are_safe(self):
        conv=self.conversation()
        async def failed(*_): raise llm.AIServiceError("upstream private body")
        async def malformed(*_): return "<html>bad</html>"
        for ask in [failed,malformed]:
            with self.subTest(ask=ask.__name__),patch.object(llm,"ask_llm",side_effect=ask):
                result=self.chat(conv)
                self.assertEqual(result.status_code,502,result.text)
                self.assertNotIn("upstream private body",result.text)

    def test_codyssey_rate_limit_preserves_brief_and_releases_lease(self):
        conv=self.conversation()
        async def limited(*_):raise llm.AIRateLimitError()
        with patch.object(llm,"ask_llm",side_effect=limited):result=self.chat(conv)
        self.assertEqual(result.status_code,429,result.text)
        self.assertEqual(result.json()["error"],"AI_RATE_LIMIT")
        current=self.client.get(f'/api/conversations/{conv["conversation_id"]}').json()
        self.assertEqual(current["version"],0)
        self.assertFalse(current["processing"])

    def test_authentication_or_permission_error_is_actionable_and_keeps_state(self):
        for failure, code in [(llm.AIAuthenticationError, "AI_AUTH_ERROR"),
                              (llm.AIAccessDeniedError, "AI_ACCESS_DENIED")]:
            conv = self.conversation()
            async def rejected(*_):
                raise failure("private provider response")
            with self.subTest(code=code), patch.object(llm, "ask_llm", side_effect=rejected):
                response = self.chat(conv)
            self.assertEqual(response.status_code, 502)
            self.assertEqual(response.json()["error"], code)
            self.assertNotIn("private", response.text)
            current = self.client.get(f'/api/conversations/{conv["conversation_id"]}').json()
            self.assertEqual(current["version"], 0)
            self.assertFalse(current["processing"])
            rows = self.client.get(f'/api/me/chats?conversation_id={conv["conversation_id"]}').json()["items"]
            self.assertEqual(rows[0]["error_code"], code)

    def test_stale_version_does_not_call_ai(self):
        conv=self.conversation()
        async def ask(*_): return '{"brief_patch":{}}'
        with patch.object(llm,"ask_llm",side_effect=ask): self.chat(conv)
        with patch.object(llm,"ask_llm") as blocked:
            self.assertEqual(self.chat(conv).status_code,409)
            blocked.assert_not_called()

    def test_generation_and_revision_keep_versions_and_sources(self):
        conv=self.conversation();self.ready(conv)
        async def ask(*_): return json.dumps(draft())
        with patch.object(llm,"ask_llm",side_effect=ask):
            first=self.chat(conv,action="generate").json()
            second=self.chat(conv,action="revise",version=1,base_script_id=first["script"]["script_id"]).json()
        self.assertEqual(second["script"]["revision"],2)
        self.assertEqual(second["script"]["parent_script_id"],first["script"]["script_id"])
        self.assertTrue(second["references"])
        with self.sessions() as db:self.assertEqual(len(db.scalars(select(ScriptVersion)).all()),2)

    def test_conversations_do_not_share_context(self):
        a=self.conversation();b=self.conversation();seen=[]
        async def ask(system,messages):
            seen.append(json.dumps(messages,ensure_ascii=False))
            return '{"brief_patch":{}}'
        with patch.object(llm,"ask_llm",side_effect=ask):
            self.chat(a,message="private-topic-unique")
            self.chat(b,message="other-topic")
        self.assertNotIn("private-topic-unique",seen[-1])

    def test_durable_lease_rejects_second_request(self):
        conv=self.conversation();body=ChatRequest(conversation_id=conv["conversation_id"],expected_version=0,message="첫 요청")
        user_id=self.client.get("/api/me").json()["id"]
        with self.sessions() as first:
            context=store.begin_turn(first,user_id,body,"test-lease-one",60)
        with self.sessions() as second:
            with self.assertRaises(APIError) as error:store.begin_turn(second,user_id,body,"test-lease-two",60)
            self.assertEqual(error.exception.status_code,409)
        with self.sessions() as third:store.fail_turn(third,context,"test-lease-one","AI_ERROR")

    def test_db_save_failure_returns_503_and_releases_lease(self):
        from sqlalchemy.exc import OperationalError
        conv=self.conversation()
        async def ask(*_):return '{"brief_patch":{}}'
        with patch.object(llm,"ask_llm",side_effect=ask),patch.object(store,"complete_turn",side_effect=OperationalError("sql",{},Exception())):
            result=self.chat(conv)
        self.assertEqual(result.status_code,503,result.text)
        current=self.client.get(f'/api/conversations/{conv["conversation_id"]}').json()
        self.assertFalse(current["processing"])
        self.assertEqual(current["version"],0)

    def test_page_redirect_and_no_generated_html_execution(self):
        self.assertIn("STORY / REELS",self.client.get("/").text)
        self.assertIn("frame-ancestors 'none'",self.client.get("/").headers["Content-Security-Policy"])
        self.assertEqual(self.client.get("/docs").status_code,404)

    def test_account_normalization_duplicate_and_extra_fields(self):
        body = {"email": " ＮｅｗＵｓｅｒ＠ｅｘａｍｐｌｅ．ｃｏｍ ", "password": "Shortform-test-1234"}
        created = self.client.post("/api/auth/signup", json=body)
        self.assertEqual(created.status_code, 201)
        self.assertEqual(created.json()["email"], "newuser@example.com")
        body["email"] = "NEWUSER@example.com"
        self.assertEqual(self.client.post("/api/auth/signup", json=body).status_code, 409)
        body["user_id"] = 999
        self.assertEqual(self.client.post("/api/auth/signup", json=body).status_code, 422)

    def test_existing_bcrypt_login_upgrades_hash_without_changing_identity(self):
        import bcrypt
        from app.models.user import User
        password = "Legacy-password-1234"
        with self.sessions() as db:
            old = User(email="legacy@example.com", password_hash=bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode())
            db.add(old)
            db.commit()
            identity = old.id
        response = self.client.post("/api/auth/login", json={"email": "legacy@example.com", "password": password})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["id"], identity)
        with self.sessions() as db:
            stored = db.get(User, identity).password_hash
            self.assertTrue(stored.startswith("scrypt$"))
        self.assertEqual(self.client.get("/api/me").json()["id"], identity)

    def test_account_invalid_unicode_is_a_safe_validation_error(self):
        payload = b'{"email":"\\ud800@example.com","password":"Shortform-test-1234"}'
        response = self.client.post("/api/auth/signup", content=payload, headers={"content-type": "application/json"})
        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.json()["error"], "INVALID_INPUT")

    def test_deleted_account_cookie_cannot_become_a_new_account(self):
        from app.models.user import User
        from app.security import hash_password
        identity = self.client.get("/api/me").json()["id"]
        with self.sessions() as db:
            db.delete(db.get(User, identity))
            db.commit()
            fresh = User(email="fresh@example.com", password_hash=hash_password("Fresh-password-1234"))
            db.add(fresh)
            db.commit()
            self.assertNotEqual(identity, fresh.id)
        self.assertEqual(self.client.get("/api/me").status_code, 401)


if __name__ == "__main__":unittest.main()
