# PaperIQ Backend

Offline-first research paper summarizer, citation helper, and evidence extractor for students.

---

## Tech Stack

| Purpose | Technology |
|---|---|
| Framework | FastAPI |
| Database | SQLite + SQLAlchemy |
| PDF Extraction | PyMuPDF |
| OCR Fallback | Tesseract |
| Summarization | HuggingFace Transformers |
| Semantic Search | Sentence Transformers |
| Citation Verify | Crossref REST API (optional) |
| Testing | Pytest |

---

## Project Structure

```
paperiq-backend/
├── app/
│   ├── main.py            ← FastAPI app entry point
│   ├── config.py          ← All settings (loaded from .env)
│   ├── database.py        ← SQLAlchemy engine + session
│   │
│   ├── api/               ← Route handlers
│   │   ├── health.py
│   │   ├── papers.py
│   │   ├── summaries.py
│   │   ├── citations.py
│   │   └── questions.py
│   │
│   ├── models/            ← SQLAlchemy table definitions
│   │   ├── paper.py
│   │   ├── paper_page.py
│   │   ├── paper_section.py
│   │   ├── paper_chunk.py
│   │   ├── summary.py
│   │   └── citation.py
│   │
│   ├── schemas/           ← Pydantic request/response models
│   │   ├── paper.py
│   │   ├── summary.py
│   │   ├── citation.py
│   │   └── question.py
│   │
│   ├── services/          ← Business logic
│   │   ├── pdf_extractor.py
│   │   ├── ocr_service.py
│   │   ├── text_cleaner.py
│   │   ├── section_detector.py
│   │   ├── chunking_service.py
│   │   ├── summarizer.py
│   │   ├── embedding_service.py
│   │   ├── evidence_matcher.py
│   │   ├── citation_formatter.py
│   │   └── crossref_service.py
│   │
│   └── utils/
│       ├── exceptions.py  ← Custom exception classes
│       └── file_validation.py
│
├── uploads/               ← Uploaded PDFs (git-ignored)
├── tests/                 ← Pytest test files
├── requirements.txt
├── .env                   ← Environment variables (git-ignored)
└── README.md
```

---

## Setup

### 1. Clone and enter the project

```bash
cd paperiq-backend
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate on **Windows**:
```bash
venv\Scripts\activate
```

Activate on **macOS / Ubuntu**:
```bash
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

For OCR support (Ubuntu):
```bash
sudo apt install tesseract-ocr
```

For OCR support (Windows):
Download the installer from https://github.com/UB-Mannheim/tesseract/wiki and add it to your system PATH.

### 4. Configure environment

Copy `.env` and fill in your values (defaults work for local development):
```bash
# .env is already created — just edit if needed
```

### 5. Run the server

```bash
uvicorn app.main:app --reload
```

---

## API Reference

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/v1/health` | Server status check |
| POST | `/api/v1/papers/upload` | Upload a PDF |
| POST | `/api/v1/papers/{id}/process` | Start processing |
| GET | `/api/v1/papers/{id}/status` | Check processing status |
| GET | `/api/v1/papers/{id}` | Get paper details |
| POST | `/api/v1/papers/{id}/summaries` | Generate summary |
| POST | `/api/v1/papers/{id}/citations` | Format citation |
| POST | `/api/v1/papers/{id}/ask` | Ask a question |

### Interactive API docs
```
http://127.0.0.1:8000/docs
```

---

## Processing Status Values

| Status | Meaning |
|---|---|
| `uploaded` | File saved, not yet processed |
| `processing` | Pipeline is running |
| `completed` | Ready to use |
| `failed` | An error occurred |

---

## Summary Types

| Type | Description |
|---|---|
| `short` | 3–5 bullet points |
| `detailed` | Full paragraph per section |
| `section_wise` | Summary of each detected section |
| `key_findings` | Results and conclusion focus |
| `beginner_friendly` | Plain language explanation |

---

## Citation Styles

| Style | Example |
|---|---|
| `apa` | Khan, A. (2025). Title. Journal. |
| `ieee` | A. Khan, "Title," Journal, 2025. |

---

## Error Response Format

All errors follow this format:

```json
{
  "detail": "Only PDF files are accepted."
}
```

---

## Development Roadmap

- [x] **Week 1** — Project setup, FastAPI server, health check, upload endpoint
- [ ] **Week 2** — PDF extraction, text cleaning, section detection, chunking
- [ ] **Week 3** — Summarization, evidence matching, Q&A
- [ ] **Week 4** — Citation formatting, APA/IEEE, Crossref (optional)
- [ ] **Week 5** — Tests, error handling, frontend integration
