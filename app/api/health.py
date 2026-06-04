"""
PaperIQ — Health Check Endpoint
GET /api/v1/health
"""

from fastapi import APIRouter

from app.config import settings

router = APIRouter(prefix="/api/v1", tags=["Health"])


@router.get("/health")
def health_check() -> dict:
    """
    Confirms the backend is running.
    The frontend should call this on startup.
    """
    return {
        "status": "ok",
        "app": settings.app_name,
        "version": settings.app_version,
    }
