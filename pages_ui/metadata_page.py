"""
PaperIQ — Edit Metadata Page
"""
import streamlit as st
from api_client import APIError, update_metadata, get_paper


def render():
    paper_id = st.session_state.get("paper_id")
    if not paper_id:
        st.warning("No paper loaded. Please upload a paper first.")
        return

    detail = st.session_state.get("paper_detail") or {}

    st.markdown("""
    <div class="piq-hero">
        <h1>✏️ Edit <span class="accent">Metadata</span></h1>
        <p>Correct any details that were extracted incorrectly from the PDF. Only changed fields are updated.</p>
    </div>
    """, unsafe_allow_html=True)

    st.info("💡 Saving changes will clear cached citations so they regenerate with corrected data.")

    with st.form("metadata_form"):
        st.markdown('<div class="piq-section-title">Paper Details</div>', unsafe_allow_html=True)

        title = st.text_input("Title", value=detail.get("title") or "", placeholder="Full paper title", max_chars=500)

        authors_raw = "\n".join(detail.get("authors") or [])
        authors_input = st.text_area(
            "Authors (one per line)",
            value=authors_raw,
            placeholder="Ali Khan\nSara Ahmed\nBilal Raza",
            height=120,
            help="Enter each author on a separate line.",
        )

        col1, col2 = st.columns(2)
        with col1:
            year_val = detail.get("year")
            year = st.number_input("Publication Year", min_value=1900, max_value=2100, value=int(year_val) if year_val else 2024, step=1)
        with col2:
            journal = st.text_input("Journal / Conference", value=detail.get("journal") or "", placeholder="e.g. IEEE Transactions on Learning Technologies", max_chars=300)

        doi = st.text_input("DOI", value=detail.get("doi") or "", placeholder="e.g. 10.1109/TLT.2024.12345", max_chars=200, help="Digital Object Identifier — found on the paper's title page.")

        st.markdown("<br>", unsafe_allow_html=True)
        submitted = st.form_submit_button("💾  Save Changes", type="primary", use_container_width=True)

    if submitted:
        authors_list = [a.strip() for a in authors_input.strip().splitlines() if a.strip()]
        payload = {}
        if title.strip() != (detail.get("title") or ""):
            payload["title"] = title.strip() or None
        if authors_list != (detail.get("authors") or []):
            payload["authors"] = authors_list
        if year != (detail.get("year") or 0):
            payload["year"] = year
        if journal.strip() != (detail.get("journal") or ""):
            payload["journal"] = journal.strip() or None
        if doi.strip() != (detail.get("doi") or ""):
            payload["doi"] = doi.strip() or None

        if not payload:
            st.info("No changes detected.")
        else:
            with st.spinner("Saving changes..."):
                try:
                    result = update_metadata(paper_id, payload)
                    fresh = get_paper(paper_id)
                    st.session_state.paper_detail = fresh
                    for style in ["apa", "ieee"]:
                        key = f"citation_{paper_id}_{style}"
                        if key in st.session_state:
                            del st.session_state[key]
                    st.success(f"✅ Updated: {', '.join(payload.keys())}")
                    st.caption(result.get("message", ""))
                except APIError as e:
                    st.error(f"❌ {e.detail}")

    st.divider()
    st.markdown('<div class="piq-section-title">📋 Current Stored Values</div>', unsafe_allow_html=True)

    fresh_detail = st.session_state.get("paper_detail") or detail
    col1, col2 = st.columns(2)
    fields_left = [("Title", "title"), ("Authors", None), ("Year", "year")]
    fields_right = [("Journal", "journal"), ("DOI", "doi")]

    with col1:
        st.markdown(f'<div class="piq-card"><span style="color:#94a3b8;font-size:0.82rem;">Title</span><br><span style="color:#e2e8f0;">{fresh_detail.get("title") or "—"}</span></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="piq-card"><span style="color:#94a3b8;font-size:0.82rem;">Authors</span><br><span style="color:#e2e8f0;">{", ".join(fresh_detail.get("authors", [])) or "—"}</span></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="piq-card"><span style="color:#94a3b8;font-size:0.82rem;">Year</span><br><span style="color:#e2e8f0;">{fresh_detail.get("year") or "—"}</span></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="piq-card"><span style="color:#94a3b8;font-size:0.82rem;">Journal</span><br><span style="color:#e2e8f0;">{fresh_detail.get("journal") or "—"}</span></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="piq-card"><span style="color:#94a3b8;font-size:0.82rem;">DOI</span><br><span style="color:#e2e8f0;">{fresh_detail.get("doi") or "—"}</span></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("← Back to Citations", use_container_width=True):
        st.session_state.current_page = "citation"
        st.rerun()
