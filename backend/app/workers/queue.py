"""Enqueue arq jobs on Redis."""

from __future__ import annotations

from arq import create_pool
from arq.connections import ArqRedis, RedisSettings

from app.core.config import settings

_pool: ArqRedis | None = None


def _redis_settings() -> RedisSettings:
    return RedisSettings.from_dsn(settings.redis_url)


async def get_arq_pool() -> ArqRedis:
    global _pool
    if _pool is None:
        _pool = await create_pool(_redis_settings())
    return _pool


async def enqueue_process_document(document_id: str, faq_text: str | None = None) -> None:
    pool = await get_arq_pool()
    await pool.enqueue_job("process_document", document_id, faq_text)
