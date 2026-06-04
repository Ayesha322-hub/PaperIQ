"""
PaperIQ — Streamlit Frontend (Modern UI)
Run: streamlit run app.py
"""

import streamlit as st
from api_client import APIError, health_check

st.set_page_config(
    page_title="PaperIQ",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=Inter:wght@300;400;500;600&display=swap');

/* ── Base ── */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stDecoration"] { display: none; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d0d1a 0%, #0f0f2e 60%, #120b2e 100%) !important;
    border-right: 1px solid rgba(139,92,246,0.2);
}
[data-testid="stSidebar"] * { color: #e2e8f0 !important; }
[data-testid="stSidebar"] .stButton button {
    background: transparent !important;
    border: 1px solid rgba(139,92,246,0.25) !important;
    color: #cbd5e1 !important;
    border-radius: 10px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.88rem !important;
    transition: all 0.2s ease !important;
    text-align: left !important;
}
[data-testid="stSidebar"] .stButton button:hover {
    background: rgba(139,92,246,0.15) !important;
    border-color: rgba(139,92,246,0.6) !important;
    color: #fff !important;
}
[data-testid="stSidebar"] .stButton button[kind="primary"] {
    background: linear-gradient(135deg, #7c3aed, #4f46e5) !important;
    border: none !important;
    color: #fff !important;
    box-shadow: 0 2px 12px rgba(124,58,237,0.4) !important;
}

/* ── Main area ── */
[data-testid="stAppViewContainer"] > .main {
    background: #07071a;
}
[data-testid="block-container"] {
    padding-top: 1.5rem !important;
}

/* ── Page header ── */
.piq-hero {
    background: linear-gradient(135deg, #0f0f2e 0%, #1a0a3e 50%, #0f1f4e 100%);
    border: 1px solid rgba(139,92,246,0.3);
    border-radius: 16px;
    padding: 2.4rem 3rem;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
}
.piq-hero::before {
    content: '';
    position: absolute;
    top: -60px; right: -60px;
    width: 220px; height: 220px;
    background: radial-gradient(circle, rgba(139,92,246,0.18) 0%, transparent 70%);
    border-radius: 50%;
}
.piq-hero h1 {
    font-family: 'Syne', sans-serif;
    font-size: 2.4rem;
    font-weight: 800;
    color: #fff;
    margin: 0 0 0.4rem;
    letter-spacing: -0.02em;
}
.piq-hero p {
    color: #94a3b8;
    font-size: 1.05rem;
    margin: 0;
    font-weight: 300;
}
.piq-hero .accent { color: #a78bfa; }

/* ── Section title ── */
.piq-section-title {
    font-family: 'Syne', sans-serif;
    font-size: 1.5rem;
    font-weight: 700;
    color: #e2e8f0;
    margin: 0 0 1rem;
    letter-spacing: -0.01em;
}

/* ── Cards ── */
.piq-card {
    background: linear-gradient(135deg, #0f0f2e, #13103a);
    border: 1px solid rgba(139,92,246,0.2);
    border-radius: 14px;
    padding: 1.4rem 1.6rem;
    margin-bottom: 1rem;
    transition: border-color 0.2s;
}
.piq-card:hover { border-color: rgba(139,92,246,0.5); }

/* ── Feature cards (home) ── */
.feat-card {
    background: linear-gradient(135deg, #0f0f2e, #13103a);
    border: 1px solid rgba(139,92,246,0.2);
    border-radius: 14px;
    padding: 1.8rem 1.5rem;
    text-align: center;
    height: 100%;
    transition: all 0.25s ease;
}
.feat-card:hover {
    border-color: rgba(139,92,246,0.55);
    transform: translateY(-3px);
    box-shadow: 0 8px 30px rgba(124,58,237,0.2);
}
.feat-card .icon { font-size: 2.4rem; margin-bottom: 0.8rem; }
.feat-card h3 {
    font-family: 'Syne', sans-serif;
    color: #e2e8f0;
    font-size: 1.1rem;
    font-weight: 700;
    margin: 0 0 0.5rem;
}
.feat-card p { color: #94a3b8; font-size: 0.88rem; line-height: 1.5; margin: 0; }

/* ── Steps (how it works) ── */
.step-row {
    display: flex;
    align-items: flex-start;
    gap: 1.2rem;
    margin-bottom: 1.2rem;
}
.step-num {
    min-width: 38px; height: 38px;
    background: linear-gradient(135deg, #7c3aed, #4f46e5);
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-family: 'Syne', sans-serif;
    font-weight: 700; font-size: 0.95rem; color: #fff;
    box-shadow: 0 2px 10px rgba(124,58,237,0.4);
}
.step-content h4 {
    font-family: 'Syne', sans-serif;
    color: #e2e8f0; font-size: 1rem; font-weight: 700; margin: 0 0 0.2rem;
}
.step-content p { color: #94a3b8; font-size: 0.87rem; margin: 0; }

/* ── Badges ── */
.badge {
    display: inline-block;
    padding: 0.2rem 0.7rem;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.04em;
    text-transform: uppercase;
}
.badge-uploaded   { background: rgba(59,130,246,0.15); color: #60a5fa; border: 1px solid rgba(59,130,246,0.3); }
.badge-processing { background: rgba(245,158,11,0.15); color: #fbbf24; border: 1px solid rgba(245,158,11,0.3); }
.badge-completed  { background: rgba(16,185,129,0.15); color: #34d399; border: 1px solid rgba(16,185,129,0.3); }
.badge-failed     { background: rgba(239,68,68,0.15);  color: #f87171; border: 1px solid rgba(239,68,68,0.3); }

/* ── Evidence card ── */
.evidence-card {
    background: rgba(139,92,246,0.07);
    border: 1px solid rgba(139,92,246,0.2);
    border-radius: 10px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.8rem;
    color: #cbd5e1;
    font-size: 0.92rem;
}
.evidence-card .meta  { color: #94a3b8; font-size: 0.8rem; margin-bottom: 0.5rem; }
.evidence-card .score { color: #a78bfa; font-weight: 600; }

/* ── Citation box ── */
.citation-box {
    background: rgba(79,70,229,0.08);
    border: 1px solid rgba(79,70,229,0.35);
    border-left: 4px solid #7c3aed;
    border-radius: 10px;
    padding: 1.2rem 1.4rem;
    font-family: 'Georgia', serif;
    font-size: 0.95rem;
    line-height: 1.7;
    color: #e2e8f0;
    margin: 0.5rem 0;
}

/* ── Summary point ── */
.summary-point {
    background: rgba(15,15,46,0.8);
    border: 1px solid rgba(139,92,246,0.18);
    border-radius: 10px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.7rem;
    color: #cbd5e1;
}
.summary-point .section-tag {
    background: rgba(139,92,246,0.2);
    color: #a78bfa;
    padding: 0.15rem 0.5rem;
    border-radius: 4px;
    font-size: 0.75rem;
    font-weight: 600;
}

/* ── Divider ── */
hr { border-color: rgba(139,92,246,0.15) !important; }

/* ── Metrics ── */
[data-testid="stMetric"] {
    background: rgba(15,15,46,0.8) !important;
    border: 1px solid rgba(139,92,246,0.2) !important;
    border-radius: 10px !important;
    padding: 1rem !important;
}
[data-testid="stMetricLabel"] { color: #94a3b8 !important; }
[data-testid="stMetricValue"] { color: #e2e8f0 !important; }

/* ── Inputs ── */
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea,
[data-testid="stNumberInput"] input {
    background: rgba(15,15,46,0.9) !important;
    border: 1px solid rgba(139,92,246,0.25) !important;
    color: #e2e8f0 !important;
    border-radius: 8px !important;
}
[data-testid="stTextInput"] input:focus,
[data-testid="stTextArea"] textarea:focus {
    border-color: rgba(139,92,246,0.6) !important;
    box-shadow: 0 0 0 2px rgba(124,58,237,0.15) !important;
}

/* ── Primary buttons ── */
.stButton button[kind="primary"] {
    background: linear-gradient(135deg, #7c3aed, #4f46e5) !important;
    border: none !important;
    color: #fff !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    letter-spacing: 0.02em !important;
    box-shadow: 0 4px 15px rgba(124,58,237,0.35) !important;
    transition: all 0.2s ease !important;
}
.stButton button[kind="primary"]:hover {
    box-shadow: 0 6px 20px rgba(124,58,237,0.5) !important;
    transform: translateY(-1px) !important;
}
.stButton button[kind="secondary"] {
    background: rgba(15,15,46,0.8) !important;
    border: 1px solid rgba(139,92,246,0.3) !important;
    color: #cbd5e1 !important;
    border-radius: 10px !important;
}

/* ── Expander ── */
[data-testid="stExpander"] {
    background: rgba(15,15,46,0.6) !important;
    border: 1px solid rgba(139,92,246,0.2) !important;
    border-radius: 10px !important;
}

/* ── Info/success/error/warning boxes ── */
[data-testid="stAlert"] {
    border-radius: 10px !important;
}

/* ── File uploader ── */
[data-testid="stFileUploader"] {
    background: rgba(15,15,46,0.6) !important;
    border: 2px dashed rgba(139,92,246,0.3) !important;
    border-radius: 12px !important;
}

/* ── Sidebar logo area ── */
.sidebar-logo {
    padding: 1.2rem 0.5rem 0.5rem;
    text-align: center;
    border-bottom: 1px solid rgba(139,92,246,0.2);
    margin-bottom: 1rem;
}
.sidebar-logo h2 {
    font-family: 'Syne', sans-serif;
    font-size: 1.4rem;
    font-weight: 800;
    color: #fff !important;
    margin: 0.3rem 0 0.2rem;
    letter-spacing: -0.01em;
}
.sidebar-logo p { color: #94a3b8 !important; font-size: 0.78rem; margin: 0; }

/* ── Nav label ── */
.nav-label {
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #64748b !important;
    font-weight: 600;
    margin: 0.8rem 0 0.3rem;
    padding-left: 0.2rem;
}
</style>
""", unsafe_allow_html=True)


# ── Session state ─────────────────────────────────────────────────────────────
defaults = {
    "paper_id": None,
    "paper_detail": None,
    "processing_status": None,
    "current_page": "home",
    "backend_ok": False,
}
for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sidebar-logo">
        <div style="font-size:2rem;">📄</div>
        <h2>PaperIQ</h2>
        <p>AI Research Assistant</p>
    </div>
    """, unsafe_allow_html=True)

    # Backend status
    st.markdown('<div class="nav-label">System</div>', unsafe_allow_html=True)
    if st.button("⚡ Check Connection", use_container_width=True):
        try:
            health_check()
            st.session_state.backend_ok = True
        except APIError as e:
            st.session_state.backend_ok = False
            st.error(e.detail)

    if st.session_state.backend_ok:
        st.success("✅ Backend connected")
    else:
        st.warning("⚠️ Not connected")

    st.markdown('<div class="nav-label">Navigate</div>', unsafe_allow_html=True)

    pages = {
        "home":     ("🏠", "Home"),
        "about":    ("ℹ️",  "About"),
        "upload":   ("📤", "Upload Paper"),
        "summary":  ("📝", "Summaries"),
        "citation": ("📚", "Citations"),
        "ask":      ("💬", "Ask Questions"),
        "metadata": ("✏️",  "Edit Metadata"),
    }

    for page_key, (icon, label) in pages.items():
        is_active = st.session_state.current_page == page_key
        needs_paper = page_key in {"summary", "citation", "ask", "metadata"}
        disabled = needs_paper and st.session_state.paper_id is None

        if st.button(
            f"{icon}  {label}",
            key=f"nav_{page_key}",
            use_container_width=True,
            disabled=disabled,
            type="primary" if is_active else "secondary",
        ):
            st.session_state.current_page = page_key
            st.rerun()

    if st.session_state.paper_id:
        st.markdown('<div class="nav-label">Current Paper</div>', unsafe_allow_html=True)
        detail = st.session_state.paper_detail
        if detail:
            title = detail.get("title") or "Untitled"
            st.markdown(f'<div style="color:#e2e8f0;font-size:0.82rem;padding:0.4rem 0;line-height:1.4;">{title[:55]}{"..." if len(title) > 55 else ""}</div>', unsafe_allow_html=True)
            status = detail.get("processing_status", "unknown")
            st.markdown(f'<span class="badge badge-{status}">{status}</span>', unsafe_allow_html=True)
            st.caption(f"Pages: {detail.get('total_pages', 0)}")
        st.button(
            "🗑️  New Paper",
            use_container_width=True,
            on_click=lambda: st.session_state.update(
                paper_id=None, paper_detail=None,
                processing_status=None, current_page="upload"
            ),
        )

    st.markdown('<div style="margin-top:2rem;"></div>', unsafe_allow_html=True)
    st.markdown('<div style="color:#475569;font-size:0.72rem;text-align:center;">PaperIQ v1.0.0 · Offline-first AI</div>', unsafe_allow_html=True)


# ── Page routing ──────────────────────────────────────────────────────────────
page = st.session_state.current_page

if page == "home":
    from pages_ui.home_page import render
elif page == "about":
    from pages_ui.about_page import render
elif page == "upload":
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
    from pages_ui.home_page import render

render()
