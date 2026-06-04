"""
PaperIQ — Summary Page
"""

import streamlit as st
from api_client import APIError, generate_summary, get_paper

SUMMARY_TYPES = {
    "short":             ("⚡", "Quick Summary",        "3–5 bullet points covering the whole paper"),
    "detailed":          ("📋", "Full Summary",          "One detailed paragraph per section"),
    "section_wise":      ("🗂️", "By Section",            "Summary of every detected section"),
    "key_findings":      ("🔑", "Key Findings",          "Results, Discussion and Conclusion only"),
    "beginner_friendly": ("🎓", "Simple Explanation",    "Plain language for non-experts"),
}


def render():
    paper_id = st.session_state.get("paper_id")
    if not paper_id:
        st.warning("No paper loaded. Please upload a paper first.")
        return

    # Refresh detail if needed
    detail = st.session_state.get("paper_detail") or {}
    title = detail.get("title") or "Untitled Paper"

    st.markdown(f"## 📝 Summaries")
    st.markdown(f"**Paper:** {title}")
    st.divider()

    # ── Summary type selector ─────────────────────────────────────────────────
    st.markdown("### Choose Summary Type")
    cols = st.columns(len(SUMMARY_TYPES))
    selected_type = st.session_state.get("selected_summary_type", "short")

    for i, (key, (icon, label, desc)) in enumerate(SUMMARY_TYPES.items()):
        with cols[i]:
            is_selected = selected_type == key
            if st.button(
                f"{icon}\n{label}",
                key=f"sum_btn_{key}",
                use_container_width=True,
                type="primary" if is_selected else "secondary",
                help=desc,
            ):
                st.session_state.selected_summary_type = key
                st.rerun()

    selected_type = st.session_state.get("selected_summary_type", "short")
    icon, label, desc = SUMMARY_TYPES[selected_type]
    st.caption(f"{icon} **{label}** — {desc}")
    st.divider()

    # ── Generate button ───────────────────────────────────────────────────────
    cache_key = f"summary_{paper_id}_{selected_type}"

    if cache_key not in st.session_state:
        if st.button(f"Generate {label}", type="primary", use_container_width=True):
            with st.spinner(f"Generating {label.lower()}... (first run may take ~30 seconds)"):
                try:
                    result = generate_summary(paper_id, selected_type)
                    st.session_state[cache_key] = result
                    st.rerun()
                except APIError as e:
                    st.error(f"❌ {e.detail}")
        return

    # ── Display summary ───────────────────────────────────────────────────────
    result = st.session_state[cache_key]
    points = result.get("summary_points", [])

    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"### {icon} {label}")
    with col2:
        if st.button("🔄 Regenerate", help="Clear cache and regenerate"):
            del st.session_state[cache_key]
            st.rerun()

    if not points:
        st.info("No summary points were generated. The paper may be too short.")
        return

    st.markdown(f"*{len(points)} point{'s' if len(points) != 1 else ''} generated*")
    st.markdown("")

    for i, point in enumerate(points, 1):
        _render_summary_point(i, point)

    # ── Export ────────────────────────────────────────────────────────────────
    st.divider()
    st.markdown("#### 📋 Copy as Text")
    full_text = "\n\n".join(
        f"{i}. [{p.get('section', 'General')}] {p['text']}"
        for i, p in enumerate(points, 1)
    )
    st.text_area("Summary text (select all and copy)", full_text, height=200, label_visibility="collapsed")


def _render_summary_point(index: int, point: dict):
    section = point.get("section") or "General"
    page = point.get("page_number")
    score = point.get("confidence_score", 0)
    text = point.get("text", "")
    evidence = point.get("evidence")

    with st.container():
        # Header row
        h_col1, h_col2, h_col3 = st.columns([1, 4, 1])
        with h_col1:
            st.markdown(f"**#{index}**")
        with h_col2:
            st.markdown(
                f'<span style="background:#e3f2fd;color:#1565c0;padding:0.15rem 0.5rem;'
                f'border-radius:4px;font-size:0.78rem;font-weight:600;">{section}</span>'
                + (f'  📄 Page {page}' if page else ''),
                unsafe_allow_html=True,
            )
        with h_col3:
            st.markdown(f"*{score:.0%}*")

        st.markdown(f"> {text}")

        if evidence:
            with st.expander("📎 View source passage"):
                st.markdown(f"*{evidence[:400]}{'...' if len(evidence) > 400 else ''}*")

        st.markdown("---")
