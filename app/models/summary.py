"""
PaperIQ — Summary and SummaryPoint Models
"""

from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Summary(Base):
    __tablename__ = "summaries"

    id: Mapped[str] = mapped_column(Text, primary_key=True)
    paper_id: Mapped[str] = mapped_column(
        ForeignKey("papers.id", ondelete="CASCADE"), nullable=False, index=True
    )
    summary_type: Mapped[str] = mapped_column(
        Text, nullable=False
    )  # short | detailed | section_wise | key_findings | beginner_friendly
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )

    paper = relationship("Paper", back_populates="summaries")
    points = relationship(
        "SummaryPoint", back_populates="summary", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Summary id={self.id} type={self.summary_type}>"


class SummaryPoint(Base):
    __tablename__ = "summary_points"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    summary_id: Mapped[str] = mapped_column(
        ForeignKey("summaries.id", ondelete="CASCADE"), nullable=False, index=True
    )
    point_text: Mapped[str] = mapped_column(Text, nullable=False)
    page_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    section_name: Mapped[str | None] = mapped_column(Text, nullable=True)
    evidence_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    confidence_score: Mapped[float] = mapped_column(Float, default=0.0)

    summary = relationship("Summary", back_populates="points")

    def __repr__(self) -> str:
        return f"<SummaryPoint summary={self.summary_id} page={self.page_number}>"
