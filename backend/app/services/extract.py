"""PDF text extraction with page metadata."""

from __future__ import annotations

from dataclasses import dataclass

import pdfplumber


@dataclass
class ExtractedPage:
    page_number: int
    text: str


def extract_pdf_pages(path: str) -> list[ExtractedPage]:
    pages: list[ExtractedPage] = []
    with pdfplumber.open(path) as pdf:
        for i, page in enumerate(pdf.pages, start=1):
            text = (page.extract_text() or "").strip()
            if text:
                pages.append(ExtractedPage(page_number=i, text=text))
    return pages
