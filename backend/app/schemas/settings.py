"""Admin settings schemas."""

from pydantic import BaseModel, Field


class SettingsOut(BaseModel):
    business_name: str
    bot_name: str
    primary_color: str
    welcome_message: str
    starter_questions: list[str]
    allowed_origins: list[str]
    rate_limit_rpm: int
    webhook_url: str | None = None
    api_key_masked: str
    api_key: str | None = None  # only when reveal=true
    embed_snippet: str


class SettingsUpdate(BaseModel):
    bot_name: str | None = Field(default=None, min_length=1, max_length=120)
    primary_color: str | None = Field(default=None, min_length=4, max_length=7)
    welcome_message: str | None = Field(default=None, min_length=1)
    starter_questions: list[str] | None = None
    allowed_origins: list[str] | None = None
    rate_limit_rpm: int | None = Field(default=None, ge=1, le=1000)
    webhook_url: str | None = None
