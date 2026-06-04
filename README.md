# PaperIQ

AI-powered research paper summarizer, citation helper, and evidence finder.
Built with FastAPI (backend) + Streamlit (frontend). Works fully offline after setup.

## Project Structure

```
PaperIQ/
├── paperiq-backend/    ← FastAPI backend (Python)
└── paperiq-frontend/   ← Streamlit frontend (Python)
```

## Quick Start

### 1. Backend

```bash
cd paperiq-backend
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # macOS / Ubuntu
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

Backend runs at: http://localhost:8000
Swagger UI: http://localhost:8000/docs

### 2. Frontend (new terminal)

```bash
cd paperiq-frontend
pip install -r requirements.txt
streamlit run app.py
```

Frontend runs at: http://localhost:8501

## Features

- Upload research paper PDFs (up to 20 MB)
- Extract text page by page with OCR fallback
- Auto-detect sections (Abstract, Introduction, Methodology, etc.)
- Generate 5 types of summaries (short, detailed, section-wise, key findings, beginner-friendly)
- Generate APA and IEEE citations from extracted metadata
- Ask questions about the paper with page-numbered evidence
- Manually correct extracted metadata
- Optional Crossref DOI verification

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI + SQLite + SQLAlchemy |
| PDF Extraction | PyMuPDF + Tesseract OCR |
| Summarization | HuggingFace distilbart-cnn-12-6 |
| Semantic Search | sentence-transformers all-MiniLM-L6-v2 |
| Frontend | Streamlit |

## First Run Note

The first time you generate a summary or ask a question, the AI models download (~600 MB total) and cache locally. All subsequent runs are fully offline.
