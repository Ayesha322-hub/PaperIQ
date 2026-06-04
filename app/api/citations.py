"""
PaperIQ — Citations API
POST /api/v1/papers/{paper_id}/citations
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.paper import Paper
from app.models.citation import Citation
from app.schemas.citation import CitationRequest, CitationResponse
from app.services import citation_formatter, crossref_service
from app.utils.exceptions import CitationError, CrossrefError, PaperNotFoundError

router = APIRouter(prefix="/api/v1/papers", tags=["Citations"])


@router.post("/{paper_id}/citations", response_model=CitationResponse)
def generate_citation(
    paper_id: str,
    request: CitationRequest,
    db: Session = Depends(get_db),
) -> CitationResponse:
    """
    Generate a formatted citation for a paper.
    Optionally verifies with Crossref if a DOI is available and
    CROSSREF_ENABLED=True in .env.
    Always returns a locally generated citation if Crossref fails.
    """
    paper = db.query(Paper).filter(Paper.id == paper_id).first()
    if not paper:
        raise PaperNotFoundError(f"Paper '{paper_id}' not found.")

    if paper.processing_status not in {"completed", "uploaded"}:
        raise HTTPException(
            status_code=400,
            detail=f"Paper status is '{paper.processing_status}'. Process the paper first.",
        )

    # ── Check cache ────────────────────────────────────────────────────────────
    existing = (
        db.query(Citation)
        .filter(
            Citation.paper_id == paper_id,
            Citation.citation_style == request.citation_style,
        )
        .first()
    )

    if existing:
        return CitationResponse(
            citation_style=existing.citation_style,
            formatted_reference=existing.formatted_reference,
            verification_status=existing.verification_status,
            requires_manual_review=True,
        )

    # ── Optional Crossref enrichment ───────────────────────────────────────────
    meta_override: dict | None = None

    if paper.doi:
        try:
            meta_override = crossref_service.lookup_by_doi(paper.doi)
        except CrossrefError as exc:
            print(f"[Citation] Crossref lookup failed: {exc}")

    # Use Crossref metadata if available, else fall back to extracted metadata
    if meta_override:
        title = meta_override.get("title") or paper.title
        authors = meta_override.get("authors") or paper.authors
        year = meta_override.get("year") or paper.publication_year
        journal = meta_override.get("journal") or paper.journal
        doi = meta_override.get("doi") or paper.doi
        verification_status = "verified_crossref"
    else:
        title = paper.title
        authors = paper.authors
        year = paper.publication_year
        journal = paper.journal
        doi = paper.doi
        verification_status = "generated_from_pdf_metadata"

    # ── Generate citation ──────────────────────────────────────────────────────
    try:
        result = citation_formatter.generate_citation(
            citation_style=request.citation_style,
            title=title,
            authors=authors,
            year=year,
            journal=journal,
            doi=doi,
        )
    except CitationError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    result["verification_status"] = verification_status

    # ── Save to database ───────────────────────────────────────────────────────
    citation_record = Citation(
        paper_id=paper_id,
        citation_style=request.citation_style,
        formatted_reference=result["formatted_reference"],
        verification_status=verification_status,
    )
    db.add(citation_record)
    db.commit()

    return CitationResponse(**result)
