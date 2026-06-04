"""
PaperIQ — Citation Model
"""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Citation(Base):
    __tablename__ = "citations"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    paper_id: Mapped[str] = mapped_column(
        ForeignKey("papers.id", ondelete="CASCADE"), nullable=False, index=True
    )
    citation_style: Mapped[str] = mapped_column(Text, nullable=False)  # apa | ieee
    formatted_reference: Mapped[str] = mapped_column(Text, nullable=False)
    verification_status: Mapped[str] = mapped_column(
        Text, default="generated_from_pdf_metadata"
    )  # verified_crossref | generated_from_pdf_metadata | needs_review
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )

    paper = relationship("Paper", back_populates="citations")

    def __repr__(self) -> str:
        return (
            f"<Citation paper={self.paper_id} style={self.citation_style}>"
        )
