"""
PaperIQ — Database Setup
Provides the SQLAlchemy engine, session factory, and Base class.
All models inherit from Base.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import settings

# ── Engine ────────────────────────────────────────────────────────────────────
# connect_args is required for SQLite to allow multi-threaded access
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False},
    echo=settings.debug,  # Logs every SQL statement in debug mode
)

# ── Session factory ───────────────────────────────────────────────────────────
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)

# ── Declarative base ──────────────────────────────────────────────────────────
class Base(DeclarativeBase):
    """All SQLAlchemy models inherit from this."""
    pass


# ── Dependency — use in FastAPI route functions ───────────────────────────────
def get_db():
    """
    Yield a database session and guarantee it is closed after the request.

    Usage in a route:
        from fastapi import Depends
        from app.database import get_db

        @router.get("/example")
        def example(db: Session = Depends(get_db)):
            ...
    """
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ── Table creation ────────────────────────────────────────────────────────────
def create_tables() -> None:
    """
    Create all tables that are registered on Base.metadata.
    Called once at application startup from main.py.
    """
    # Import all models so SQLAlchemy registers them on Base.metadata
    from app.models import paper, paper_page, paper_section, paper_chunk, summary, citation  # noqa: F401
    Base.metadata.create_all(bind=engine)
