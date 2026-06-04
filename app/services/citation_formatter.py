"""
PaperIQ — Citation Formatter Service
Generates APA and IEEE citations from extracted paper metadata.
Works fully offline — no API calls required.

All generated citations are marked as requiring manual review
because metadata extracted from PDFs can be incomplete or inaccurate.
"""

from app.utils.exceptions import CitationError


def _format_authors_apa(authors: list[str]) -> str:
    """
    Format an author list in APA style.
    e.g. ["Ali Khan", "Sara Ahmed"] → "Khan, A., & Ahmed, S."
    """
    if not authors:
        return "Unknown Author"

    formatted: list[str] = []

    for author in authors:
        parts = author.strip().split()
        if len(parts) >= 2:
            last = parts[-1]
            initials = ". ".join(p[0].upper() for p in parts[:-1]) + "."
            formatted.append(f"{last}, {initials}")
        else:
            formatted.append(author.strip())

    if len(formatted) == 1:
        return formatted[0]
    elif len(formatted) == 2:
        return f"{formatted[0]}, & {formatted[1]}"
    else:
        return ", ".join(formatted[:-1]) + f", & {formatted[-1]}"


def _format_authors_ieee(authors: list[str]) -> str:
    """
    Format an author list in IEEE style.
    e.g. ["Ali Khan", "Sara Ahmed"] → "A. Khan and S. Ahmed"
    """
    if not authors:
        return "Unknown Author"

    formatted: list[str] = []

    for author in authors:
        parts = author.strip().split()
        if len(parts) >= 2:
            last = parts[-1]
            initials = ". ".join(p[0].upper() for p in parts[:-1]) + "."
            formatted.append(f"{initials} {last}")
        else:
            formatted.append(author.strip())

    if len(formatted) == 1:
        return formatted[0]
    elif len(formatted) == 2:
        return f"{formatted[0]} and {formatted[1]}"
    else:
        return ", ".join(formatted[:-1]) + f", and {formatted[-1]}"


def format_apa(
    title: str | None,
    authors: list[str],
    year: int | None,
    journal: str | None = None,
    doi: str | None = None,
) -> str:
    """
    Generate an APA 7th edition citation string.

    Format:
        Author, A., & Author, B. (Year). Title of article.
        Journal Name. https://doi.org/xxxxx
    """
    author_str = _format_authors_apa(authors)
    year_str = f"({year})" if year else "(n.d.)"
    title_str = title.strip() if title else "Untitled"

    # APA sentence-cases the title (only first word capitalised)
    title_lower = title_str[0].upper() + title_str[1:].lower() if len(title_str) > 1 else title_str

    parts = [f"{author_str} {year_str}. {title_lower}."]

    if journal:
        parts.append(f" {journal.strip()}.")

    if doi:
        clean_doi = doi.lstrip("https://doi.org/")
        parts.append(f" https://doi.org/{clean_doi}")

    return "".join(parts)


def format_ieee(
    title: str | None,
    authors: list[str],
    year: int | None,
    journal: str | None = None,
    doi: str | None = None,
) -> str:
    """
    Generate an IEEE citation string.

    Format:
        A. Author and B. Author, "Title of article," Journal Name, Year.
        doi: 10.xxxx/xxxxx.
    """
    author_str = _format_authors_ieee(authors)
    title_str = title.strip() if title else "Untitled"
    year_str = str(year) if year else "n.d."

    citation = f'{author_str}, "{title_str},"'

    if journal:
        citation += f" {journal.strip()},"

    citation += f" {year_str}."

    if doi:
        clean_doi = doi.lstrip("https://doi.org/")
        citation += f" doi: {clean_doi}."

    return citation


def generate_citation(
    citation_style: str,
    title: str | None,
    authors: list[str],
    year: int | None,
    journal: str | None = None,
    doi: str | None = None,
) -> dict:
    """
    Generate a formatted citation and return it with metadata.

    Returns:
        {
            "citation_style": str,
            "formatted_reference": str,
            "verification_status": str,
            "requires_manual_review": bool,
        }
    """
    style = citation_style.lower().strip()

    if style == "apa":
        reference = format_apa(title, authors, year, journal, doi)
    elif style == "ieee":
        reference = format_ieee(title, authors, year, journal, doi)
    else:
        raise CitationError(
            f"Unknown citation style: '{citation_style}'. "
            "Supported styles: apa, ieee."
        )

    # Determine how complete the metadata is
    has_doi = bool(doi)
    missing_fields = [
        field for field, value in [
            ("title", title), ("authors", authors),
            ("year", year),
        ]
        if not value
    ]

    if has_doi and not missing_fields:
        verification_status = "generated_from_pdf_metadata"
    else:
        verification_status = "needs_review"

    return {
        "citation_style": style,
        "formatted_reference": reference,
        "verification_status": verification_status,
        "requires_manual_review": True,  # Always True — PDF metadata is unreliable
    }
