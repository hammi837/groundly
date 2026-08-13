"""Local file storage for uploaded PDFs."""

from __future__ import annotations

from pathlib import Path
from uuid import UUID

from app.core.config import settings


def tenant_dir(tenant_id: UUID) -> Path:
    path = settings.upload_path / str(tenant_id)
    path.mkdir(parents=True, exist_ok=True)
    return path


def document_pdf_path(tenant_id: UUID, document_id: UUID) -> Path:
    return tenant_dir(tenant_id) / f"{document_id}.pdf"


def save_pdf(tenant_id: UUID, document_id: UUID, data: bytes) -> Path:
    path = document_pdf_path(tenant_id, document_id)
    path.write_bytes(data)
    return path


def delete_pdf(tenant_id: UUID, document_id: UUID) -> None:
    path = document_pdf_path(tenant_id, document_id)
    if path.exists():
        path.unlink()
