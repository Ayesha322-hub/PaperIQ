"""
PaperIQ — Custom Exceptions
Centralised exceptions make error handling consistent across the project.
"""


class PaperIQBaseError(Exception):
    """Base class for all PaperIQ exceptions."""
    pass


# ── File / Upload ─────────────────────────────────────────────────────────────

class InvalidFileTypeError(PaperIQBaseError):
    """Raised when the uploaded file is not a PDF."""
    pass


class FileTooLargeError(PaperIQBaseError):
    """Raised when the uploaded file exceeds the size limit."""
    pass


class EmptyFileError(PaperIQBaseError):
    """Raised when the uploaded file has no content."""
    pass


# ── PDF Extraction ────────────────────────────────────────────────────────────

class PDFExtractionError(PaperIQBaseError):
    """Raised when PyMuPDF fails to open or read the PDF."""
    pass


class OCRError(PaperIQBaseError):
    """Raised when Tesseract OCR fails."""
    pass


# ── Database / Paper ──────────────────────────────────────────────────────────

class PaperNotFoundError(PaperIQBaseError):
    """Raised when a paper_id does not exist in the database."""
    pass


class PaperAlreadyProcessedError(PaperIQBaseError):
    """Raised when trying to re-process a paper that is already completed."""
    pass


# ── NLP / Summarization ───────────────────────────────────────────────────────

class SummarizationError(PaperIQBaseError):
    """Raised when the summarization model fails."""
    pass


class EmbeddingError(PaperIQBaseError):
    """Raised when the embedding model fails."""
    pass


# ── Citation ──────────────────────────────────────────────────────────────────

class CitationError(PaperIQBaseError):
    """Raised when citation generation fails."""
    pass


class CrossrefError(PaperIQBaseError):
    """Raised when the Crossref API request fails."""
    pass
