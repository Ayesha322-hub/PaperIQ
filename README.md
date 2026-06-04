# PaperIQ — Streamlit Frontend

The frontend for PaperIQ — runs on Streamlit and connects to the FastAPI backend.

## Requirements

- Python 3.10+
- PaperIQ backend running on `http://localhost:8000`

## Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the frontend
streamlit run app.py
```

Opens at: `http://localhost:8501`

## Folder Structure

```
paperiq-frontend/
├── app.py                    ← Main entry point (layout, routing, CSS)
├── api_client.py             ← All backend HTTP calls
├── requirements.txt
├── .streamlit/
│   └── config.toml           ← Theme and server settings
└── pages_ui/
    ├── upload_page.py        ← Upload + processing pipeline
    ├── summary_page.py       ← All 5 summary types
    ├── citation_page.py      ← APA + IEEE citation generation
    ├── ask_page.py           ← Q&A with evidence passages
    └── metadata_page.py      ← Manual metadata correction
```

## Pages

| Page | What it does |
|------|-------------|
| **Upload** | Upload PDF → trigger processing → poll until complete |
| **Summaries** | Choose from 5 summary types, view with evidence |
| **Citations** | Generate APA or IEEE, copy to clipboard |
| **Ask Questions** | Ask anything, get answer + page-numbered evidence |
| **Edit Metadata** | Correct title/authors/year/journal/DOI |

## Deploying to Streamlit Cloud

1. Push this folder to a GitHub repository
2. Go to https://share.streamlit.io
3. Connect your repo and set `app.py` as the main file
4. Set the backend URL in `api_client.py` to your deployed backend URL

> **Note:** For Streamlit Cloud deployment, update `BASE_URL` in `api_client.py`
> to point to your hosted backend (e.g. a Railway or Render deployment).
