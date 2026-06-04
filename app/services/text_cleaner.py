"""
PaperIQ — Text Cleaner Service
Normalises raw extracted text before NLP processing.

Academic PDFs often have:
- Hyphenated line breaks (e.g. "meth-\nods")
- Excessive whitespace and blank lines
- Page headers/footers repeated on every page
- Ligature characters (ﬁ, ﬂ, ﬀ) not in standard ASCII
"""

import re
import unicodedata


# ── Ligature map ──────────────────────────────────────────────────────────────
LIGATURE_MAP: dict[str, str] = {
    "\ufb00": "ff",
    "\ufb01": "fi",
    "\ufb02": "fl",
    "\ufb03": "ffi",
    "\ufb04": "ffl",
    "\ufb05": "st",
    "\ufb06": "st",
}


def _replace_ligatures(text: str) -> str:
    for ligature, replacement in LIGATURE_MAP.items():
        text = text.replace(ligature, replacement)
    return text


def _fix_hyphenated_line_breaks(text: str) -> str:
    """
    Join words broken across lines with a hyphen.
    e.g. "meth-\nods" → "methods"
    """
    return re.sub(r"(\w)-\n(\w)", r"\1\2", text)


def _normalise_whitespace(text: str) -> str:
    """
    Collapse multiple spaces and blank lines.
    Preserve single paragraph breaks (double newline).
    """
    # Collapse 3+ newlines into 2
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Collapse multiple spaces into one
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


def _remove_page_numbers(text: str) -> str:
    """Remove standalone page numbers (lines that are just a number)."""
    return re.sub(r"(?m)^\s*\d{1,4}\s*$", "", text)


def _normalise_unicode(text: str) -> str:
    """
    Normalise unicode to NFC form.
    Converts composed characters to their canonical form.
    """
    return unicodedata.normalize("NFC", text)


def clean_text(raw_text: str) -> str:
    """
    Apply the full cleaning pipeline to raw extracted text.
    Returns cleaned text ready for section detection and NLP.
    """
    text = raw_text

    # 1. Replace ligatures (ﬁ → fi)
    text = _replace_ligatures(text)

    # 2. Normalise unicode
    text = _normalise_unicode(text)

    # 3. Fix hyphenated line breaks
    text = _fix_hyphenated_line_breaks(text)

    # 4. Remove lone page numbers
    text = _remove_page_numbers(text)

    # 5. Normalise whitespace
    text = _normalise_whitespace(text)

    return text


def clean_pages(pages: list[dict]) -> list[dict]:
    """
    Apply clean_text to every page in the extracted pages list.
    Adds a 'cleaned_text' key to each page dict.
    """
    for page in pages:
        page["cleaned_text"] = clean_text(page.get("text", ""))
    return pages


def get_full_text(pages: list[dict], use_cleaned: bool = True) -> str:
    """
    Concatenate all pages into one string.
    Use cleaned text by default; fall back to raw text.
    """
    key = "cleaned_text" if use_cleaned else "text"
    parts: list[str] = []
    for page in pages:
        text = page.get(key) or page.get("text", "")
        if text:
            parts.append(f"[Page {page['page_number']}]\n{text}")
    return "\n\n".join(parts)
