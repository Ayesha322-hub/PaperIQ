"""
PaperIQ — PaperChunk Model
Stores text chunks used for semantic search and summarisation.
Embeddings are stored as JSON arrays.
"""

import json

from sqlalchemy import ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class PaperChunk(Base):
    __tablename__ = "paper_chunks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    paper_id: Mapped[str] = mapped_column(
        ForeignKey("papers.id", ondelete="CASCADE"), nullable=False, index=True
    )
    section_name: Mapped[str] = mapped_column(Text, default="Unknown")
    page_number: Mapped[int] = mapped_column(Integer, nullable=False)
    chunk_index: Mapped[int] = mapped_column(Integer, default=0)
    chunk_text: Mapped[str] = mapped_column(Text, nullable=False)
    embedding_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    word_count: Mapped[int] = mapped_column(Integer, default=0)

    paper = relationship("Paper", back_populates="chunks")

    @property
    def embedding(self) -> list[float] | None:
        if not self.embedding_json:
            return None
        try:
            return json.loads(self.embedding_json)
        except (json.JSONDecodeError, TypeError):
            return None

    @embedding.setter
    def embedding(self, value: list[float]) -> None:
        self.embedding_json = json.dumps(value)

    def __repr__(self) -> str:
        return (
            f"<PaperChunk paper={self.paper_id} "
            f"section={self.section_name!r} idx={self.chunk_index}>"
        )
