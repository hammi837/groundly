"""Pydantic schemas for auth."""

from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)


class RegisterRequest(BaseModel):
    business_name: str = Field(min_length=2, max_length=255)
    email: EmailStr
    password: str = Field(min_length=8)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TenantSummary(BaseModel):
    id: UUID
    name: str
    bot_name: str
    primary_color: str

    model_config = {"from_attributes": True}


class MeResponse(BaseModel):
    id: UUID
    email: EmailStr
    tenant: TenantSummary

    model_config = {"from_attributes": True}
