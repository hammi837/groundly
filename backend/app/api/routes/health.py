"""Health check — DB + Redis."""

from fastapi import APIRouter
from redis.asyncio import from_url as redis_from_url
from sqlalchemy import text

from app.core.config import settings
from app.db.session import engine

router = APIRouter(tags=["health"])


@router.get("/health")
async def health() -> dict:
    db_ok = False
    redis_ok = False
    errors: list[str] = []

    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        db_ok = True
    except Exception as exc:  # noqa: BLE001 — surface in health payload
        errors.append(f"database: {exc}")

    try:
        client = redis_from_url(settings.redis_url, decode_responses=True)
        try:
            pong = await client.ping()
            redis_ok = bool(pong)
        finally:
            await client.aclose()
    except Exception as exc:  # noqa: BLE001
        errors.append(f"redis: {exc}")

    status = "ok" if db_ok and redis_ok else "degraded"
    return {
        "status": status,
        "service": "groundly",
        "database": db_ok,
        "redis": redis_ok,
        "errors": errors,
    }
