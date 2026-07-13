"""Text extraction from resume files.

This is the deterministic, pre-AI step: pull raw text out of PDF/DOCX. The
AI-structured parse (sections, skills, etc.) is layered on top in M3/M4 via the
LLM gateway — this module gives that step clean text to work with.
"""
from __future__ import annotations

import io

PARSE_SCHEMA_VERSION = "extract.v1"


def extract_text(file, file_type: str) -> str:
    """Return raw text from a file-like object. Raises on unreadable input."""
    data = file.read()
    if hasattr(file, "seek"):
        file.seek(0)

    if file_type == "pdf":
        return _extract_pdf(data)
    if file_type == "docx":
        return _extract_docx(data)
    raise ValueError(f"Unsupported file_type: {file_type}")


def _extract_pdf(data: bytes) -> str:
    from pypdf import PdfReader

    reader = PdfReader(io.BytesIO(data))
    parts = [(page.extract_text() or "") for page in reader.pages]
    return "\n".join(parts).strip()


def _extract_docx(data: bytes) -> str:
    from docx import Document

    document = Document(io.BytesIO(data))
    return "\n".join(p.text for p in document.paragraphs).strip()
