"""RAG orchestration — retrieve, threshold, generate, persist."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models import Conversation, Message, Tenant, UsageEvent
from app.services.llm import (
    LlmResult,
    closing_reply,
    generate_answer,
    is_conversation_closing,
    stream_answer_tokens,
)
from app.services.retrieval import RetrievedChunk, hybrid_search


@dataclass
class Citation:
    chunk_id: UUID
    document: str
    excerpt: str
    page: int | None = None


@dataclass
class RagResponse:
    conversation_id: UUID
    answer: str
    citations: list[Citation]
    was_fallback: bool
    retrieval_scores: dict[str, float]


def _citations_from_chunks(chunks: list[RetrievedChunk], *, limit: int = 3) -> list[Citation]:
    out: list[Citation] = []
    seen_docs: set[str] = set()
    for c in chunks[: max(limit * 2, limit)]:
        # Prefer unique documents so chips stay readable
        if c.source_name in seen_docs and len(out) >= 1:
            continue
        excerpt = c.content.strip()
        if len(excerpt) > 180:
            excerpt = excerpt[:177] + "..."
        page = c.metadata.get("page")
        out.append(
            Citation(
                chunk_id=c.id,
                document=c.source_name,
                excerpt=excerpt,
                page=int(page) if page is not None else None,
            )
        )
        seen_docs.add(c.source_name)
        if len(out) >= limit:
            break
    return out


async def _get_or_create_conversation(
    db: AsyncSession,
    *,
    tenant: Tenant,
    conversation_id: UUID | None,
    visitor_id: str,
) -> Conversation:
    if conversation_id:
        result = await db.execute(
            select(Conversation).where(
                Conversation.id == conversation_id,
                Conversation.tenant_id == tenant.id,
            )
        )
        existing = result.scalar_one_or_none()
        if existing is None:
            raise ValueError("conversation_id not found for this tenant")
        return existing

    convo = Conversation(
        id=uuid4(),
        tenant_id=tenant.id,
        visitor_id=visitor_id,
    )
    db.add(convo)
    await db.flush()
    return convo


async def run_rag(
    db: AsyncSession,
    *,
    tenant: Tenant,
    message: str,
    visitor_id: str,
    conversation_id: UUID | None = None,
) -> RagResponse:
    convo = await _get_or_create_conversation(
        db, tenant=tenant, conversation_id=conversation_id, visitor_id=visitor_id
    )

    db.add(
        Message(
            conversation_id=convo.id,
            role="user",
            content=message,
        )
    )

    if is_conversation_closing(message):
        result = closing_reply()
        used_chunks: list[RetrievedChunk] = []
        chunks: list[RetrievedChunk] = []
    else:
        chunks = await hybrid_search(db, tenant_id=tenant.id, query=message)
        top_score = chunks[0].score if chunks else 0.0
        weak = (not chunks) or top_score < settings.relevance_threshold

        if weak:
            result = LlmResult(
                answer=(
                    "I’m not sure about that. I can connect you with the team — "
                    "please leave your email and someone will follow up."
                ),
                was_fallback=True,
            )
            used_chunks = []
        else:
            result = await generate_answer(
                business_name=tenant.name,
                question=message,
                chunks=chunks,
            )
            used_chunks = [] if result.was_fallback else chunks

    citations = _citations_from_chunks(used_chunks)
    cited_ids = [c.chunk_id for c in citations]
    scores = {str(c.id): c.score for c in chunks}

    db.add(
        Message(
            conversation_id=convo.id,
            role="assistant",
            content=result.answer,
            cited_chunk_ids=cited_ids,
            retrieval_scores=scores,
            was_fallback=result.was_fallback,
            prompt_tokens=result.prompt_tokens or None,
            completion_tokens=result.completion_tokens or None,
        )
    )
    if result.prompt_tokens or result.completion_tokens:
        db.add(
            UsageEvent(
                tenant_id=tenant.id,
                event_type="chat",
                prompt_tokens=result.prompt_tokens,
                completion_tokens=result.completion_tokens,
            )
        )

    convo.last_message_at = datetime.now(timezone.utc)
    await db.commit()

    return RagResponse(
        conversation_id=convo.id,
        answer=result.answer,
        citations=citations,
        was_fallback=result.was_fallback,
        retrieval_scores=scores,
    )


async def iter_rag_stream(
    db: AsyncSession,
    *,
    tenant: Tenant,
    message: str,
    visitor_id: str,
    conversation_id: UUID | None = None,
):
    """
    Async generator yielding ("token", str) and finally ("final", RagResponse).
    Persists messages at the end.
    """
    convo = await _get_or_create_conversation(
        db, tenant=tenant, conversation_id=conversation_id, visitor_id=visitor_id
    )
    db.add(Message(conversation_id=convo.id, role="user", content=message))
    await db.flush()

    if is_conversation_closing(message):
        result = closing_reply()
        for piece in [result.answer]:
            yield ("token", piece)
        used_chunks: list[RetrievedChunk] = []
        chunks: list[RetrievedChunk] = []
    else:
        chunks = await hybrid_search(db, tenant_id=tenant.id, query=message)
        top_score = chunks[0].score if chunks else 0.0
        weak = (not chunks) or top_score < settings.relevance_threshold

        if weak:
            result = LlmResult(
                answer=(
                    "I’m not sure about that. I can connect you with the team — "
                    "please leave your email and someone will follow up."
                ),
                was_fallback=True,
            )
            for piece in [result.answer]:
                yield ("token", piece)
            used_chunks = []
        else:
            result = None
            async for item in stream_answer_tokens(
                business_name=tenant.name,
                question=message,
                chunks=chunks,
            ):
                if isinstance(item, LlmResult):
                    result = item
                else:
                    yield ("token", item)
            assert result is not None
            used_chunks = [] if result.was_fallback else chunks

    citations = _citations_from_chunks(used_chunks)
    cited_ids = [c.chunk_id for c in citations]
    scores = {str(c.id): c.score for c in chunks}

    db.add(
        Message(
            conversation_id=convo.id,
            role="assistant",
            content=result.answer,
            cited_chunk_ids=cited_ids,
            retrieval_scores=scores,
            was_fallback=result.was_fallback,
            prompt_tokens=result.prompt_tokens or None,
            completion_tokens=result.completion_tokens or None,
        )
    )
    if result.prompt_tokens or result.completion_tokens:
        db.add(
            UsageEvent(
                tenant_id=tenant.id,
                event_type="chat",
                prompt_tokens=result.prompt_tokens,
                completion_tokens=result.completion_tokens,
            )
        )
    convo.last_message_at = datetime.now(timezone.utc)
    await db.commit()

    yield (
        "final",
        RagResponse(
            conversation_id=convo.id,
            answer=result.answer,
            citations=citations,
            was_fallback=result.was_fallback,
            retrieval_scores=scores,
        ),
    )
