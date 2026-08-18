"""Text chunking with overlap (approx token-aware via char windows)."""

from __future__ import annotations

from dataclasses import dataclass

from app.core.config import settings
from app.services.extract import ExtractedPage


@dataclass
class TextChunk:
    content: str
    metadata: dict


_HEADING_NAMES = {
    "office hours",
    "hours",
    "insurance",
    "appointments",
    "parking",
    "location",
    "location and address",
    "address",
    "services",
    "contact",
    "fees",
    "payment",
    "new patients",
    "emergency",
}


def _looks_like_heading(line: str) -> bool:
    text = (line or "").strip()
    if not text or len(text) > 48:
        return False
    if text.endswith((".", "?", "!")):
        return False
    lowered = text.lower().rstrip(":")
    if lowered in _HEADING_NAMES:
        return True
    words = lowered.split()
    return 1 <= len(words) <= 5 and text[0].isupper() and not any(ch.isdigit() for ch in text[:1])


def split_heading_sections(text: str) -> list[str]:
    """Split FAQ/PDF pages on short headings so Parking is not buried in Hours."""
    raw = (text or "").replace("\r\n", "\n").strip()
    if not raw:
        return []
    lines = raw.split("\n")
    buckets: list[list[str]] = []
    current: list[str] = []
    for line in lines:
        stripped = line.strip()
        if _looks_like_heading(stripped) and current:
            joined = "\n".join(current).strip()
            if joined:
                buckets.append(current)
            current = [stripped]
        else:
            current.append(stripped if stripped else "")
    if current:
        buckets.append(current)

    sections: list[str] = []
    pending_title = ""
    for bucket in buckets:
        joined = "\n".join(part for part in bucket if part is not None).strip()
        if not joined:
            continue
        compact = " ".join(joined.split())
        # Title-only lines merge into the next real section
        if len(compact) < 80 and not any(ch in compact for ch in ".?!"):
            pending_title = compact
            continue
        if pending_title:
            joined = f"{pending_title}\n{joined}"
            pending_title = ""
        sections.append(joined)
    if pending_title:
        sections.append(pending_title)
    return sections or [raw]


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
        sections = split_heading_sections(page.text)
        for section_idx, section in enumerate(sections):
            parts = _window_split(section, size, overlap)
            heading = section.split("\n", 1)[0][:48]
            for idx, part in enumerate(parts):
                out.append(
                    TextChunk(
                        content=part,
                        metadata={
                            "source_name": source_name,
                            "source_type": source_type,
                            "page": page.page_number,
                            "section": heading or f"page-{page.page_number}-part-{idx + 1}",
                            "section_index": section_idx,
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
    sections = split_heading_sections(text)
    out: list[TextChunk] = []
    for section_idx, section in enumerate(sections):
        parts = _window_split(section, settings.chunk_size_chars, settings.chunk_overlap_chars)
        heading = section.split("\n", 1)[0][:48]
        for i, part in enumerate(parts):
            meta = {
                **base,
                "section": heading or (f"part-{i + 1}" if len(parts) > 1 else "body"),
                "section_index": section_idx,
            }
            out.append(TextChunk(content=part, metadata=meta))
    return out
