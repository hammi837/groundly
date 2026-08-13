"""Conversation / lead / analytics schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class ConversationListItem(BaseModel):
    id: UUID
    visitor_id: str
    visitor_email: str | None
    started_at: datetime
    last_message_at: datetime
    message_count: int
    had_fallback: bool


class MessageOut(BaseModel):
    id: UUID
    role: str
    content: str
    cited_chunk_ids: list[UUID]
    was_fallback: bool
    created_at: datetime
    citations: list[dict] = []

    model_config = {"from_attributes": True}


class ConversationDetail(BaseModel):
    id: UUID
    visitor_id: str
    visitor_email: str | None
    started_at: datetime
    last_message_at: datetime
    messages: list[MessageOut]


class LeadOut(BaseModel):
    id: UUID
    email: EmailStr
    name: str | None
    phone: str | None
    question: str
    status: str
    conversation_id: UUID
    created_at: datetime

    model_config = {"from_attributes": True}


class LeadStatusUpdate(BaseModel):
    status: str = Field(pattern="^(new|contacted)$")


class AnalyticsOverview(BaseModel):
    conversations: int
    messages: int
    leads: int
    fallback_rate: float
    documents_ready: int
