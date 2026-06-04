"""
PaperIQ — PaperSection Model
Represents a detected section (Abstract, Introduction, etc.) in a paper.
"""

from sqlalchemy import ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class PaperSection(Base):
    __tablename__ = "paper_sections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    paper_id: Mapped[str] = mapped_column(
        ForeignKey("papers.id", ondelete="CASCADE"), nullable=False, index=True
    )
    section_name: Mapped[str] = mapped_column(Text, nullable=False)
    start_page: Mapped[int] = mapped_column(Integer, nullable=False)
    end_page: Mapped[int] = mapped_column(Integer, nullable=False)
    section_text: Mapped[str] = mapped_column(Text, default="")
    word_count: Mapped[int] = mapped_column(Integer, default=0)

    paper = relationship("Paper", back_populates="sections")

    def __repr__(self) -> str:
        return (
            f"<PaperSection paper={self.paper_id} "
            f"section={self.section_name!r} pages={self.start_page}-{self.end_page}>"
        )
