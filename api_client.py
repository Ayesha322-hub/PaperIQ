"""
PaperIQ — API Client
All HTTP calls to the backend go through this module.
Never call requests directly from the UI pages.
"""

import time
import requests

BASE_URL = "https://AyeshaAkbar00-paperiq-backend.hf.space/api/v1"
TIMEOUT = 300  # seconds


class APIError(Exception):
    """Raised when the backend returns a non-2xx response."""
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail
        super().__init__(detail)


def _handle(response: requests.Response) -> dict:
    """Parse response, raise APIError on failure."""
    if response.ok:
        return response.json()
    try:
        detail = response.json().get("detail", response.text)
    except Exception:
        detail = response.text
    raise APIError(response.status_code, str(detail))


# ── Health ────────────────────────────────────────────────────────────────────

def health_check() -> dict:
    try:
        r = requests.get(f"{BASE_URL}/health", timeout=5)
        return _handle(r)
    except requests.ConnectionError:
        raise APIError(503, "Cannot connect to backend. Is the server running on port 8000?")


# ── Upload ────────────────────────────────────────────────────────────────────

def upload_paper(file_bytes: bytes, filename: str) -> dict:
    """Upload a PDF. Returns {paper_id, filename, status}."""
    r = requests.post(
        f"{BASE_URL}/papers/upload",
        files={"file": (filename, file_bytes, "application/pdf")},
        timeout=TIMEOUT,
    )
    return _handle(r)


# ── Process ───────────────────────────────────────────────────────────────────

def process_paper(paper_id: str) -> dict:
    r = requests.post(f"{BASE_URL}/papers/{paper_id}/process", timeout=TIMEOUT)
    return _handle(r)


# ── Status ────────────────────────────────────────────────────────────────────

def get_status(paper_id: str) -> dict:
    r = requests.get(f"{BASE_URL}/papers/{paper_id}/status", timeout=TIMEOUT)
    return _handle(r)


def wait_for_completion(paper_id: str, poll_interval: float = 2.0, max_wait: int = 300) -> dict:
    """
    Poll /status every poll_interval seconds until completed or failed.
    Returns the final status dict.
    Raises APIError if failed or timeout exceeded.
    """
    elapsed = 0
    while elapsed < max_wait:
        status = get_status(paper_id)
        if status["status"] == "completed":
            return status
        if status["status"] == "failed":
            raise APIError(500, status.get("error_message") or "Processing failed.")
        time.sleep(poll_interval)
        elapsed += poll_interval
    raise APIError(504, "Processing timed out after 5 minutes.")


# ── Paper detail ──────────────────────────────────────────────────────────────

def get_paper(paper_id: str) -> dict:
    r = requests.get(f"{BASE_URL}/papers/{paper_id}", timeout=TIMEOUT)
    return _handle(r)


# ── Metadata update ───────────────────────────────────────────────────────────

def update_metadata(paper_id: str, payload: dict) -> dict:
    r = requests.patch(
        f"{BASE_URL}/papers/{paper_id}/metadata",
        json=payload,
        timeout=TIMEOUT,
    )
    return _handle(r)


# ── Summary ───────────────────────────────────────────────────────────────────

def generate_summary(paper_id: str, summary_type: str) -> dict:
    r = requests.post(
        f"{BASE_URL}/papers/{paper_id}/summaries",
        json={"summary_type": summary_type},
        timeout=300,  # model inference can be slow first time
    )
    return _handle(r)


# ── Citation ──────────────────────────────────────────────────────────────────

def generate_citation(paper_id: str, citation_style: str) -> dict:
    r = requests.post(
        f"{BASE_URL}/papers/{paper_id}/citations",
        json={"citation_style": citation_style},
        timeout=TIMEOUT,
    )
    return _handle(r)


# ── Q&A ───────────────────────────────────────────────────────────────────────

def ask_question(paper_id: str, question: str) -> dict:
    r = requests.post(
        f"{BASE_URL}/papers/{paper_id}/ask",
        json={"question": question},
        timeout=120,
    )
    return _handle(r)
