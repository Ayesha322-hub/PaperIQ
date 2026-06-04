"""
PaperIQ — Question & Answer Schemas (Pydantic)
"""

from pydantic import BaseModel, Field


class QuestionRequest(BaseModel):
    question: str = Field(..., min_length=3, max_length=500)


class EvidenceItem(BaseModel):
    section: str | None
    page_number: int | None
    text: str
    similarity_score: float


class QuestionResponse(BaseModel):
    answer: str
    evidence: list[EvidenceItem]
