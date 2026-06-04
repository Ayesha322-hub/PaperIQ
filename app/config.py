"""
PaperIQ — Central Configuration
All settings are loaded from the .env file.
Import `settings` anywhere in the project.
"""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # ── Application ───────────────────────────────────────────
    app_name: str = "PaperIQ"
    app_version: str = "1.0.0"
    debug: bool = True

    # ── Server ────────────────────────────────────────────────
    host: str = "0.0.0.0"
    port: int = 8000

    # ── Database ──────────────────────────────────────────────
    database_url: str = "sqlite:///./paperiq.db"

    # ── File Upload ───────────────────────────────────────────
    upload_dir: str = "uploads"
    max_file_size_mb: int = 20

    # ── CORS ──────────────────────────────────────────────────
    allowed_origins: str = "http://localhost:3000,http://localhost:5173"

    # ── NLP Models (local) ────────────────────────────────────
    summarization_model: str = "sshleifer/distilbart-cnn-12-6"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"

    # ── Crossref (optional) ───────────────────────────────────
    crossref_email: str = "your@email.com"
    crossref_enabled: bool = False

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
    }

    # ── Computed helpers ──────────────────────────────────────
    @property
    def upload_path(self) -> Path:
        path = Path(self.upload_dir)
        path.mkdir(exist_ok=True)
        return path

    @property
    def max_file_size_bytes(self) -> int:
        return self.max_file_size_mb * 1024 * 1024

    @property
    def origins_list(self) -> list[str]:
        return [o.strip() for o in self.allowed_origins.split(",")]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached Settings instance. Import and call this everywhere."""
    return Settings()


# Convenience alias — use `from app.config import settings`
settings: Settings = get_settings()
