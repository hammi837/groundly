"""Admin conversations + leads + thin analytics (JWT)."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models import Chunk, Conversation, Document, Lead, Message, User
from app.schemas.admin import (
    AnalyticsOverview,
    ConversationDetail,
    ConversationListItem,
    LeadOut,
    LeadStatusUpdate,
    MessageOut,
)

router = APIRouter(tags=["admin"])


@router.get("/conversations", response_model=list[ConversationListItem])
async def list_conversations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[ConversationListItem]:
    result = await db.execute(
        select(Conversation)
        .where(Conversation.tenant_id == current_user.tenant_id)
        .order_by(Conversation.last_message_at.desc())
        .limit(100)
    )
    convos = list(result.scalars().all())
    items: list[ConversationListItem] = []
    for c in convos:
        msg_count = (
            await db.execute(
                select(func.count()).select_from(Message).where(Message.conversation_id == c.id)
            )
        ).scalar_one()
        fallbacks = (
            await db.execute(
                select(func.count())
                .select_from(Message)
                .where(Message.conversation_id == c.id, Message.was_fallback.is_(True))
            )
        ).scalar_one()
        items.append(
            ConversationListItem(
                id=c.id,
                visitor_id=c.visitor_id,
                visitor_email=c.visitor_email,
                started_at=c.started_at,
                last_message_at=c.last_message_at,
                message_count=int(msg_count),
                had_fallback=int(fallbacks) > 0,
            )
        )
    return items


@router.get("/conversations/{conversation_id}", response_model=ConversationDetail)
async def get_conversation(
    conversation_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ConversationDetail:
    result = await db.execute(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.tenant_id == current_user.tenant_id,
        )
    )
    convo = result.scalar_one_or_none()
    if convo is None:
        raise HTTPException(status_code=404, detail="Conversation not found")

    msg_result = await db.execute(
        select(Message)
        .where(Message.conversation_id == convo.id)
        .order_by(Message.created_at.asc())
    )
    messages = list(msg_result.scalars().all())

    # Resolve citation labels from chunk metadata
    all_ids: list[UUID] = []
    for m in messages:
        all_ids.extend(m.cited_chunk_ids or [])
    chunk_map: dict[UUID, Chunk] = {}
    if all_ids:
        chunk_rows = await db.execute(select(Chunk).where(Chunk.id.in_(all_ids)))
        chunk_map = {c.id: c for c in chunk_rows.scalars().all()}

    out_msgs: list[MessageOut] = []
    for m in messages:
        citations = []
        for cid in m.cited_chunk_ids or []:
            chunk = chunk_map.get(cid)
            if not chunk:
                continue
            meta = chunk.metadata_ if isinstance(chunk.metadata_, dict) else {}
            excerpt = chunk.content[:160] + ("..." if len(chunk.content) > 160 else "")
            citations.append(
                {
                    "chunk_id": str(cid),
                    "document": meta.get("source_name") or "document",
                    "excerpt": excerpt,
                    "page": meta.get("page"),
                }
            )
        out_msgs.append(
            MessageOut(
                id=m.id,
                role=m.role,
                content=m.content,
                cited_chunk_ids=list(m.cited_chunk_ids or []),
                was_fallback=m.was_fallback,
                created_at=m.created_at,
                citations=citations,
            )
        )

    return ConversationDetail(
        id=convo.id,
        visitor_id=convo.visitor_id,
        visitor_email=convo.visitor_email,
        started_at=convo.started_at,
        last_message_at=convo.last_message_at,
        messages=out_msgs,
    )


@router.get("/leads", response_model=list[LeadOut])
async def list_leads(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[Lead]:
    result = await db.execute(
        select(Lead)
        .where(Lead.tenant_id == current_user.tenant_id)
        .order_by(Lead.created_at.desc())
        .limit(200)
    )
    return list(result.scalars().all())


@router.patch("/leads/{lead_id}", response_model=LeadOut)
async def update_lead(
    lead_id: UUID,
    body: LeadStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Lead:
    result = await db.execute(
        select(Lead).where(Lead.id == lead_id, Lead.tenant_id == current_user.tenant_id)
    )
    lead = result.scalar_one_or_none()
    if lead is None:
        raise HTTPException(status_code=404, detail="Lead not found")
    lead.status = body.status
    await db.commit()
    await db.refresh(lead)
    return lead


@router.get("/analytics/overview", response_model=AnalyticsOverview)
async def analytics_overview(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> AnalyticsOverview:
    tid = current_user.tenant_id
    conversations = (
        await db.execute(select(func.count()).select_from(Conversation).where(Conversation.tenant_id == tid))
    ).scalar_one()
    messages = (
        await db.execute(
            select(func.count())
            .select_from(Message)
            .join(Conversation, Conversation.id == Message.conversation_id)
            .where(Conversation.tenant_id == tid)
        )
    ).scalar_one()
    assistant = (
        await db.execute(
            select(func.count())
            .select_from(Message)
            .join(Conversation, Conversation.id == Message.conversation_id)
            .where(Conversation.tenant_id == tid, Message.role == "assistant")
        )
    ).scalar_one()
    fallbacks = (
        await db.execute(
            select(func.count())
            .select_from(Message)
            .join(Conversation, Conversation.id == Message.conversation_id)
            .where(
                Conversation.tenant_id == tid,
                Message.role == "assistant",
                Message.was_fallback.is_(True),
            )
        )
    ).scalar_one()
    leads = (
        await db.execute(select(func.count()).select_from(Lead).where(Lead.tenant_id == tid))
    ).scalar_one()
    docs_ready = (
        await db.execute(
            select(func.count())
            .select_from(Document)
            .where(Document.tenant_id == tid, Document.status == "ready")
        )
    ).scalar_one()

    rate = (float(fallbacks) / float(assistant)) if assistant else 0.0
    return AnalyticsOverview(
        conversations=int(conversations),
        messages=int(messages),
        leads=int(leads),
        fallback_rate=round(rate, 3),
        documents_ready=int(docs_ready),
    )


@router.get("/analytics/unanswered")
async def unanswered(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[dict]:
    """Recent user questions that triggered fallback."""
    result = await db.execute(
        select(Message, Conversation)
        .join(Conversation, Conversation.id == Message.conversation_id)
        .where(
            Conversation.tenant_id == current_user.tenant_id,
            Message.role == "assistant",
            Message.was_fallback.is_(True),
        )
        .order_by(Message.created_at.desc())
        .limit(50)
    )
    rows = result.all()
    out: list[dict] = []
    for assistant_msg, convo in rows:
        # previous user message
        prev = await db.execute(
            select(Message)
            .where(
                Message.conversation_id == convo.id,
                Message.role == "user",
                Message.created_at <= assistant_msg.created_at,
            )
            .order_by(Message.created_at.desc())
            .limit(1)
        )
        user_msg = prev.scalar_one_or_none()
        out.append(
            {
                "conversation_id": str(convo.id),
                "question": user_msg.content if user_msg else "(unknown)",
                "created_at": assistant_msg.created_at.isoformat(),
            }
        )
    return out
