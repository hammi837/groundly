"""Document API schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class DocumentOut(BaseModel):
    id: UUID
    source_type: str
    source_name: str
    status: str
    error_message: str | None = None
    chunk_count: int
    bytes: int | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class FaqCreate(BaseModel):
    question: str = Field(min_length=3, max_length=2000)
    answer: str = Field(min_length=3, max_length=20000)
    title: str | None = Field(default=None, max_length=255)


class DocumentUpdate(BaseModel):
    source_name: str | None = Field(default=None, max_length=255)
    question: str | None = Field(default=None, min_length=3, max_length=2000)
    answer: str | None = Field(default=None, min_length=3, max_length=20000)


class DocumentContentOut(BaseModel):
    id: UUID
    source_type: str
    source_name: str
    status: str
    text: str
    question: str | None = None
    answer: str | None = None
