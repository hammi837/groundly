"""Public chat API — X-Api-Key + origin + rate limit."""

from __future__ import annotations

import json
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.deps import get_tenant_from_api_key
from app.db.session import get_db
from app.models import Conversation, Lead, Tenant
from app.schemas.chat import (
    ChatMessageRequest,
    ChatMessageResponse,
    CitationOut,
    HandoffRequest,
    HandoffResponse,
)
from app.services.rag import RagResponse, iter_rag_stream, run_rag

router = APIRouter(prefix="/chat", tags=["chat"])


def _to_response(rag: RagResponse) -> ChatMessageResponse:
    return ChatMessageResponse(
        conversation_id=rag.conversation_id,
        answer=rag.answer,
        citations=[
            CitationOut(
                chunk_id=c.chunk_id,
                document=c.document,
                excerpt=c.excerpt,
                page=c.page,
            )
            for c in rag.citations
        ],
        was_fallback=rag.was_fallback,
    )


@router.post("/message", response_model=ChatMessageResponse)
async def chat_message(
    body: ChatMessageRequest,
    tenant: Tenant = Depends(get_tenant_from_api_key),
    db: AsyncSession = Depends(get_db),
) -> ChatMessageResponse:
    if len(body.message) > settings.max_message_chars:
        raise HTTPException(status_code=400, detail="Message too long")
    try:
        rag = await run_rag(
            db,
            tenant=tenant,
            message=body.message.strip(),
            visitor_id=body.visitor_id,
            conversation_id=body.conversation_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return _to_response(rag)


@router.post("/message/stream")
async def chat_message_stream(
    body: ChatMessageRequest,
    tenant: Tenant = Depends(get_tenant_from_api_key),
    db: AsyncSession = Depends(get_db),
) -> StreamingResponse:
    if len(body.message) > settings.max_message_chars:
        raise HTTPException(status_code=400, detail="Message too long")

    async def event_gen():
        try:
            async for kind, payload in iter_rag_stream(
                db,
                tenant=tenant,
                message=body.message.strip(),
                visitor_id=body.visitor_id,
                conversation_id=body.conversation_id,
            ):
                if kind == "token":
                    yield f"event: token\ndata: {json.dumps({'text': payload})}\n\n"
                else:
                    rag: RagResponse = payload
                    data = _to_response(rag).model_dump(mode="json")
                    yield f"event: final\ndata: {json.dumps(data)}\n\n"
        except ValueError as exc:
            yield f"event: error\ndata: {json.dumps({'detail': str(exc)})}\n\n"
        except Exception as exc:  # noqa: BLE001
            yield f"event: error\ndata: {json.dumps({'detail': 'Chat failed', 'error': str(exc)})}\n\n"

    return StreamingResponse(
        event_gen(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/handoff", response_model=HandoffResponse, status_code=status.HTTP_201_CREATED)
async def chat_handoff(
    body: HandoffRequest,
    tenant: Tenant = Depends(get_tenant_from_api_key),
    db: AsyncSession = Depends(get_db),
) -> HandoffResponse:
    result = await db.execute(
        select(Conversation).where(
            Conversation.id == body.conversation_id,
            Conversation.tenant_id == tenant.id,
            Conversation.visitor_id == body.visitor_id,
        )
    )
    convo = result.scalar_one_or_none()
    if convo is None:
        raise HTTPException(status_code=404, detail="Conversation not found")

    lead = Lead(
        tenant_id=tenant.id,
        conversation_id=convo.id,
        email=str(body.email).lower(),
        name=body.name,
        phone=body.phone,
        question=body.question.strip(),
        status="new",
    )
    convo.visitor_email = str(body.email).lower()
    db.add(lead)
    await db.commit()
    await db.refresh(lead)

    return HandoffResponse(id=lead.id, status=lead.status)
