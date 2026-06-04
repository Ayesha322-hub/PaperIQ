"""
PaperIQ — Streamlit Frontend
Run: streamlit run app.py
"""

import streamlit as st
from api_client import APIError, health_check

# ── Page config — must be first Streamlit call ────────────────────────────────
st.set_page_config(
    page_title="PaperIQ",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* Main header */
.paperiq-header {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    padding: 2rem 2.5rem;
    border-radius: 12px;
    margin-bottom: 1.5rem;
    color: white;
}
.paperiq-header h1 { margin: 0; font-size: 2.2rem; font-weight: 700; }
.paperiq-header p  { margin: 0.3rem 0 0; opacity: 0.8; font-size: 1rem; }

/* Status badges */
.badge {
    display: inline-block;
    padding: 0.2rem 0.7rem;
    border-radius: 20px;
    font-size: 0.78rem;
    font-weight: 600;
    letter-spacing: 0.03em;
}
.badge-uploaded    { background: #e8f4fd; color: #1565c0; }
.badge-processing  { background: #fff8e1; color: #f57f17; }
.badge-completed   { background: #e8f5e9; color: #2e7d32; }
.badge-failed      { background: #ffebee; color: #c62828; }

/* Section cards */
.section-card {
    background: #f8f9fa;
    border-left: 4px solid #0f3460;
    padding: 0.8rem 1rem;
    border-radius: 0 8px 8px 0;
    margin-bottom: 0.6rem;
}

/* Evidence card */
.evidence-card {
    background: #f0f4ff;
    border: 1px solid #c5cae9;
    border-radius: 8px;
    padding: 0.9rem 1.1rem;
    margin-bottom: 0.7rem;
}
.evidence-card .score { color: #3949ab; font-weight: 600; font-size: 0.82rem; }
.evidence-card .meta  { color: #666; font-size: 0.8rem; margin-bottom: 0.4rem; }

/* Citation box */
.citation-box {
    background: #fffde7;
    border: 1px solid #f9a825;
    border-radius: 8px;
    padding: 1rem 1.2rem;
    font-family: 'Georgia', serif;
    font-size: 0.95rem;
    line-height: 1.6;
    margin: 0.5rem 0;
}

/* Summary point */
.summary-point {
    background: white;
    border: 1px solid #e0e0e0;
    border-radius: 8px;
    padding: 0.9rem 1.1rem;
    margin-bottom: 0.6rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
}
.summary-point .section-tag {
    background: #e3f2fd;
    color: #1565c0;
    padding: 0.15rem 0.5rem;
    border-radius: 4px;
    font-size: 0.75rem;
    font-weight: 600;
}

/* Sidebar */
[data-testid="stSidebar"] { background: #f5f6fa; }

/* Hide Streamlit branding */
#MainMenu { visibility: hidden; }
footer    { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


# ── Session state initialisation ──────────────────────────────────────────────
defaults = {
    "paper_id": None,
    "paper_detail": None,
    "processing_status": None,
    "current_page": "upload",
    "backend_ok": False,
}
for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val


# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="paperiq-header">
    <h1>📄 PaperIQ</h1>
    <p>AI-powered research paper summarizer, citation helper &amp; evidence finder</p>
</div>
""", unsafe_allow_html=True)


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🔌 Backend Status")

    if st.button("Check Connection", use_container_width=True):
        try:
            health_check()
            st.session_state.backend_ok = True
        except APIError as e:
            st.session_state.backend_ok = False
            st.error(e.detail)

    if st.session_state.backend_ok:
        st.success("✅ Connected to backend")
    else:
        st.warning("⚠️ Not verified — click above")
        st.caption("Make sure the backend is running:\n```\nuvicorn app.main:app --reload\n```")

    st.divider()

    st.markdown("### 🗺️ Navigation")

    pages = {
        "upload":    ("📤", "Upload Paper"),
        "summary":   ("📝", "Summaries"),
        "citation":  ("📚", "Citations"),
        "ask":       ("💬", "Ask Questions"),
        "metadata":  ("✏️",  "Edit Metadata"),
    }

    for page_key, (icon, label) in pages.items():
        is_active = st.session_state.current_page == page_key
        # Disable pages that need a processed paper
        needs_paper = page_key in {"summary", "citation", "ask", "metadata"}
        disabled = needs_paper and st.session_state.paper_id is None

        if st.button(
            f"{icon} {label}",
            key=f"nav_{page_key}",
            use_container_width=True,
            disabled=disabled,
            type="primary" if is_active else "secondary",
        ):
            st.session_state.current_page = page_key
            st.rerun()

    # Show current paper info
    if st.session_state.paper_id:
        st.divider()
        st.markdown("### 📄 Current Paper")
        detail = st.session_state.paper_detail
        if detail:
            title = detail.get("title") or "Untitled"
            st.markdown(f"**{title[:50]}{'...' if len(title) > 50 else ''}**")
            status = detail.get("processing_status", "unknown")
            badge_class = f"badge-{status}"
            st.markdown(
                f'<span class="badge {badge_class}">{status.upper()}</span>',
                unsafe_allow_html=True,
            )
            st.caption(f"Pages: {detail.get('total_pages', 0)}")
        st.button(
            "🗑️ Clear / New Paper",
            use_container_width=True,
            on_click=lambda: st.session_state.update(
                paper_id=None, paper_detail=None,
                processing_status=None, current_page="upload"
            ),
        )

    st.divider()
    st.caption("PaperIQ v1.0.0 | Offline-first AI")


# ── Page routing ──────────────────────────────────────────────────────────────
page = st.session_state.current_page

if page == "upload":
    from pages_ui.upload_page import render
elif page == "summary":
    from pages_ui.summary_page import render
elif page == "citation":
    from pages_ui.citation_page import render
elif page == "ask":
    from pages_ui.ask_page import render
elif page == "metadata":
    from pages_ui.metadata_page import render
else:
    from pages_ui.upload_page import render

render()
