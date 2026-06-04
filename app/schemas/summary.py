"""
PaperIQ — Summary Schemas (Pydantic)
"""

from typing import Literal

from pydantic import BaseModel, Field

SummaryType = Literal[
    "short", "detailed", "section_wise", "key_findings", "beginner_friendly"
]


class SummaryRequest(BaseModel):
    summary_type: SummaryType = Field(
        default="short",
        description="Type of summary to generate.",
    )


class SummaryPointResponse(BaseModel):
    text: str
    section: str | None
    page_number: int | None
    confidence_score: float
    evidence: str | None


class SummaryResponse(BaseModel):
    summary_id: str
    summary_type: str
    summary_points: list[SummaryPointResponse]
