"""
PaperIQ — Paper Schemas (Pydantic)
Request bodies and response shapes for all paper-related endpoints.
"""

from pydantic import BaseModel, Field


# ── Upload ────────────────────────────────────────────────────────────────────

class PaperUploadResponse(BaseModel):
    paper_id: str
    filename: str
    status: str


# ── Processing ────────────────────────────────────────────────────────────────

class ProcessResponse(BaseModel):
    paper_id: str
    status: str


class ProcessingStatusResponse(BaseModel):
    paper_id: str
    status: str
    total_pages: int = 0
    characters_extracted: int = 0
    ocr_used: bool = False
    error_message: str | None = None


# ── Metadata Update (manual edit) ────────────────────────────────────────────

class PaperMetadataUpdateRequest(BaseModel):
    title: str | None = Field(None, max_length=500)
    authors: list[str] | None = None
    year: int | None = Field(None, ge=1900, le=2100)
    journal: str | None = Field(None, max_length=300)
    doi: str | None = Field(None, max_length=200)

class PaperMetadataUpdateResponse(BaseModel):
    paper_id: str
    title: str | None
    authors: list[str]
    year: int | None
    journal: str | None
    doi: str | None
    message: str


# ── Paper Detail ──────────────────────────────────────────────────────────────

class PaperDetailResponse(BaseModel):
    paper_id: str
    filename: str
    title: str | None
    authors: list[str]
    year: int | None
    journal: str | None
    doi: str | None
    abstract: str | None
    total_pages: int
    sections: list[str]
    processing_status: str
    ocr_used: bool
