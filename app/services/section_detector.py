"""
PaperIQ — Section Detector Service
Identifies standard research paper sections from cleaned text.

Strategy:
1. Look for lines that match known section heading patterns.
2. Assign each page range to a section.
3. Return a list of detected sections with their text.

This is rule-based — good enough for standard academic papers.
"""

import re

# ── Known section headings (case-insensitive) ─────────────────────────────────
# Order matters — more specific patterns should come before broader ones.
KNOWN_SECTIONS: list[str] = [
    "Abstract",
    "Keywords",
    "Introduction",
    "Related Work",
    "Literature Review",
    "Background",
    "Methodology",
    "Methods",
    "Materials and Methods",
    "Proposed Method",
    "System Design",
    "Architecture",
    "Experimental Setup",
    "Experiments",
    "Evaluation",
    "Results",
    "Results and Discussion",
    "Discussion",
    "Analysis",
    "Findings",
    "Conclusion",
    "Conclusions",
    "Conclusion and Future Work",
    "Future Work",
    "Limitations",
    "Acknowledgements",
    "Acknowledgments",
    "References",
    "Bibliography",
    "Appendix",
]

# Build a single compiled regex from known section names
_SECTION_PATTERN = re.compile(
    r"(?im)^\s*(?:\d+[\.\)]?\s*)?("
    + "|".join(re.escape(s) for s in KNOWN_SECTIONS)
    + r")\s*$"
)


def _normalise_section_name(raw: str) -> str:
    """Strip numbering and normalise spacing from a detected heading."""
    cleaned = re.sub(r"^\d+[\.\)]\s*", "", raw.strip())
    return cleaned.strip().title()


def detect_sections_from_pages(pages: list[dict]) -> list[dict]:
    """
    Detect sections by scanning each page for heading patterns.

    Returns a list of section dicts:
        {
            "section_name": str,
            "start_page": int,
            "end_page": int,
            "section_text": str,
            "word_count": int,
        }
    """
    if not pages:
        return []

    # ── Step 1: Find which page each section starts on ────────────────────────
    section_hits: list[tuple[str, int]] = []  # (section_name, page_number)

    for page in pages:
        page_num = page["page_number"]
        text = page.get("cleaned_text") or page.get("text", "")

        for match in _SECTION_PATTERN.finditer(text):
            name = _normalise_section_name(match.group(1))
            # Avoid duplicate consecutive detections
            if section_hits and section_hits[-1][0] == name:
                continue
            section_hits.append((name, page_num))

    if not section_hits:
        # No sections detected — return the whole paper as one section
        full_text = "\n\n".join(
            p.get("cleaned_text") or p.get("text", "") for p in pages
        )
        return [
            {
                "section_name": "Full Text",
                "start_page": pages[0]["page_number"],
                "end_page": pages[-1]["page_number"],
                "section_text": full_text.strip(),
                "word_count": len(full_text.split()),
            }
        ]

    # ── Step 2: Build a page lookup ───────────────────────────────────────────
    page_text: dict[int, str] = {
        p["page_number"]: (p.get("cleaned_text") or p.get("text", ""))
        for p in pages
    }
    last_page = pages[-1]["page_number"]

    # ── Step 3: Assign page ranges and collect text ───────────────────────────
    sections: list[dict] = []

    for idx, (section_name, start_page) in enumerate(section_hits):
        # End page is one before the next section starts (or last page)
        if idx + 1 < len(section_hits):
            next_start = section_hits[idx + 1][1]
            end_page = max(start_page, next_start - 1)
        else:
            end_page = last_page

        # Gather text for the page range
        section_text_parts = []
        for pnum in range(start_page, end_page + 1):
            part = page_text.get(pnum, "")
            if part:
                section_text_parts.append(part)

        section_text = "\n\n".join(section_text_parts).strip()
        word_count = len(section_text.split())

        sections.append(
            {
                "section_name": section_name,
                "start_page": start_page,
                "end_page": end_page,
                "section_text": section_text,
                "word_count": word_count,
            }
        )

    return sections


def extract_abstract(pages: list[dict]) -> str | None:
    """
    Try to extract the abstract text specifically.
    Looks in the first 3 pages.
    """
    abstract_pattern = re.compile(
        r"(?is)abstract[:\s\-]*(.+?)(?=\n\n(?:keywords|introduction|\d\.)|\Z)",
        re.DOTALL,
    )

    for page in pages[:3]:
        text = page.get("cleaned_text") or page.get("text", "")
        match = abstract_pattern.search(text)
        if match:
            return match.group(1).strip()[:2000]  # cap at 2000 chars

    return None


def extract_metadata_hints(pages: list[dict]) -> dict:
    """
    Try to extract title, authors, year, and DOI from the first 2 pages.
    These are rough heuristics — not guaranteed to be accurate.
    """
    hints: dict = {
        "title": None,
        "authors": [],
        "year": None,
        "doi": None,
        "journal": None,
    }

    first_pages_text = ""
    for page in pages[:2]:
        first_pages_text += page.get("cleaned_text") or page.get("text", "")
        first_pages_text += "\n"

    # DOI — most reliable metadata field
    doi_match = re.search(
        r"(?i)(?:doi|https?://doi\.org/)[\s:]*(10\.\d{4,}/\S+)",
        first_pages_text,
    )
    if doi_match:
        hints["doi"] = doi_match.group(1).rstrip(".,)")

    # Year — 4-digit year between 1990 and 2030
    year_match = re.search(r"\b(19[9]\d|20[0-2]\d)\b", first_pages_text)
    if year_match:
        hints["year"] = int(year_match.group(1))

    # Title — first non-empty line of the paper (rough heuristic)
    lines = [line.strip() for line in first_pages_text.split("\n") if line.strip()]
    if lines:
        # Skip very short lines (page numbers, journal names)
        for line in lines[:5]:
            if len(line) > 20:
                hints["title"] = line
                break

    return hints
