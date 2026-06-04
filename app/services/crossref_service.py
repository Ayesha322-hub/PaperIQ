"""
PaperIQ — Crossref Service (Optional)
Verifies and enriches citation metadata using the free Crossref REST API.

This service is optional. The system works without it.
Set CROSSREF_ENABLED=True in .env to activate.
Crossref does not require signup. A polite email in the header is recommended.
"""

import requests

from app.config import settings
from app.utils.exceptions import CrossrefError

CROSSREF_BASE_URL = "https://api.crossref.org/works"
REQUEST_TIMEOUT_SECONDS = 10


def _polite_headers() -> dict[str, str]:
    """
    Crossref recommends including your email (polite pool = faster responses).
    https://www.crossref.org/documentation/retrieve-metadata/rest-api/
    """
    return {
        "User-Agent": f"PaperIQ/1.0 (mailto:{settings.crossref_email})",
    }


def lookup_by_doi(doi: str) -> dict | None:
    """
    Look up a paper by DOI using the Crossref API.
    Returns a dict of enriched metadata, or None if not found.

    Raises:
        CrossrefError: if the request fails.
    """
    if not settings.crossref_enabled:
        return None

    clean_doi = doi.strip().lstrip("https://doi.org/")

    try:
        response = requests.get(
            f"{CROSSREF_BASE_URL}/{clean_doi}",
            headers=_polite_headers(),
            timeout=REQUEST_TIMEOUT_SECONDS,
        )

        if response.status_code == 404:
            return None

        if response.status_code != 200:
            raise CrossrefError(
                f"Crossref returned status {response.status_code} for DOI: {doi}"
            )

        data = response.json()
        work = data.get("message", {})
        return _parse_crossref_work(work)

    except CrossrefError:
        raise
    except requests.Timeout:
        raise CrossrefError("Crossref request timed out.")
    except requests.ConnectionError:
        raise CrossrefError("Could not connect to Crossref (no internet?).")
    except Exception as exc:
        raise CrossrefError(f"Crossref lookup failed: {exc}") from exc


def _parse_crossref_work(work: dict) -> dict:
    """Parse a Crossref work object into our metadata format."""
    # Title
    titles = work.get("title", [])
    title = titles[0] if titles else None

    # Authors
    author_list = work.get("author", [])
    authors = []
    for a in author_list:
        given = a.get("given", "")
        family = a.get("family", "")
        if given and family:
            authors.append(f"{given} {family}")
        elif family:
            authors.append(family)

    # Year
    year = None
    date_parts = work.get("published", {}).get("date-parts", [[]])
    if date_parts and date_parts[0]:
        year = date_parts[0][0]

    # Journal
    container = work.get("container-title", [])
    journal = container[0] if container else None

    # DOI
    doi = work.get("DOI")

    return {
        "title": title,
        "authors": authors,
        "year": year,
        "journal": journal,
        "doi": doi,
        "verification_status": "verified_crossref",
    }


def search_by_title(title: str, author: str | None = None) -> dict | None:
    """
    Search Crossref by title (and optionally author).
    Less reliable than DOI lookup — use as a fallback only.
    """
    if not settings.crossref_enabled:
        return None

    params: dict = {
        "query.title": title,
        "rows": 1,
        "select": "DOI,title,author,published,container-title",
    }

    if author:
        params["query.author"] = author

    try:
        response = requests.get(
            CROSSREF_BASE_URL,
            params=params,
            headers=_polite_headers(),
            timeout=REQUEST_TIMEOUT_SECONDS,
        )

        if response.status_code != 200:
            return None

        data = response.json()
        items = data.get("message", {}).get("items", [])

        if not items:
            return None

        return _parse_crossref_work(items[0])

    except Exception:
        return None
