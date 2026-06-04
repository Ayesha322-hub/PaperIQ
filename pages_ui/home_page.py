"""
PaperIQ — Home Page
"""
import streamlit as st


def render():
    # ── Hero ──────────────────────────────────────────────────────────────────
    st.markdown("""
    <div class="piq-hero">
        <h1>📄 Paper<span class="accent">IQ</span></h1>
        <p>Your AI-powered research assistant — summarize, cite, and interrogate academic papers in seconds.</p>
    </div>
    """, unsafe_allow_html=True)

    # ── CTA buttons ───────────────────────────────────────────────────────────
    c1, c2, c3 = st.columns([1, 1, 2])
    with c1:
        if st.button("🚀  Get Started", type="primary", use_container_width=True):
            st.session_state.current_page = "upload"
            st.rerun()
    with c2:
        if st.button("ℹ️  Learn More", use_container_width=True):
            st.session_state.current_page = "about"
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Feature cards ─────────────────────────────────────────────────────────
    st.markdown('<div class="piq-section-title">What PaperIQ Does</div>', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    features = [
        ("📝", "Smart Summaries", "Get quick 3-point overviews or detailed section-by-section breakdowns — your choice."),
        ("📚", "Citation Generator", "Instantly generate APA or IEEE citations from extracted PDF metadata."),
        ("💬", "Ask Anything", "Ask natural language questions and get answers with page-level evidence."),
        ("🔒", "100% Offline", "All AI runs locally on your machine. Your papers never leave your computer."),
    ]
    for col, (icon, title, desc) in zip([col1, col2, col3, col4], features):
        with col:
            st.markdown(f"""
            <div class="feat-card">
                <div class="icon">{icon}</div>
                <h3>{title}</h3>
                <p>{desc}</p>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── How it works ──────────────────────────────────────────────────────────
    left, right = st.columns([1, 1], gap="large")

    with left:
        st.markdown('<div class="piq-section-title">How It Works</div>', unsafe_allow_html=True)
        steps = [
            ("Upload", "Drop your PDF research paper into PaperIQ — up to 20 MB."),
            ("Process", "Our AI extracts text, detects sections, and builds a semantic index."),
            ("Explore", "Summarize, generate citations, or ask questions about your paper."),
            ("Export", "Copy results, citations, and summaries directly to your work."),
        ]
        for i, (title, desc) in enumerate(steps, 1):
            st.markdown(f"""
            <div class="step-row">
                <div class="step-num">{i}</div>
                <div class="step-content">
                    <h4>{title}</h4>
                    <p>{desc}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)

    with right:
        st.markdown('<div class="piq-section-title">Supported Summary Types</div>', unsafe_allow_html=True)
        summary_types = [
            ("⚡", "Quick Summary",         "3–5 bullet points covering the whole paper"),
            ("📋", "Full Summary",           "One detailed paragraph per section"),
            ("🗂️", "Section-by-Section",    "Summary of every detected section"),
            ("🔑", "Key Findings",           "Results, Discussion & Conclusion focus"),
            ("🎓", "Beginner-Friendly",      "Plain language for non-experts"),
        ]
        for icon, title, desc in summary_types:
            st.markdown(f"""
            <div class="piq-card" style="padding:0.9rem 1.2rem;margin-bottom:0.6rem;">
                <span style="font-size:1.1rem;">{icon}</span>
                <span style="color:#e2e8f0;font-weight:600;margin-left:0.5rem;">{title}</span>
                <span style="color:#64748b;font-size:0.82rem;margin-left:0.5rem;">— {desc}</span>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Stats strip ───────────────────────────────────────────────────────────
    st.markdown('<div class="piq-section-title">Built for Researchers</div>', unsafe_allow_html=True)
    s1, s2, s3, s4 = st.columns(4)
    stats = [
        ("20 MB", "Max PDF Size"),
        ("2 Styles", "APA & IEEE"),
        ("5 Types", "Summary Modes"),
        ("100%", "Offline & Private"),
    ]
    for col, (val, label) in zip([s1, s2, s3, s4], stats):
        with col:
            st.metric(label, val)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align:center;color:#475569;font-size:0.85rem;padding:1rem;">
        Ready to analyze your first paper? Click <strong style="color:#a78bfa;">Get Started</strong> above.
    </div>
    """, unsafe_allow_html=True)
