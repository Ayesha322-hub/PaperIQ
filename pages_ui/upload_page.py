"""
PaperIQ — Upload Page
"""
import time
import streamlit as st
from api_client import APIError, upload_paper, process_paper, get_status, get_paper


def render():
    st.markdown("""
    <div class="piq-hero">
        <h1>📤 Upload <span class="accent">Paper</span></h1>
        <p>Upload a PDF and PaperIQ will extract text, detect sections, and prepare it for AI analysis.</p>
    </div>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Drop your PDF here or click to browse",
        type=["pdf"],
        help="Maximum file size: 20 MB",
    )

    if uploaded_file is None:
        st.markdown("<br>", unsafe_allow_html=True)
        _show_feature_overview()
        return

    file_size_mb = len(uploaded_file.getvalue()) / (1024 * 1024)

    col1, col2, col3 = st.columns(3)
    col1.metric("📁 File", uploaded_file.name[:28])
    col2.metric("📦 Size", f"{file_size_mb:.1f} MB")
    col3.metric("📋 Type", "PDF")

    if file_size_mb > 20:
        st.error("❌ File exceeds 20 MB limit. Please use a smaller PDF.")
        return

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🚀  Upload & Process Paper", type="primary", use_container_width=True):
        _run_pipeline(uploaded_file)


def _run_pipeline(uploaded_file):
    progress = st.progress(0, text="Starting...")
    status_box = st.empty()

    try:
        status_box.info("📤 Uploading PDF...")
        progress.progress(15, text="Uploading PDF...")
        result = upload_paper(file_bytes=uploaded_file.getvalue(), filename=uploaded_file.name)
        paper_id = result["paper_id"]
        st.session_state.paper_id = paper_id
        progress.progress(30, text="Uploaded successfully!")

        status_box.info("⚙️ Starting processing pipeline...")
        progress.progress(40, text="Starting pipeline...")
        process_paper(paper_id)

        status_box.info("🔍 Extracting text, detecting sections, generating embeddings...")
        progress.progress(50, text="Processing — this may take 1–3 minutes...")

        max_polls = 90
        poll_count = 0
        while poll_count < max_polls:
            time.sleep(2)
            poll_count += 1
            status_data = get_status(paper_id)
            current_status = status_data["status"]

            if current_status == "completed":
                progress.progress(90, text="Processing complete!")
                break
            elif current_status == "failed":
                error_msg = status_data.get("error_message") or "Unknown error."
                progress.empty()
                status_box.error(f"❌ Processing failed: {error_msg}")
                return
            else:
                pct = min(50 + int((poll_count / max_polls) * 35), 85)
                pages = status_data.get("total_pages", 0)
                chars = status_data.get("characters_extracted", 0)
                msg = "Processing"
                if pages: msg += f" — {pages} pages"
                if chars: msg += f", {chars:,} characters"
                progress.progress(pct, text=f"{msg}...")
        else:
            progress.empty()
            status_box.error("⏱️ Processing timed out. Try again with a smaller PDF.")
            return

        progress.progress(95, text="Loading paper details...")
        detail = get_paper(paper_id)
        st.session_state.paper_detail = detail
        progress.progress(100, text="Done!")
        status_box.empty()

        st.success("✅ Paper processed successfully!")
        _show_paper_summary(detail, status_data)

        time.sleep(0.5)
        st.session_state.current_page = "summary"
        st.rerun()

    except APIError as e:
        progress.empty()
        status_box.empty()
        if e.status_code == 400:
            st.error(f"❌ {e.detail}")
        elif e.status_code == 413:
            st.error("❌ File too large. Maximum size is 20 MB.")
        elif e.status_code == 503:
            st.error("❌ Cannot connect to backend. Is the server running?")
        else:
            st.error(f"❌ Error ({e.status_code}): {e.detail}")


def _show_paper_summary(detail: dict, status: dict):
    st.markdown('<div class="piq-section-title">📊 Extraction Results</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Pages", status.get("total_pages", 0))
    c2.metric("Characters", f"{status.get('characters_extracted', 0):,}")
    c3.metric("OCR Used", "Yes" if status.get("ocr_used") else "No")
    c4.metric("Sections", len(detail.get("sections", [])))

    if detail.get("title"):
        st.markdown(f'<div class="piq-card"><span style="color:#94a3b8;">Detected Title:</span> <span style="color:#e2e8f0;font-weight:600;">{detail["title"]}</span></div>', unsafe_allow_html=True)
    if detail.get("authors"):
        st.markdown(f'<div class="piq-card"><span style="color:#94a3b8;">Authors:</span> <span style="color:#e2e8f0;">{", ".join(detail["authors"])}</span></div>', unsafe_allow_html=True)
    if detail.get("sections"):
        st.markdown(f'<div class="piq-card"><span style="color:#94a3b8;">Sections:</span> <span style="color:#a78bfa;">{" → ".join(detail["sections"])}</span></div>', unsafe_allow_html=True)


def _show_feature_overview():
    st.markdown('<div class="piq-section-title">✨ What happens after upload</div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    features = [
        ("📝", "Summaries", ["Quick 3–5 point summary", "Detailed section-by-section", "Key findings focus", "Beginner-friendly mode"]),
        ("📚", "Citations",  ["APA 7th edition format", "IEEE format", "Auto-extracted metadata", "Manual correction support"]),
        ("💬", "Q&A",        ["Ask anything about the paper", "Get answers with evidence", "Semantic similarity search", "Fully offline after setup"]),
    ]
    for col, (icon, title, items) in zip([col1, col2, col3], features):
        with col:
            items_html = "".join(f'<li style="color:#94a3b8;font-size:0.85rem;margin-bottom:0.3rem;">{item}</li>' for item in items)
            st.markdown(f"""
            <div class="feat-card">
                <div class="icon">{icon}</div>
                <h3>{title}</h3>
                <ul style="list-style:none;padding:0;margin:0;text-align:left;">{items_html}</ul>
            </div>
            """, unsafe_allow_html=True)
