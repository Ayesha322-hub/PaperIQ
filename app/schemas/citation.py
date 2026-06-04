"""
PaperIQ — Citation Schemas (Pydantic)
"""

from typing import Literal

from pydantic import BaseModel

CitationStyle = Literal["apa", "ieee"]


class CitationRequest(BaseModel):
    citation_style: CitationStyle = "apa"


class CitationResponse(BaseModel):
    citation_style: str
    formatted_reference: str
    verification_status: str
    requires_manual_review: bool
