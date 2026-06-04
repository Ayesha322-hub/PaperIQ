"""
PaperIQ — OCR Service
Uses Tesseract via pytesseract to extract text from image-based PDF pages.
Only called when pdf_extractor.requires_ocr() returns True.
"""

from pathlib import Path

import fitz  # PyMuPDF — used to render pages to images
from PIL import Image
import io

from app.utils.exceptions import OCRError


def _is_tesseract_available() -> bool:
    """Check if Tesseract is installed on this machine."""
    try:
        import pytesseract
        pytesseract.get_tesseract_version()
        return True
    except Exception:
        return False


def ocr_pages(file_path: Path) -> list[dict]:
    """
    Run Tesseract OCR on every page of a PDF.
    Each page is rasterised to an image at 300 DPI first.

    Returns the same structure as pdf_extractor.extract_pages():
        [{"page_number": int, "text": str, "character_count": int}]

    Raises:
        OCRError: if Tesseract is not installed or fails.
    """
    if not _is_tesseract_available():
        raise OCRError(
            "Tesseract OCR is not installed. "
            "On Ubuntu: sudo apt install tesseract-ocr. "
            "On Windows: download from https://github.com/UB-Mannheim/tesseract/wiki"
        )

    try:
        import pytesseract
    except ImportError as exc:
        raise OCRError("pytesseract package is not installed.") from exc

    if not file_path.exists():
        raise OCRError(f"PDF file not found: {file_path}")

    try:
        document = fitz.open(str(file_path))
    except Exception as exc:
        raise OCRError(f"Could not open PDF for OCR: {exc}") from exc

    results: list[dict] = []

    try:
        for page_index, page in enumerate(document):
            # Render the page to a high-resolution image
            matrix = fitz.Matrix(300 / 72, 300 / 72)  # 300 DPI
            pixmap = page.get_pixmap(matrix=matrix)
            image_bytes = pixmap.tobytes("png")

            # Convert to PIL Image for pytesseract
            image = Image.open(io.BytesIO(image_bytes))

            try:
                text = pytesseract.image_to_string(image, lang="eng")
                stripped = text.strip()
            except Exception as ocr_exc:
                stripped = ""
                print(
                    f"[OCR] Warning: page {page_index + 1} failed — {ocr_exc}"
                )

            results.append(
                {
                    "page_number": page_index + 1,
                    "text": stripped,
                    "character_count": len(stripped),
                }
            )
    finally:
        document.close()

    return results
