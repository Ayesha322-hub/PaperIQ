"""
PaperIQ — Citation Page
"""

import streamlit as st
from api_client import APIError, generate_citation


CITATION_STYLES = {
    "apa":  ("📖", "APA 7th Edition", "Author, A. (Year). Title. Journal."),
    "ieee": ("🔬", "IEEE",            'A. Author, "Title," Journal, Year.'),
}


def render():
    paper_id = st.session_state.get("paper_id")
    if not paper_id:
        st.warning("No paper loaded. Please upload a paper first.")
        return

    detail = st.session_state.get("paper_detail") or {}
    title = detail.get("title") or "Untitled Paper"

    st.markdown("## 📚 Citation Generator")
    st.markdown(f"**Paper:** {title}")
    st.divider()

    # ── Show current metadata ─────────────────────────────────────────────────
    with st.expander("📋 Metadata used for citation (click to review)", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Title:** {detail.get('title') or '—'}")
            st.markdown(f"**Authors:** {', '.join(detail.get('authors', [])) or '—'}")
            st.markdown(f"**Year:** {detail.get('year') or '—'}")
        with col2:
            st.markdown(f"**Journal:** {detail.get('journal') or '—'}")
            st.markdown(f"**DOI:** {detail.get('doi') or '—'}")

        if st.button("✏️ Edit Metadata", help="Correct wrong fields before generating citation"):
            st.session_state.current_page = "metadata"
            st.rerun()

    st.divider()

    # ── Style selector ────────────────────────────────────────────────────────
    st.markdown("### Choose Citation Style")
    col1, col2 = st.columns(2)
    selected_style = st.session_state.get("selected_citation_style", "apa")

    for i, (style_key, (icon, label, example)) in enumerate(CITATION_STYLES.items()):
        col = col1 if i == 0 else col2
        with col:
            is_active = selected_style == style_key
            if st.button(
                f"{icon} {label}",
                key=f"cite_btn_{style_key}",
                use_container_width=True,
                type="primary" if is_active else "secondary",
                help=f"Format: {example}",
            ):
                st.session_state.selected_citation_style = style_key
                st.rerun()

    selected_style = st.session_state.get("selected_citation_style", "apa")
    icon, label, example = CITATION_STYLES[selected_style]
    st.caption(f"Format: *{example}*")
    st.divider()

    # ── Generate ──────────────────────────────────────────────────────────────
    cache_key = f"citation_{paper_id}_{selected_style}"

    if cache_key not in st.session_state:
        if st.button(f"Generate {label} Citation", type="primary", use_container_width=True):
            with st.spinner("Generating citation..."):
                try:
                    result = generate_citation(paper_id, selected_style)
                    st.session_state[cache_key] = result
                    st.rerun()
                except APIError as e:
                    st.error(f"❌ {e.detail}")
        return

    # ── Display citation ──────────────────────────────────────────────────────
    result = st.session_state[cache_key]
    reference = result.get("formatted_reference", "")
    status = result.get("verification_status", "")

    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"### {icon} {label} Citation")
    with col2:
        if st.button("🔄 Regenerate"):
            del st.session_state[cache_key]
            st.rerun()

    # Citation box
    st.markdown(
        f'<div class="citation-box">{reference}</div>',
        unsafe_allow_html=True,
    )

    # Status badge
    status_config = {
        "verified_crossref":           ("✅", "Verified via Crossref",           "success"),
        "generated_from_pdf_metadata": ("📄", "Generated from PDF metadata",     "info"),
        "needs_review":                ("⚠️", "Incomplete metadata — needs review", "warning"),
    }
    s_icon, s_label, s_type = status_config.get(status, ("❓", status, "info"))

    if s_type == "success":
        st.success(f"{s_icon} {s_label}")
    elif s_type == "warning":
        st.warning(f"{s_icon} {s_label}")
    else:
        st.info(f"{s_icon} {s_label}")

    # Always show manual review warning
    st.warning(
        "⚠️ **Always verify before submitting academic work.** "
        "Metadata extracted from PDFs can be incomplete or inaccurate."
    )

    # Copy section
    st.divider()
    st.markdown("#### 📋 Copy Citation")
    st.text_area(
        "Select all and copy",
        reference,
        height=100,
        label_visibility="collapsed",
    )

    # Both styles at once
    st.divider()
    other_style = "ieee" if selected_style == "apa" else "apa"
    other_key = f"citation_{paper_id}_{other_style}"
    other_label = CITATION_STYLES[other_style][1]

    if st.button(f"Also generate {other_label} citation", use_container_width=True):
        with st.spinner(f"Generating {other_label}..."):
            try:
                result2 = generate_citation(paper_id, other_style)
                st.session_state[other_key] = result2
                st.session_state.selected_citation_style = other_style
                st.rerun()
            except APIError as e:
                st.error(f"❌ {e.detail}")
