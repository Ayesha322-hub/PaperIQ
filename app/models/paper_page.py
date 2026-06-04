"""
PaperIQ — PaperPage Model
Stores the raw and cleaned text of each page in a paper.
"""

from sqlalchemy import ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class PaperPage(Base):
    __tablename__ = "paper_pages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    paper_id: Mapped[str] = mapped_column(
        ForeignKey("papers.id", ondelete="CASCADE"), nullable=False, index=True
    )
    page_number: Mapped[int] = mapped_column(Integer, nullable=False)
    raw_text: Mapped[str] = mapped_column(Text, default="")
    cleaned_text: Mapped[str] = mapped_column(Text, default="")
    character_count: Mapped[int] = mapped_column(Integer, default=0)
    ocr_applied: Mapped[bool] = mapped_column(default=False)

    paper = relationship("Paper", back_populates="pages")

    def __repr__(self) -> str:
        return f"<PaperPage paper={self.paper_id} page={self.page_number}>"
