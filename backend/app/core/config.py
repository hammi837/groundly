"""Application settings (env-driven)."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Groundly"
    database_url: str = "postgresql+asyncpg://groundly:groundly@localhost:5432/groundly"
    redis_url: str = "redis://localhost:6379/0"
    jwt_secret: str = "change-me"
    jwt_algorithm: str = "HS256"
    register_enabled: bool = False
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    upload_dir: str = "uploads"


settings = Settings()
