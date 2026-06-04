"""
PaperIQ — About Page
"""
import streamlit as st


def render():
    st.markdown("""
    <div class="piq-hero">
        <h1>About <span class="accent">PaperIQ</span></h1>
        <p>Built for students, researchers, and academics who need to move fast.</p>
    </div>
    """, unsafe_allow_html=True)

    left, right = st.columns([3, 2], gap="large")

    with left:
        st.markdown('<div class="piq-section-title">What is PaperIQ?</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="piq-card">
            <p style="color:#cbd5e1;line-height:1.8;font-size:0.95rem;">
                PaperIQ is an <strong style="color:#a78bfa;">offline-first AI research assistant</strong> that helps you 
                understand academic papers faster. Upload any research PDF and instantly get structured summaries, 
                proper academic citations, and the ability to ask natural language questions — all powered by 
                local AI models running entirely on your own machine.
            </p>
            <p style="color:#cbd5e1;line-height:1.8;font-size:0.95rem;margin-top:0.8rem;">
                No API keys. No cloud uploads. No subscription fees. Your research stays private.
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="piq-section-title" style="margin-top:1.5rem;">Technology Stack</div>', unsafe_allow_html=True)
        tech = [
            ("🧠", "Transformers", "HuggingFace transformers for summarization (DistilBART)"),
            ("🔍", "Sentence Transformers", "Semantic search & embeddings (MiniLM-L6-v2)"),
            ("📄", "PyMuPDF + Tesseract", "PDF text extraction with OCR fallback"),
            ("⚡", "FastAPI", "High-performance async Python backend"),
            ("🗃️", "SQLite + SQLAlchemy", "Local database for paper storage"),
            ("🎨", "Streamlit", "Interactive web UI"),
        ]
        for icon, name, desc in tech:
            st.markdown(f"""
            <div class="piq-card" style="padding:0.8rem 1.2rem;margin-bottom:0.5rem;display:flex;align-items:center;gap:0.8rem;">
                <span style="font-size:1.3rem;">{icon}</span>
                <div>
                    <span style="color:#e2e8f0;font-weight:600;">{name}</span>
                    <span style="color:#64748b;font-size:0.82rem;margin-left:0.4rem;">— {desc}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

    with right:
        st.markdown('<div class="piq-section-title">Key Features</div>', unsafe_allow_html=True)
        features = [
            ("✅", "PDF Upload & Processing", "Handles text-based and scanned PDFs"),
            ("✅", "5 Summary Modes", "From quick bullets to beginner-friendly explanations"),
            ("✅", "APA & IEEE Citations", "Auto-extracted and Crossref-verified"),
            ("✅", "Semantic Q&A", "Ask questions, get answers with evidence"),
            ("✅", "Metadata Editor", "Fix incorrectly extracted paper details"),
            ("✅", "Section Detection", "Automatically identifies paper structure"),
            ("✅", "Fully Offline", "No internet required after setup"),
            ("✅", "Privacy First", "Your papers never leave your machine"),
        ]
        for icon, title, desc in features:
            st.markdown(f"""
            <div style="display:flex;gap:0.7rem;margin-bottom:0.7rem;align-items:flex-start;">
                <span style="color:#34d399;font-size:1rem;margin-top:0.1rem;">{icon}</span>
                <div>
                    <span style="color:#e2e8f0;font-weight:600;font-size:0.92rem;">{title}</span><br>
                    <span style="color:#64748b;font-size:0.82rem;">{desc}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="piq-section-title">Limitations</div>', unsafe_allow_html=True)
        limits = [
            "⚠️ First inference run downloads AI models (~1 GB)",
            "⚠️ Summarization may take 30–60 seconds first time",
            "⚠️ Scanned PDFs require Tesseract OCR installed",
            "⚠️ Very large papers (100+ pages) may be slow",
            "⚠️ Citation metadata depends on PDF quality",
        ]
        for l in limits:
            st.markdown(f'<div style="color:#94a3b8;font-size:0.85rem;margin-bottom:0.4rem;">{l}</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.divider()
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🚀  Start Using PaperIQ", type="primary", use_container_width=True):
            st.session_state.current_page = "upload"
            st.rerun()
    with c2:
        if st.button("🏠  Back to Home", use_container_width=True):
            st.session_state.current_page = "home"
            st.rerun()
