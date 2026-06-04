"""
PaperIQ — PDF Extractor Service
Extracts text page-by-page using PyMuPDF.
Falls back to OCR detection when text content is insufficient.
"""

from pathlib import Path

import fitz  # PyMuPDF

from app.utils.exceptions import PDFExtractionError

# Pages with fewer than this many characters are considered image-based
OCR_THRESHOLD_CHARS_PER_PAGE = 100


def extract_pages(file_path: Path) -> list[dict]:
    """
    Extract text from every page of the PDF.

    Returns a list of dicts:
        {
            "page_number": int,       # 1-based
            "text": str,              # raw extracted text
            "character_count": int,
        }

    Raises:
        PDFExtractionError: if the file cannot be opened or read.
    """
    if not file_path.exists():
        raise PDFExtractionError(f"PDF file not found: {file_path}")

    try:
        document = fitz.open(str(file_path))
    except Exception as exc:
        raise PDFExtractionError(f"Could not open PDF: {exc}") from exc

    extracted: list[dict] = []

    try:
        for page_index, page in enumerate(document):
            # sort=True reorders text blocks top-left → bottom-right
            # Works well for single-column papers; imperfect for multi-column
            text: str = page.get_text("text", sort=True)
            stripped = text.strip()

            extracted.append(
                {
                    "page_number": page_index + 1,
                    "text": stripped,
                    "character_count": len(stripped),
                }
            )
    finally:
        document.close()

    return extracted


def requires_ocr(pages: list[dict]) -> bool:
    """
    Return True if the PDF is likely image-based and needs OCR.
    Decision is based on the average character count per page.
    """
    if not pages:
        return True

    total_chars = sum(p["character_count"] for p in pages)
    avg_chars = total_chars / len(pages)
    return avg_chars < OCR_THRESHOLD_CHARS_PER_PAGE


def get_total_characters(pages: list[dict]) -> int:
    """Return total extracted characters across all pages."""
    return sum(p["character_count"] for p in pages)


def extract_pdf_metadata(file_path: Path) -> dict:
    """
    Extract basic metadata stored inside the PDF (title, author, subject).
    These fields are often missing or inaccurate in academic papers —
    treat them as hints, not facts.
    """
    if not file_path.exists():
        return {}

    try:
        document = fitz.open(str(file_path))
        meta = document.metadata or {}
        document.close()
        return {
            "pdf_title": meta.get("title", "").strip(),
            "pdf_author": meta.get("author", "").strip(),
            "pdf_subject": meta.get("subject", "").strip(),
            "pdf_keywords": meta.get("keywords", "").strip(),
        }
    except Exception:
        return {}
