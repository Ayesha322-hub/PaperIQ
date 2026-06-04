"""
PaperIQ — Upload Page
Handles PDF upload, processing pipeline trigger, and status polling.
"""

import time
import streamlit as st
from api_client import APIError, upload_paper, process_paper, get_status, get_paper


def render():
    st.markdown("## 📤 Upload Research Paper")
    st.markdown("Upload a PDF and PaperIQ will extract text, detect sections, and prepare it for summarisation and Q&A.")

    # ── Upload widget ─────────────────────────────────────────────────────────
    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type=["pdf"],
        help="Maximum file size: 20 MB",
    )

    if uploaded_file is None:
        st.info("👆 Upload a research paper PDF to get started.")
        _show_feature_overview()
        return

    # Show file info
    file_size_mb = len(uploaded_file.getvalue()) / (1024 * 1024)
    col1, col2, col3 = st.columns(3)
    col1.metric("File", uploaded_file.name[:30])
    col2.metric("Size", f"{file_size_mb:.1f} MB")
    col3.metric("Type", "PDF")

    if file_size_mb > 20:
        st.error("❌ File exceeds 20 MB limit. Please use a smaller PDF.")
        return

    # ── Upload button ─────────────────────────────────────────────────────────
    if st.button("🚀 Upload & Process Paper", type="primary", use_container_width=True):
        _run_pipeline(uploaded_file)


def _run_pipeline(uploaded_file):
    """Run the full upload → process → poll pipeline with live status updates."""

    progress = st.progress(0, text="Starting...")
    status_box = st.empty()

    try:
        # Step 1: Upload
        status_box.info("📤 Uploading PDF...")
        progress.progress(15, text="Uploading PDF...")

        result = upload_paper(
            file_bytes=uploaded_file.getvalue(),
            filename=uploaded_file.name,
        )
        paper_id = result["paper_id"]
        st.session_state.paper_id = paper_id
        progress.progress(30, text="Uploaded successfully!")

        # Step 2: Trigger processing
        status_box.info("⚙️ Starting processing pipeline...")
        progress.progress(40, text="Starting pipeline...")
        process_paper(paper_id)

        # Step 3: Poll status
        status_box.info("🔍 Extracting text, detecting sections, generating embeddings...")
        progress.progress(50, text="Processing (this may take 1–3 minutes)...")

        max_polls = 90  # 3 minutes
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
                # Animate the progress bar while waiting
                pct = min(50 + int((poll_count / max_polls) * 35), 85)
                pages = status_data.get("total_pages", 0)
                chars = status_data.get("characters_extracted", 0)
                msg = "Processing"
                if pages:
                    msg += f" — {pages} pages"
                if chars:
                    msg += f", {chars:,} characters"
                progress.progress(pct, text=f"{msg}...")

        else:
            progress.empty()
            status_box.error("⏱️ Processing timed out. Try again with a smaller PDF.")
            return

        # Step 4: Load paper details
        progress.progress(95, text="Loading paper details...")
        detail = get_paper(paper_id)
        st.session_state.paper_detail = detail

        progress.progress(100, text="Done!")
        status_box.empty()

        # ── Success display ───────────────────────────────────────────────────
        st.success("✅ Paper processed successfully!")
        _show_paper_summary(detail, status_data)

        # Navigate to summaries
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
            st.error("❌ Cannot connect to the backend. Is the server running?")
        else:
            st.error(f"❌ Error ({e.status_code}): {e.detail}")


def _show_paper_summary(detail: dict, status: dict):
    """Show a quick summary of what was extracted."""
    st.markdown("### 📊 Extraction Results")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Pages", status.get("total_pages", 0))
    c2.metric("Characters", f"{status.get('characters_extracted', 0):,}")
    c3.metric("OCR Used", "Yes" if status.get("ocr_used") else "No")
    c4.metric("Sections", len(detail.get("sections", [])))

    if detail.get("title"):
        st.markdown(f"**Detected Title:** {detail['title']}")
    if detail.get("authors"):
        st.markdown(f"**Authors:** {', '.join(detail['authors'])}")
    if detail.get("sections"):
        st.markdown(f"**Sections:** {' → '.join(detail['sections'])}")


def _show_feature_overview():
    st.markdown("---")
    st.markdown("### ✨ What PaperIQ can do")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("#### 📝 Summaries")
        st.markdown("""
- Quick 3–5 point summary
- Detailed section-by-section
- Key findings focus
- Beginner-friendly explanation
""")
    with col2:
        st.markdown("#### 📚 Citations")
        st.markdown("""
- APA 7th edition format
- IEEE format
- Auto-extracted metadata
- Manual correction support
""")
    with col3:
        st.markdown("#### 💬 Q&A")
        st.markdown("""
- Ask anything about the paper
- Get evidence with page numbers
- Semantic similarity search
- Fully offline after setup
""")
