"""
PaperIQ — Questions API
POST /api/v1/papers/{paper_id}/ask
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.paper import Paper
from app.models.paper_chunk import PaperChunk
from app.schemas.question import EvidenceItem, QuestionRequest, QuestionResponse
from app.services import evidence_matcher
from app.utils.exceptions import PaperNotFoundError

router = APIRouter(prefix="/api/v1/papers", tags=["Questions"])


@router.post("/{paper_id}/ask", response_model=QuestionResponse)
def ask_question(
    paper_id: str,
    request: QuestionRequest,
    db: Session = Depends(get_db),
) -> QuestionResponse:
    """
    Ask a question about a paper.
    Returns the most relevant passages as evidence plus a direct answer.
    """
    paper = db.query(Paper).filter(Paper.id == paper_id).first()
    if not paper:
        raise PaperNotFoundError(f"Paper '{paper_id}' not found.")

    if paper.processing_status != "completed":
        raise HTTPException(
            status_code=400,
            detail=f"Paper is not ready. Status: '{paper.processing_status}'.",
        )

    # ── Load chunks from database ──────────────────────────────────────────────
    chunk_records = (
        db.query(PaperChunk)
        .filter(PaperChunk.paper_id == paper_id)
        .all()
    )

    if not chunk_records:
        raise HTTPException(
            status_code=400,
            detail="No chunks found. Re-process the paper.",
        )

    # Convert to dicts for evidence_matcher
    chunks = [
        {
            "chunk_text": c.chunk_text,
            "section_name": c.section_name,
            "page_number": c.page_number,
            "embedding": c.embedding,  # list[float] or None
        }
        for c in chunk_records
    ]

    # ── Find answer ────────────────────────────────────────────────────────────
    result = evidence_matcher.answer_question(
        question=request.question,
        chunks=chunks,
        top_k=3,
    )

    evidence_items = [
        EvidenceItem(
            section=e.get("section"),
            page_number=e.get("page_number"),
            text=e.get("text", ""),
            similarity_score=e.get("similarity_score", 0.0),
        )
        for e in result["evidence"]
    ]

    return QuestionResponse(
        answer=result["answer"],
        evidence=evidence_items,
    )
