"""Document management routes (Phase 2 + edit)."""

from __future__ import annotations

import re
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models import Chunk, Document, User
from app.schemas.documents import DocumentContentOut, DocumentOut, DocumentUpdate, FaqCreate
from app.services import storage
from app.services.ingest import process_document_job

router = APIRouter(prefix="/documents", tags=["documents"])

MAX_PDF_BYTES = 15 * 1024 * 1024


def _safe_name(name: str) -> str:
    cleaned = re.sub(r"[^\w.\- ]+", "", name).strip()
    return cleaned[:240] or "document.pdf"


def _parse_faq_text(text: str) -> tuple[str | None, str | None]:
    q_match = re.search(r"(?is)question:\s*(.+?)(?:\n\s*\n|\n\s*answer:)", text)
    a_match = re.search(r"(?is)answer:\s*(.+)$", text)
    question = q_match.group(1).strip() if q_match else None
    answer = a_match.group(1).strip() if a_match else None
    return question, answer


async def _get_tenant_doc(
    db: AsyncSession, *, document_id: str, tenant_id: UUID
) -> Document:
    try:
        doc_uuid = UUID(document_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid document id") from exc

    result = await db.execute(
        select(Document).where(
            Document.id == doc_uuid,
            Document.tenant_id == tenant_id,
        )
    )
    doc = result.scalar_one_or_none()
    if doc is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


async def _chunk_text(db: AsyncSession, document_id: UUID) -> str:
    result = await db.execute(
        select(Chunk.content)
        .where(Chunk.document_id == document_id)
        .order_by(Chunk.created_at.asc())
    )
    parts = [row[0] for row in result.all()]
    return "\n\n".join(parts).strip()


@router.get("", response_model=list[DocumentOut])
async def list_documents(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[Document]:
    result = await db.execute(
        select(Document)
        .where(Document.tenant_id == current_user.tenant_id)
        .order_by(Document.created_at.desc())
    )
    return list(result.scalars().all())


@router.get("/{document_id}/content", response_model=DocumentContentOut)
async def get_document_content(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> DocumentContentOut:
    doc = await _get_tenant_doc(db, document_id=document_id, tenant_id=current_user.tenant_id)
    text = await _chunk_text(db, doc.id)
    question, answer = _parse_faq_text(text) if doc.source_type == "faq" else (None, None)
    return DocumentContentOut(
        id=doc.id,
        source_type=doc.source_type,
        source_name=doc.source_name,
        status=doc.status,
        text=text,
        question=question,
        answer=answer,
    )


@router.patch("/{document_id}", response_model=DocumentOut)
async def update_document(
    document_id: str,
    body: DocumentUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Document:
    doc = await _get_tenant_doc(db, document_id=document_id, tenant_id=current_user.tenant_id)

    if body.source_name is not None:
        doc.source_name = _safe_name(body.source_name)

    faq_text: str | None = None
    if doc.source_type == "faq":
        if body.question is None or body.answer is None:
            # allow rename-only without re-ingest
            if body.question is not None or body.answer is not None:
                raise HTTPException(
                    status_code=400,
                    detail="FAQ edits require both question and answer.",
                )
        else:
            faq_text = (
                f"Question: {body.question.strip()}\n\nAnswer: {body.answer.strip()}"
            )
            doc.bytes = len(faq_text.encode("utf-8"))
            doc.status = "processing"
            doc.error_message = None
            doc.chunk_count = 0

    await db.commit()
    await db.refresh(doc)

    if faq_text is not None:
        await process_document_job(str(doc.id), faq_text=faq_text)
        db.expire_all()
        result = await db.execute(select(Document).where(Document.id == doc.id))
        doc = result.scalar_one()

    return doc


@router.put("/{document_id}/file", response_model=DocumentOut)
async def replace_pdf(
    document_id: str,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Document:
    doc = await _get_tenant_doc(db, document_id=document_id, tenant_id=current_user.tenant_id)
    if doc.source_type != "pdf":
        raise HTTPException(status_code=400, detail="Only PDF documents can replace files.")

    filename = file.filename or doc.source_name
    if not filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF uploads are supported.")

    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")
    if len(data) > MAX_PDF_BYTES:
        raise HTTPException(status_code=400, detail="PDF is too large (max 15 MB).")

    doc.source_name = _safe_name(filename)
    doc.status = "processing"
    doc.error_message = None
    doc.bytes = len(data)
    doc.chunk_count = 0
    storage.save_pdf(current_user.tenant_id, doc.id, data)
    await db.commit()
    await db.refresh(doc)

    await process_document_job(str(doc.id))
    db.expire_all()
    result = await db.execute(select(Document).where(Document.id == doc.id))
    return result.scalar_one()


@router.post("/upload", response_model=DocumentOut, status_code=status.HTTP_201_CREATED)
async def upload_pdf(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Document:
    filename = file.filename or "upload.pdf"
    if not filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF uploads are supported in Phase 2.",
        )

    data = await file.read()
    if not data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded file is empty.")
    if len(data) > MAX_PDF_BYTES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="PDF is too large (max 15 MB).",
        )

    doc = Document(
        id=uuid4(),
        tenant_id=current_user.tenant_id,
        source_type="pdf",
        source_name=_safe_name(filename),
        status="processing",
        bytes=len(data),
        chunk_count=0,
    )
    db.add(doc)
    await db.flush()

    storage.save_pdf(current_user.tenant_id, doc.id, data)
    await db.commit()
    await db.refresh(doc)

    # Process inline so uploads work without an arq worker
    await process_document_job(str(doc.id))
    db.expire_all()
    result = await db.execute(select(Document).where(Document.id == doc.id))
    return result.scalar_one()


@router.post("/faq", response_model=DocumentOut, status_code=status.HTTP_201_CREATED)
async def create_faq(
    body: FaqCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Document:
    title = body.title or body.question[:80]
    faq_text = f"Question: {body.question.strip()}\n\nAnswer: {body.answer.strip()}"

    doc = Document(
        id=uuid4(),
        tenant_id=current_user.tenant_id,
        source_type="faq",
        source_name=_safe_name(title),
        status="processing",
        bytes=len(faq_text.encode("utf-8")),
        chunk_count=0,
    )
    db.add(doc)
    await db.commit()
    await db.refresh(doc)

    await process_document_job(str(doc.id), faq_text=faq_text)
    db.expire_all()
    result = await db.execute(select(Document).where(Document.id == doc.id))
    return result.scalar_one()


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    doc = await _get_tenant_doc(db, document_id=document_id, tenant_id=current_user.tenant_id)
    storage.delete_pdf(current_user.tenant_id, doc.id)
    await db.delete(doc)
    await db.commit()
