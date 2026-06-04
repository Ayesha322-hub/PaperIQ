"""
PaperIQ — Papers API
Handles upload, processing, status polling, and paper detail endpoints.
"""

from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.paper import Paper
from app.models.paper_chunk import PaperChunk
from app.models.paper_page import PaperPage
from app.models.paper_section import PaperSection
from app.schemas.paper import (
    PaperDetailResponse,
    PaperMetadataUpdateRequest,
    PaperMetadataUpdateResponse,
    PaperUploadResponse,
    ProcessingStatusResponse,
    ProcessResponse,
)
from app.services import (
    chunking_service,
    embedding_service,
    ocr_service,
    pdf_extractor,
    section_detector,
    text_cleaner,
)
from app.utils.exceptions import (
    EmptyFileError,
    FileTooLargeError,
    InvalidFileTypeError,
    PaperNotFoundError,
)
from app.utils.file_validation import validate_pdf_upload
from app.config import settings

router = APIRouter(prefix="/api/v1/papers", tags=["Papers"])


# ── Helper ────────────────────────────────────────────────────────────────────

def _get_paper_or_404(paper_id: str, db: Session) -> Paper:
    paper = db.query(Paper).filter(Paper.id == paper_id).first()
    if not paper:
        raise PaperNotFoundError(f"Paper '{paper_id}' not found.")
    return paper


# ── 1. Upload ─────────────────────────────────────────────────────────────────

@router.post("/upload", response_model=PaperUploadResponse)
async def upload_paper(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> PaperUploadResponse:
    """
    Upload a research paper PDF.
    Returns a paper_id used for all subsequent requests.
    """
    content = await file.read()

    # Validate (raises on failure — caught by global handlers in main.py)
    validate_pdf_upload(file, content)

    paper_id = str(uuid4())
    file_path = settings.upload_path / f"{paper_id}.pdf"
    file_path.write_bytes(content)

    # Save to database
    paper = Paper(
        id=paper_id,
        filename=file.filename or "unnamed.pdf",
        file_path=str(file_path),
        processing_status="uploaded",
    )
    db.add(paper)
    db.commit()

    return PaperUploadResponse(
        paper_id=paper_id,
        filename=paper.filename,
        status="uploaded",
    )


# ── 2. Process ────────────────────────────────────────────────────────────────

@router.post("/{paper_id}/process", response_model=ProcessResponse)
def process_paper(
    paper_id: str,
    db: Session = Depends(get_db),
) -> ProcessResponse:
    """
    Run the full PDF processing pipeline on an uploaded paper.

    Pipeline:
        1. Extract text page by page
        2. Detect if OCR is needed
        3. Clean extracted text
        4. Detect sections
        5. Extract metadata hints
        6. Split into chunks
        7. Generate embeddings for each chunk
        8. Save everything to the database
    """
    paper = _get_paper_or_404(paper_id, db)

    if paper.processing_status == "completed":
        return ProcessResponse(paper_id=paper_id, status="completed")

    # Mark as processing
    paper.processing_status = "processing"
    db.commit()

    try:
        file_path = Path(paper.file_path)

        # ── Step 1: Extract text ───────────────────────────────────────────
        pages = pdf_extractor.extract_pages(file_path)
        ocr_needed = pdf_extractor.requires_ocr(pages)

        # ── Step 2: OCR fallback ───────────────────────────────────────────
        if ocr_needed:
            try:
                pages = ocr_service.ocr_pages(file_path)
                paper.ocr_used = True
            except Exception as ocr_exc:
                # OCR failed — continue with whatever text we have
                print(f"[Process] OCR failed for {paper_id}: {ocr_exc}")
                paper.ocr_used = False

        # ── Step 3: Clean text ─────────────────────────────────────────────
        pages = text_cleaner.clean_pages(pages)

        # ── Step 4: Save pages ─────────────────────────────────────────────
        for page_data in pages:
            page_record = PaperPage(
                paper_id=paper_id,
                page_number=page_data["page_number"],
                raw_text=page_data.get("text", ""),
                cleaned_text=page_data.get("cleaned_text", ""),
                character_count=page_data.get("character_count", 0),
                ocr_applied=paper.ocr_used,
            )
            db.add(page_record)

        # ── Step 5: Detect sections ────────────────────────────────────────
        sections = section_detector.detect_sections_from_pages(pages)
        for sec in sections:
            section_record = PaperSection(
                paper_id=paper_id,
                section_name=sec["section_name"],
                start_page=sec["start_page"],
                end_page=sec["end_page"],
                section_text=sec["section_text"],
                word_count=sec["word_count"],
            )
            db.add(section_record)

        # ── Step 6: Extract metadata hints ────────────────────────────────
        meta = section_detector.extract_metadata_hints(pages)
        abstract = section_detector.extract_abstract(pages)
        pdf_meta = pdf_extractor.extract_pdf_metadata(file_path)

        # Prefer extracted hints over PDF metadata (more reliable)
        paper.title = meta.get("title") or pdf_meta.get("pdf_title") or None
        paper.publication_year = meta.get("year")
        paper.doi = meta.get("doi")
        paper.abstract = abstract

        # Authors from PDF metadata (rough)
        if pdf_meta.get("pdf_author"):
            raw_authors = [
                a.strip()
                for a in pdf_meta["pdf_author"].replace(";", ",").split(",")
                if a.strip()
            ]
            paper.authors = raw_authors

        paper.total_pages = len(pages)

        # ── Step 7: Chunk sections ─────────────────────────────────────────
        chunks = chunking_service.chunk_sections(sections)

        # ── Step 8: Embed and save chunks ──────────────────────────────────
        chunk_texts = [c["chunk_text"] for c in chunks]
        try:
            embeddings = embedding_service.embed_batch(chunk_texts)
        except Exception as emb_exc:
            print(f"[Process] Embedding failed for {paper_id}: {emb_exc}")
            embeddings = [None] * len(chunks)

        for idx, (chunk_data, embedding) in enumerate(zip(chunks, embeddings)):
            chunk_record = PaperChunk(
                paper_id=paper_id,
                section_name=chunk_data["section_name"],
                page_number=chunk_data["page_number"],
                chunk_index=chunk_data["chunk_index"],
                chunk_text=chunk_data["chunk_text"],
                word_count=chunk_data["word_count"],
            )
            if embedding:
                chunk_record.embedding = embedding
            db.add(chunk_record)

        # ── Done ───────────────────────────────────────────────────────────
        paper.processing_status = "completed"
        db.commit()

    except Exception as exc:
        paper.processing_status = "failed"
        paper.error_message = str(exc)
        db.commit()
        raise HTTPException(
            status_code=500,
            detail=f"Processing failed: {exc}",
        )

    return ProcessResponse(paper_id=paper_id, status="processing")


# ── 3. Status ─────────────────────────────────────────────────────────────────

@router.get("/{paper_id}/status", response_model=ProcessingStatusResponse)
def get_status(
    paper_id: str,
    db: Session = Depends(get_db),
) -> ProcessingStatusResponse:
    """Check the processing status of a paper."""
    paper = _get_paper_or_404(paper_id, db)

    total_chars = (
        db.query(PaperPage)
        .filter(PaperPage.paper_id == paper_id)
        .with_entities(PaperPage.character_count)
        .all()
    )
    chars_extracted = sum(row[0] for row in total_chars)

    return ProcessingStatusResponse(
        paper_id=paper_id,
        status=paper.processing_status,
        total_pages=paper.total_pages,
        characters_extracted=chars_extracted,
        ocr_used=paper.ocr_used,
        error_message=paper.error_message,
    )


# ── 4. Paper Detail ───────────────────────────────────────────────────────────

@router.get("/{paper_id}", response_model=PaperDetailResponse)
def get_paper(
    paper_id: str,
    db: Session = Depends(get_db),
) -> PaperDetailResponse:
    """Get full details and metadata for a processed paper."""
    paper = _get_paper_or_404(paper_id, db)

    sections = (
        db.query(PaperSection)
        .filter(PaperSection.paper_id == paper_id)
        .order_by(PaperSection.start_page)
        .all()
    )

    return PaperDetailResponse(
        paper_id=paper.id,
        filename=paper.filename,
        title=paper.title,
        authors=paper.authors,
        year=paper.publication_year,
        journal=paper.journal,
        doi=paper.doi,
        abstract=paper.abstract,
        total_pages=paper.total_pages,
        sections=[s.section_name for s in sections],
        processing_status=paper.processing_status,
        ocr_used=paper.ocr_used,
    )


# ── 5. Update Metadata (manual edit) ─────────────────────────────────────────

@router.patch("/{paper_id}/metadata", response_model=PaperMetadataUpdateResponse)
def update_metadata(
    paper_id: str,
    request: PaperMetadataUpdateRequest,
    db: Session = Depends(get_db),
) -> PaperMetadataUpdateResponse:
    """
    Manually correct extracted metadata before generating a citation.

    Only fields included in the request body are updated.
    Omitted fields keep their current values.
    After editing, delete any cached citations so they are regenerated
    with the corrected metadata.
    """
    paper = _get_paper_or_404(paper_id, db)

    updated_fields: list[str] = []

    if request.title is not None:
        paper.title = request.title.strip()
        updated_fields.append("title")

    if request.authors is not None:
        paper.authors = [a.strip() for a in request.authors if a.strip()]
        updated_fields.append("authors")

    if request.year is not None:
        paper.publication_year = request.year
        updated_fields.append("year")

    if request.journal is not None:
        paper.journal = request.journal.strip()
        updated_fields.append("journal")

    if request.doi is not None:
        paper.doi = request.doi.strip() or None
        updated_fields.append("doi")

    if updated_fields:
        # Invalidate cached citations — they used the old metadata
        from app.models.citation import Citation
        db.query(Citation).filter(Citation.paper_id == paper_id).delete()

    db.commit()
    db.refresh(paper)

    fields_str = ", ".join(updated_fields) if updated_fields else "none"

    return PaperMetadataUpdateResponse(
        paper_id=paper.id,
        title=paper.title,
        authors=paper.authors,
        year=paper.publication_year,
        journal=paper.journal,
        doi=paper.doi,
        message=f"Updated fields: {fields_str}. Cached citations cleared.",
    )
