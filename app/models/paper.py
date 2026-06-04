"""
PaperIQ — Paper Model
Represents one uploaded and processed research paper.
"""

import json
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Paper(Base):
    __tablename__ = "papers"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(512), nullable=False)

    # Extracted metadata
    title: Mapped[str | None] = mapped_column(Text, nullable=True)
    authors_json: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON array
    publication_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    journal: Mapped[str | None] = mapped_column(Text, nullable=True)
    doi: Mapped[str | None] = mapped_column(String(255), nullable=True)
    abstract: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Processing state
    total_pages: Mapped[int] = mapped_column(Integer, default=0)
    processing_status: Mapped[str] = mapped_column(
        String(20), default="uploaded"
    )  # uploaded | processing | completed | failed
    ocr_used: Mapped[bool] = mapped_column(Boolean, default=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    pages = relationship("PaperPage", back_populates="paper", cascade="all, delete-orphan")
    sections = relationship("PaperSection", back_populates="paper", cascade="all, delete-orphan")
    chunks = relationship("PaperChunk", back_populates="paper", cascade="all, delete-orphan")
    summaries = relationship("Summary", back_populates="paper", cascade="all, delete-orphan")
    citations = relationship("Citation", back_populates="paper", cascade="all, delete-orphan")

    # ── Helpers ───────────────────────────────────────────────────────────────

    @property
    def authors(self) -> list[str]:
        if not self.authors_json:
            return []
        try:
            return json.loads(self.authors_json)
        except (json.JSONDecodeError, TypeError):
            return []

    @authors.setter
    def authors(self, value: list[str]) -> None:
        self.authors_json = json.dumps(value)

    @property
    def section_names(self) -> list[str]:
        return [s.section_name for s in self.sections]

    def __repr__(self) -> str:
        return f"<Paper id={self.id} title={self.title!r} status={self.processing_status}>"
