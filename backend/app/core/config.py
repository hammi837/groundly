"""Application settings (env-driven)."""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        # Later files override earlier — keep backend/.env last when cwd is backend/
        env_file=("../.env", ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Groundly"
    database_url: str = "postgresql+asyncpg://groundly:groundly@localhost:5432/groundly"
    database_url_sync: str = "postgresql://groundly:groundly@localhost:5432/groundly"
    redis_url: str = "redis://localhost:6379/0"
    jwt_secret: str = "change-me"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440
    register_enabled: bool = False
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    groq_api_key: str = ""
    # openai | fake
    embedding_mode: str = "fake"
    embedding_model: str = "text-embedding-3-small"
    embedding_dims: int = 1536
    # anthropic | groq | fake
    llm_mode: str = "fake"
    llm_model: str = "claude-sonnet-4-20250514"
    retrieval_top_k: int = 6
    rrf_k: int = 60
    # Minimum RRF score to call the LLM; below → immediate fallback
    relevance_threshold: float = 0.012
    max_message_chars: int = 2000
    chunk_size_chars: int = 1800
    chunk_overlap_chars: int = 200
    upload_dir: str = "uploads"
    seed_admin_email: str = "admin@riverside.demo"
    seed_admin_password: str = "riverside-demo"
    cors_origins: str = (
        "http://localhost:5173,http://127.0.0.1:5173,"
        "http://localhost:5174,http://127.0.0.1:5174,"
        "http://localhost:4173,http://127.0.0.1:4173,"
        "http://localhost:8000,http://127.0.0.1:8000,null"
    )

    @property
    def upload_path(self) -> Path:
        path = Path(self.upload_dir)
        if not path.is_absolute():
            path = Path.cwd() / path
        path.mkdir(parents=True, exist_ok=True)
        return path


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
