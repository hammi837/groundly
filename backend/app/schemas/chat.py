"""Chat / handoff schemas."""

from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class ChatMessageRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    visitor_id: str = Field(min_length=1, max_length=255)
    conversation_id: UUID | None = None


class CitationOut(BaseModel):
    chunk_id: UUID
    document: str
    excerpt: str
    page: int | None = None


class ChatMessageResponse(BaseModel):
    conversation_id: UUID
    answer: str
    citations: list[CitationOut]
    was_fallback: bool


class HandoffRequest(BaseModel):
    conversation_id: UUID
    visitor_id: str = Field(min_length=1, max_length=255)
    email: EmailStr
    question: str = Field(min_length=1, max_length=4000)
    name: str | None = Field(default=None, max_length=255)
    phone: str | None = Field(default=None, max_length=64)


class HandoffResponse(BaseModel):
    id: UUID
    status: str
    message: str = "Thanks — the team will follow up."
