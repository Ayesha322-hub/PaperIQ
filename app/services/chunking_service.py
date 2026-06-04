"""
PaperIQ — Chunking Service
Splits section text into overlapping chunks for summarisation and embedding.

Why chunking matters:
- Summarisation models have a token limit (~1024 tokens for distilbart).
- Embedding models work better on shorter focused passages.
- Overlapping chunks prevent context loss at boundaries.
"""

import re

# ── Configuration ─────────────────────────────────────────────────────────────
DEFAULT_CHUNK_WORDS = 200      # Target words per chunk
DEFAULT_OVERLAP_WORDS = 30     # Words of overlap between consecutive chunks
MIN_CHUNK_WORDS = 30           # Chunks shorter than this are discarded


def _split_into_sentences(text: str) -> list[str]:
    """
    Split text into sentences using a simple regex.
    Good enough for academic paper text.
    """
    # Split on ". ", "! ", "? " followed by a capital letter
    sentences = re.split(r"(?<=[.!?])\s+(?=[A-Z])", text)
    return [s.strip() for s in sentences if s.strip()]


def chunk_text(
    text: str,
    section_name: str,
    page_number: int,
    chunk_words: int = DEFAULT_CHUNK_WORDS,
    overlap_words: int = DEFAULT_OVERLAP_WORDS,
) -> list[dict]:
    """
    Split a section's text into overlapping word-based chunks.

    Returns a list of chunk dicts:
        {
            "section_name": str,
            "page_number": int,
            "chunk_index": int,
            "chunk_text": str,
            "word_count": int,
        }
    """
    if not text or not text.strip():
        return []

    words = text.split()

    if len(words) <= chunk_words:
        # Short enough — return as a single chunk
        return [
            {
                "section_name": section_name,
                "page_number": page_number,
                "chunk_index": 0,
                "chunk_text": text.strip(),
                "word_count": len(words),
            }
        ]

    chunks: list[dict] = []
    start = 0
    chunk_index = 0

    while start < len(words):
        end = min(start + chunk_words, len(words))
        chunk_words_list = words[start:end]

        if len(chunk_words_list) >= MIN_CHUNK_WORDS:
            chunks.append(
                {
                    "section_name": section_name,
                    "page_number": page_number,
                    "chunk_index": chunk_index,
                    "chunk_text": " ".join(chunk_words_list),
                    "word_count": len(chunk_words_list),
                }
            )
            chunk_index += 1

        # Move forward by (chunk_words - overlap) so chunks overlap
        step = max(1, chunk_words - overlap_words)
        start += step

    return chunks


def chunk_sections(sections: list[dict]) -> list[dict]:
    """
    Chunk all sections and return a flat list of all chunks.
    """
    all_chunks: list[dict] = []

    for section in sections:
        section_chunks = chunk_text(
            text=section["section_text"],
            section_name=section["section_name"],
            page_number=section["start_page"],
        )
        all_chunks.extend(section_chunks)

    return all_chunks
