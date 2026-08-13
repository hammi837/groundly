"""Text chunking with overlap (approx token-aware via char windows)."""

from __future__ import annotations

from dataclasses import dataclass

from app.core.config import settings
from app.services.extract import ExtractedPage


@dataclass
class TextChunk:
    content: str
    metadata: dict


def _window_split(text: str, size: int, overlap: int) -> list[str]:
    text = " ".join(text.split())
    if not text:
        return []
    if len(text) <= size:
        return [text]
    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = min(len(text), start + size)
        piece = text[start:end].strip()
        if piece:
            chunks.append(piece)
        if end >= len(text):
            break
        start = max(0, end - overlap)
    return chunks


def chunk_pages(
    pages: list[ExtractedPage],
    *,
    source_name: str,
    source_type: str,
) -> list[TextChunk]:
    size = settings.chunk_size_chars
    overlap = settings.chunk_overlap_chars
    out: list[TextChunk] = []
    for page in pages:
        parts = _window_split(page.text, size, overlap)
        for idx, part in enumerate(parts):
            out.append(
                TextChunk(
                    content=part,
                    metadata={
                        "source_name": source_name,
                        "source_type": source_type,
                        "page": page.page_number,
                        "section": f"page-{page.page_number}-part-{idx + 1}",
                    },
                )
            )
    return out


def chunk_plain_text(
    text: str,
    *,
    source_name: str,
    source_type: str,
    extra_metadata: dict | None = None,
) -> list[TextChunk]:
    base = {
        "source_name": source_name,
        "source_type": source_type,
        "page": 1,
        "section": "body",
    }
    if extra_metadata:
        base.update(extra_metadata)
    parts = _window_split(text, settings.chunk_size_chars, settings.chunk_overlap_chars)
    return [
        TextChunk(
            content=part,
            metadata={**base, "section": f"part-{i + 1}" if len(parts) > 1 else "body"},
        )
        for i, part in enumerate(parts)
    ]
