"""
PaperIQ — Summaries API
POST /api/v1/papers/{paper_id}/summaries
"""

from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.paper import Paper
from app.models.paper_section import PaperSection
from app.models.summary import Summary, SummaryPoint
from app.schemas.summary import SummaryRequest, SummaryResponse, SummaryPointResponse
from app.services import summarizer
from app.utils.exceptions import PaperNotFoundError, SummarizationError

router = APIRouter(prefix="/api/v1/papers", tags=["Summaries"])


@router.post("/{paper_id}/summaries", response_model=SummaryResponse)
def generate_summary(
    paper_id: str,
    request: SummaryRequest,
    db: Session = Depends(get_db),
) -> SummaryResponse:
    """
    Generate a summary of the requested type for a processed paper.
    Cached: if the same type was already generated, returns the stored result.
    """
    paper = db.query(Paper).filter(Paper.id == paper_id).first()
    if not paper:
        raise PaperNotFoundError(f"Paper '{paper_id}' not found.")

    if paper.processing_status != "completed":
        raise HTTPException(
            status_code=400,
            detail=f"Paper is not ready. Current status: '{paper.processing_status}'. "
                   "Call POST /process first.",
        )

    # ── Check cache ────────────────────────────────────────────────────────────
    existing = (
        db.query(Summary)
        .filter(
            Summary.paper_id == paper_id,
            Summary.summary_type == request.summary_type,
        )
        .first()
    )

    if existing:
        points = [
            SummaryPointResponse(
                text=p.point_text,
                section=p.section_name,
                page_number=p.page_number,
                confidence_score=p.confidence_score,
                evidence=p.evidence_text,
            )
            for p in existing.points
        ]
        return SummaryResponse(
            summary_id=existing.id,
            summary_type=existing.summary_type,
            summary_points=points,
        )

    # ── Load sections ──────────────────────────────────────────────────────────
    section_records = (
        db.query(PaperSection)
        .filter(PaperSection.paper_id == paper_id)
        .order_by(PaperSection.start_page)
        .all()
    )

    sections = [
        {
            "section_name": s.section_name,
            "section_text": s.section_text,
            "start_page": s.start_page,
            "end_page": s.end_page,
            "word_count": s.word_count,
        }
        for s in section_records
    ]

    if not sections:
        raise HTTPException(
            status_code=400,
            detail="No sections found. The paper may not have been processed correctly.",
        )

    # ── Generate summary ───────────────────────────────────────────────────────
    try:
        points_data = summarizer.generate_summary(
            summary_type=request.summary_type,
            sections=sections,
            paper_title=paper.title,
        )
    except SummarizationError as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    # ── Save to database ───────────────────────────────────────────────────────
    summary_id = f"sum_{uuid4().hex[:12]}"
    summary_record = Summary(
        id=summary_id,
        paper_id=paper_id,
        summary_type=request.summary_type,
    )
    db.add(summary_record)

    response_points: list[SummaryPointResponse] = []

    for point in points_data:
        point_record = SummaryPoint(
            summary_id=summary_id,
            point_text=point["text"],
            page_number=point.get("page_number"),
            section_name=point.get("section"),
            evidence_text=point.get("evidence"),
            confidence_score=point.get("confidence_score", 0.0),
        )
        db.add(point_record)
        response_points.append(
            SummaryPointResponse(
                text=point["text"],
                section=point.get("section"),
                page_number=point.get("page_number"),
                confidence_score=point.get("confidence_score", 0.0),
                evidence=point.get("evidence"),
            )
        )

    db.commit()

    return SummaryResponse(
        summary_id=summary_id,
        summary_type=request.summary_type,
        summary_points=response_points,
    )
