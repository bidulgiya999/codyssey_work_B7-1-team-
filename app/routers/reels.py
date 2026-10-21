"""A/B/C public contract. Every conversation and log lookup is owner-scoped."""
import asyncio
import json
import logging
import time
from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.dependencies import require_login
from app.errors import APIError
from app.models.reels import Conversation, ReelsTurn
from app.services import llm
from app.services.reels.coach import CoachError, ReelsCoach
from app.services.reels.schemas import Brief, ChatRequest, ConversationCreate
from app.services.reels import store

router = APIRouter(prefix="/api", tags=["reels"])
logger = logging.getLogger(__name__)
Limit = Annotated[int, Query(ge=1, le=100)]


@router.get("/me")
def me(user=Depends(require_login)):
    return {"id": user.id, "email": user.email, "ai_provider": "codyssey", "ai_configured": bool(settings.LLM_API_KEY)}


@router.post("/conversations", status_code=201)
def create_conversation(body: ConversationCreate, user=Depends(require_login), db: Session = Depends(get_db)):
    item = Conversation(user_id=user.id, title=body.title, brief_json=Brief().model_dump_json())
    db.add(item)
    db.commit()
    db.refresh(item)
    return store.conversation_payload(db, item)


@router.get("/conversations")
def conversations(limit: Limit = 20, offset: Annotated[int, Query(ge=0)] = 0,
                  user=Depends(require_login), db: Session = Depends(get_db)):
    rows = db.scalars(select(Conversation).where(Conversation.user_id == user.id)
                      .order_by(Conversation.updated_at.desc(), Conversation.id.desc()).offset(offset).limit(limit)).all()
    return {"items": [store.conversation_payload(db, row) for row in rows], "limit": limit, "offset": offset}


@router.get("/conversations/{conversation_id}")
def conversation(conversation_id: int, user=Depends(require_login), db: Session = Depends(get_db)):
    return store.conversation_payload(db, store.owned(db, user.id, conversation_id))


@router.get("/me/chats")
def history(conversation_id: int, limit: Limit = 20, offset: Annotated[int, Query(ge=0)] = 0,
            user=Depends(require_login), db: Session = Depends(get_db)):
    store.owned(db, user.id, conversation_id)
    rows = db.scalars(select(ReelsTurn).where(ReelsTurn.user_id == user.id,
                                             ReelsTurn.conversation_id == conversation_id)
                      .order_by(ReelsTurn.id.desc()).offset(offset).limit(limit)).all()
    return {"items": [{"chat_id": row.id, "question": row.question, "answer": row.answer,
                       "status": row.status, "error_code": row.error_code, "request_id": row.request_id,
                       "created_at": store.timestamp(row.created_at),
                       "response": json.loads(row.response_json) if row.response_json else None} for row in rows],
            "limit": limit, "offset": offset}


@router.post("/chat")
async def chat(body: ChatRequest, request: Request, user=Depends(require_login), db: Session = Depends(get_db)):
    request_id = request.state.request_id
    context = None
    user_id = user.id

    async def ask(system, messages):
        started = time.perf_counter()
        logger.info("ai_call_start user_id=%s conversation_id=%s request_id=%s", user_id, body.conversation_id, request_id)
        try:
            answer = await llm.ask_llm(system, messages)
        except llm.AITimeoutError:
            raise CoachError("AI_TIMEOUT", "응답이 지연되고 있어요. 잠시 후 다시 시도해 주세요.", 504) from None
        except llm.AIAuthenticationError:
            logger.warning("ai_provider_rejected user_id=%s request_id=%s upstream_status=401", user_id, request_id)
            raise CoachError("AI_AUTH_ERROR", "코디세이 API 인증에 실패했습니다. 서버의 API 키 설정을 확인해 주세요.") from None
        except llm.AIAccessDeniedError:
            logger.warning("ai_provider_rejected user_id=%s request_id=%s upstream_status=403", user_id, request_id)
            raise CoachError("AI_ACCESS_DENIED", "코디세이에서 채팅 요청을 거부했습니다. 계정·API 키의 사용 권한과 선택한 모델을 확인해 주세요.") from None
        except llm.AIRateLimitError:
            raise CoachError("AI_RATE_LIMIT", "AI 요청 한도에 도달했습니다. 잠시 후 다시 시도해 주세요.", 429) from None
        except llm.AIServiceError:
            raise CoachError("AI_ERROR", "AI에 연결하지 못했습니다. 잠시 후 다시 시도해 주세요.") from None
        logger.info("ai_call_success user_id=%s request_id=%s latency_ms=%s", user_id, request_id, int((time.perf_counter()-started)*1000))
        return answer

    try:
        context = store.begin_turn(db, user_id, body, request_id, settings.CHAT_TOTAL_TIMEOUT_SECONDS + 30)
        coach = ReelsCoach(request.app.state.knowledge, ask, timeout=settings.CHAT_TOTAL_TIMEOUT_SECONDS)
        result = await coach.process(action=body.action, message=body.message, brief=context.brief,
                                     phase=context.phase, history=context.history, latest_script=context.latest_script)
        return store.complete_turn(db, context, request_id, result)
    except (CoachError, APIError) as exc:
        code = exc.code if isinstance(exc, CoachError) else exc.error
        logger.warning("%s user_id=%s request_id=%s reason=%s",
                       "ai_call_fail" if isinstance(exc, CoachError) else "request_rejected", user_id, request_id, code)
        if context:
            try:
                store.fail_turn(db, context, request_id, code)
            except SQLAlchemyError:
                db.rollback()
                logger.error("db_save_fail user_id=%s request_id=%s operation=failure_record", user_id, request_id)
                raise APIError(503, "DB_ERROR", "오류 기록을 저장하지 못했습니다. 잠시 후 다시 시도해 주세요.") from None
        if isinstance(exc, CoachError):
            raise APIError(exc.status, exc.code, exc.message) from None
        raise
    except asyncio.CancelledError:
        if context:
            store.fail_turn(db, context, request_id, "REQUEST_CANCELLED")
        raise
    except SQLAlchemyError:
        db.rollback()
        logger.error("db_save_fail user_id=%s request_id=%s", user_id, request_id)
        if context:
            try:
                store.fail_turn(db, context, request_id, "DB_ERROR")
            except SQLAlchemyError:
                db.rollback()
                logger.error("db_save_fail user_id=%s request_id=%s operation=failure_record", user_id, request_id)
        raise APIError(503, "DB_ERROR", "대화를 저장하지 못했습니다. 잠시 후 다시 시도해 주세요.") from None
    except Exception as exc:
        logger.error("chat_fail user_id=%s request_id=%s reason=%s", user_id, request_id, type(exc).__name__)
        if context:
            try:
                store.fail_turn(db, context, request_id, "INTERNAL_ERROR")
            except SQLAlchemyError:
                db.rollback()
                logger.error("db_save_fail user_id=%s request_id=%s operation=failure_record", user_id, request_id)
        raise APIError(500, "INTERNAL_ERROR", "요청을 처리하지 못했습니다. 잠시 후 다시 시도해 주세요.") from None
