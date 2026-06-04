"""
PaperIQ — File Validation Utilities
Validates uploaded files before saving them to disk.
"""

from fastapi import UploadFile

from app.config import settings
from app.utils.exceptions import EmptyFileError, FileTooLargeError, InvalidFileTypeError

# PDF magic bytes — every valid PDF starts with %PDF
PDF_MAGIC_BYTES = b"%PDF"

ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "application/x-pdf",
}


def validate_pdf_upload(file: UploadFile, content: bytes) -> None:
    """
    Run all validation checks on an uploaded file.
    Raises a descriptive exception on the first failure found.

    Args:
        file:    The FastAPI UploadFile object (for content-type and filename).
        content: The already-read bytes of the file.

    Raises:
        EmptyFileError:       File has no content.
        InvalidFileTypeError: MIME type or magic bytes are not PDF.
        FileTooLargeError:    File exceeds the configured size limit.
    """
    # 1. Empty file check
    if not content:
        raise EmptyFileError("The uploaded file is empty.")

    # 2. MIME type check
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise InvalidFileTypeError(
            f"Only PDF files are accepted. "
            f"Received content-type: '{file.content_type}'."
        )

    # 3. Magic bytes check (defence against renamed files)
    if not content.startswith(PDF_MAGIC_BYTES):
        raise InvalidFileTypeError(
            "The file does not appear to be a valid PDF "
            "(missing PDF header bytes)."
        )

    # 4. Size check
    if len(content) > settings.max_file_size_bytes:
        raise FileTooLargeError(
            f"The PDF exceeds the {settings.max_file_size_mb} MB size limit. "
            f"Uploaded size: {len(content) / (1024 * 1024):.1f} MB."
        )
