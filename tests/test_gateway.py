"""Groq HTTP contract tests with MockTransport; no external network or real key."""
import importlib.util
import json
import os
import unittest
from unittest.mock import patch

from async_runner import run

os.environ["SECRET_KEY"]="test-only-reels-secret-at-least-32"
os.environ["GROQ_API_KEY"]=""
AVAILABLE=bool(importlib.util.find_spec("httpx") and importlib.util.find_spec("pydantic_settings"))
if AVAILABLE:
    import httpx
    from app.config import settings
    from app.services import llm


@unittest.skipUnless(AVAILABLE,"HTTP client dependencies are not installed")
class GroqGatewayTests(unittest.TestCase):
    def invoke(self,handler):
        original=httpx.AsyncClient
        transport=httpx.MockTransport(handler)
        def factory(**kwargs):return original(transport=transport,**kwargs)
        with patch.object(settings,"GROQ_API_KEY","test-only-key"),patch.object(llm.httpx,"AsyncClient",side_effect=factory):
            return run(llm.ask_llm("JSON 객체로 답해 주세요.",[{"role":"user","content":"릴스 기획"}]))

    def test_groq_endpoint_model_auth_and_json_mode(self):
        seen=[]
        def handler(request):
            seen.append(request)
            return httpx.Response(200,json={"choices":[{"message":{"content":"{\"brief_patch\":{}}"},"finish_reason":"stop"}]})
        self.assertEqual(json.loads(self.invoke(handler)),{"brief_patch":{}})
        request=seen[0];body=json.loads(request.content)
        self.assertEqual(str(request.url),"https://api.groq.com/openai/v1/chat/completions")
        self.assertEqual(request.headers["Authorization"],"Bearer test-only-key")
        self.assertEqual(body["model"],settings.GROQ_MODEL)
        self.assertEqual(body["response_format"],{"type":"json_object"})
        self.assertEqual(body["max_completion_tokens"],settings.GROQ_MAX_COMPLETION_TOKENS)
        self.assertNotIn("api_key",body)

    def test_missing_key_does_not_open_client(self):
        with patch.object(settings,"GROQ_API_KEY",""),patch.object(llm.httpx,"AsyncClient") as client:
            with self.assertRaises(llm.AIServiceError):run(llm.ask_llm("JSON",[]))
            client.assert_not_called()

    def test_timeout_maps_to_safe_exception(self):
        def handler(request):raise httpx.ReadTimeout("simulated",request=request)
        with self.assertRaises(llm.AITimeoutError):self.invoke(handler)

    def test_rate_limit_is_distinct_and_not_retried(self):
        seen=[]
        def handler(request):
            seen.append(request)
            return httpx.Response(429,json={"error":{"message":"private upstream detail"}})
        with self.assertRaises(llm.AIRateLimitError) as error:self.invoke(handler)
        self.assertEqual(len(seen),1)
        self.assertNotIn("private",str(error.exception))

    def test_http_failure_does_not_expose_body(self):
        def handler(request):return httpx.Response(503,text="private provider response")
        with self.assertRaises(llm.AIServiceError) as error:self.invoke(handler)
        self.assertNotIn("private",str(error.exception))

    def test_malformed_provider_json(self):
        def handler(request):return httpx.Response(200,text="not json")
        with self.assertRaises(llm.AIServiceError):self.invoke(handler)

    def test_empty_answer(self):
        def handler(request):return httpx.Response(200,json={"choices":[{"message":{"content":" "}}]})
        with self.assertRaises(llm.AIServiceError):self.invoke(handler)

    def test_truncated_answer_is_not_accepted(self):
        def handler(request):return httpx.Response(200,json={"choices":[{"message":{"content":"{}"},"finish_reason":"length"}]})
        with self.assertRaises(llm.AIServiceError):self.invoke(handler)


if __name__=="__main__":unittest.main()
