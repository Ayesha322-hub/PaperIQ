"""
PaperIQ — Application Entry Point

Start the server:
    uvicorn app.main:app --reload

Swagger UI (test every endpoint):
    http://127.0.0.1:8000/docs

ReDoc (read-only API reference):
    http://127.0.0.1:8000/redoc
"""

import traceback
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.health import router as health_router
from app.config import settings
from app.database import create_tables
from app.utils.exceptions import (
    CitationError,
    CrossrefError,
    EmbeddingError,
    EmptyFileError,
    FileTooLargeError,
    InvalidFileTypeError,
    OCRError,
    PaperAlreadyProcessedError,
    PaperNotFoundError,
    PDFExtractionError,
    SummarizationError,
)


# ── Lifespan ──────────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"🚀 Starting {settings.app_name} v{settings.app_version}")
    create_tables()
    print("✅ Database tables ready")
    print(f"📂 Upload directory: {settings.upload_path.resolve()}")
    yield
    print(f"👋 {settings.app_name} shutting down")


# ── FastAPI app ───────────────────────────────────────────────────────────────
app = FastAPI(
    title=f"{settings.app_name} API",
    description=(
        "Offline-first research paper summarizer, citation helper, "
        "and evidence extractor for students."
    ),
    version=settings.app_version,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)


# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Exception handlers — 404 ──────────────────────────────────────────────────
@app.exception_handler(PaperNotFoundError)
async def paper_not_found_handler(request: Request, exc: PaperNotFoundError):
    return JSONResponse(status_code=404, content={"detail": str(exc)})


# ── Exception handlers — 400 ──────────────────────────────────────────────────
@app.exception_handler(InvalidFileTypeError)
async def invalid_file_type_handler(request: Request, exc: InvalidFileTypeError):
    return JSONResponse(status_code=400, content={"detail": str(exc)})


@app.exception_handler(EmptyFileError)
async def empty_file_handler(request: Request, exc: EmptyFileError):
    return JSONResponse(status_code=400, content={"detail": str(exc)})


@app.exception_handler(PaperAlreadyProcessedError)
async def already_processed_handler(request: Request, exc: PaperAlreadyProcessedError):
    return JSONResponse(status_code=400, content={"detail": str(exc)})


@app.exception_handler(CitationError)
async def citation_error_handler(request: Request, exc: CitationError):
    return JSONResponse(status_code=400, content={"detail": str(exc)})


# ── Exception handlers — 413 ──────────────────────────────────────────────────
@app.exception_handler(FileTooLargeError)
async def file_too_large_handler(request: Request, exc: FileTooLargeError):
    return JSONResponse(status_code=413, content={"detail": str(exc)})


# ── Exception handlers — 500 (NLP / pipeline errors) ─────────────────────────
@app.exception_handler(PDFExtractionError)
async def pdf_extraction_handler(request: Request, exc: PDFExtractionError):
    return JSONResponse(status_code=500, content={"detail": f"PDF extraction failed: {exc}"})


@app.exception_handler(OCRError)
async def ocr_error_handler(request: Request, exc: OCRError):
    return JSONResponse(status_code=500, content={"detail": f"OCR failed: {exc}"})


@app.exception_handler(SummarizationError)
async def summarization_error_handler(request: Request, exc: SummarizationError):
    return JSONResponse(status_code=500, content={"detail": f"Summarization failed: {exc}"})


@app.exception_handler(EmbeddingError)
async def embedding_error_handler(request: Request, exc: EmbeddingError):
    return JSONResponse(status_code=500, content={"detail": f"Embedding failed: {exc}"})


@app.exception_handler(CrossrefError)
async def crossref_error_handler(request: Request, exc: CrossrefError):
    # Crossref is optional — treat as 503 so the frontend can fall back gracefully
    return JSONResponse(
        status_code=503,
        content={"detail": f"Crossref unavailable: {exc}. Citation generated locally."},
    )


# ── Global catch-all — catches ANY unhandled exception ───────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Last-resort handler. Returns a clean JSON 500 instead of an HTML crash page.
    Logs the full traceback to the console for debugging.
    """
    traceback.print_exc()
    return JSONResponse(
        status_code=500,
        content={
            "detail": "An unexpected server error occurred. Check the server logs.",
            "type": type(exc).__name__,
        },
    )


# ── Routers ───────────────────────────────────────────────────────────────────
from app.api.papers import router as papers_router        # noqa: E402
from app.api.summaries import router as summaries_router  # noqa: E402
from app.api.citations import router as citations_router  # noqa: E402
from app.api.questions import router as questions_router  # noqa: E402

app.include_router(health_router)
app.include_router(papers_router)
app.include_router(summaries_router)
app.include_router(citations_router)
app.include_router(questions_router)


# ── Root ──────────────────────────────────────────────────────────────────────
@app.get("/", include_in_schema=False)
def root():
    return {
        "message": f"Welcome to {settings.app_name}!",
        "docs": "/docs",
        "health": "/api/v1/health",
    }
