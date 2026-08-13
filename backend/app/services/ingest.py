"""Document ingestion pipeline — extract → chunk → embed → store."""

from __future__ import annotations

import logging
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings
from app.models import Chunk, Document, UsageEvent
from app.services.chunking import chunk_pages, chunk_plain_text
from app.services.embeddings import embed_texts
from app.services.extract import extract_pdf_pages
from app.services.storage import document_pdf_path

logger = logging.getLogger(__name__)


def _session_factory() -> async_sessionmaker[AsyncSession]:
    engine = create_async_engine(settings.database_url, echo=False)
    return async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False), engine


async def process_document_job(document_id: str, faq_text: str | None = None) -> None:
    """Arq entrypoint — owns its own DB session."""
    Session, engine = _session_factory()
    try:
        async with Session() as db:
            await _ingest(db, UUID(document_id), faq_text=faq_text)
            await db.commit()
    finally:
        await engine.dispose()


async def _ingest(db: AsyncSession, document_id: UUID, faq_text: str | None = None) -> None:
    result = await db.execute(select(Document).where(Document.id == document_id))
    doc = result.scalar_one_or_none()
    if doc is None:
        logger.warning("Document %s not found — skipping", document_id)
        return

    doc.status = "processing"
    doc.error_message = None
    await db.flush()

    try:
        chunks_data = await _build_chunks(doc, faq_text=faq_text)
        if not chunks_data:
            raise ValueError(
                "No readable text found. For PDFs, use a text-based file (not a scanned image)."
            )

        texts = [c.content for c in chunks_data]
        vectors, embed_tokens = await embed_texts(texts)

        # Replace any previous chunks (re-process safe)
        await db.execute(delete(Chunk).where(Chunk.document_id == doc.id))

        for chunk, vector in zip(chunks_data, vectors, strict=True):
            db.add(
                Chunk(
                    document_id=doc.id,
                    tenant_id=doc.tenant_id,
                    content=chunk.content,
                    embedding=vector,
                    metadata_=chunk.metadata,
                )
            )

        db.add(
            UsageEvent(
                tenant_id=doc.tenant_id,
                event_type="embed",
                embedding_tokens=embed_tokens,
            )
        )

        doc.chunk_count = len(chunks_data)
        doc.status = "ready"
        doc.error_message = None
        logger.info("Ingested document %s (%s chunks)", doc.id, doc.chunk_count)
    except Exception as exc:  # noqa: BLE001 — persist failure for UI
        logger.exception("Ingest failed for %s", document_id)
        doc.status = "failed"
        doc.error_message = str(exc)[:2000]
        doc.chunk_count = 0


async def _build_chunks(doc: Document, faq_text: str | None):
    if doc.source_type == "faq":
        text = (faq_text or "").strip()
        if not text:
            raise ValueError("FAQ content was empty.")
        return chunk_plain_text(
            text,
            source_name=doc.source_name,
            source_type="faq",
            extra_metadata={"section": "faq"},
        )

    if doc.source_type == "pdf":
        path = document_pdf_path(doc.tenant_id, doc.id)
        if not path.exists():
            raise ValueError("Uploaded PDF file is missing on disk.")
        pages = extract_pdf_pages(str(path))
        if not pages:
            # try whole-file empty message
            raise ValueError(
                "Could not extract text from this PDF. It may be empty or image-only."
            )
        return chunk_pages(pages, source_name=doc.source_name, source_type="pdf")

    raise ValueError(f"Unsupported source_type for Phase 2: {doc.source_type}")
