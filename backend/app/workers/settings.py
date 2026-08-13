"""Arq worker process — run: arq app.workers.settings.WorkerSettings"""

from __future__ import annotations

import logging

from arq.connections import RedisSettings

from app.core.config import settings
from app.services.ingest import process_document_job

logger = logging.getLogger(__name__)


async def process_document(ctx, document_id: str, faq_text: str | None = None) -> None:
    logger.info("Job process_document id=%s", document_id)
    await process_document_job(document_id, faq_text=faq_text)


async def startup(ctx) -> None:
    logging.basicConfig(level=logging.INFO)
    logger.info("Groundly ingest worker started (embedding_mode=%s)", settings.embedding_mode)


class WorkerSettings:
    functions = [process_document]
    on_startup = startup
    redis_settings = RedisSettings.from_dsn(settings.redis_url)
    max_jobs = 2
