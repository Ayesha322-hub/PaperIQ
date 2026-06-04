"""
PaperIQ — Summary Page
"""
import streamlit as st
from api_client import APIError, generate_summary

SUMMARY_TYPES = {
    "short":             ("⚡", "Quick Summary",       "3–5 bullet points covering the whole paper"),
    "detailed":          ("📋", "Full Summary",         "One detailed paragraph per section"),
    "section_wise":      ("🗂️", "By Section",           "Summary of every detected section"),
    "key_findings":      ("🔑", "Key Findings",         "Results, Discussion and Conclusion only"),
    "beginner_friendly": ("🎓", "Simple Explanation",   "Plain language for non-experts"),
}


def render():
    paper_id = st.session_state.get("paper_id")
    if not paper_id:
        st.warning("No paper loaded. Please upload a paper first.")
        return

    detail = st.session_state.get("paper_detail") or {}
    title = detail.get("title") or "Untitled Paper"

    st.markdown(f"""
    <div class="piq-hero">
        <h1>📝 <span class="accent">Summaries</span></h1>
        <p>{title}</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="piq-section-title">Choose Summary Type</div>', unsafe_allow_html=True)
    cols = st.columns(len(SUMMARY_TYPES))
    selected_type = st.session_state.get("selected_summary_type", "short")

    for i, (key, (icon, label, desc)) in enumerate(SUMMARY_TYPES.items()):
        with cols[i]:
            is_selected = selected_type == key
            if st.button(
                f"{icon}  {label}",
                key=f"sum_btn_{key}",
                use_container_width=True,
                type="primary" if is_selected else "secondary",
                help=desc,
            ):
                st.session_state.selected_summary_type = key
                st.rerun()

    selected_type = st.session_state.get("selected_summary_type", "short")
    icon, label, desc = SUMMARY_TYPES[selected_type]
    st.markdown(f'<div style="color:#94a3b8;font-size:0.85rem;margin:0.5rem 0 1rem;">{icon} <strong style="color:#a78bfa;">{label}</strong> — {desc}</div>', unsafe_allow_html=True)
    st.divider()

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

    result = st.session_state[cache_key]
    points = result.get("summary_points", [])

    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f'<div class="piq-section-title">{icon} {label}</div>', unsafe_allow_html=True)
    with col2:
        if st.button("🔄  Regenerate"):
            del st.session_state[cache_key]
            st.rerun()

    if not points:
        st.info("No summary points were generated. The paper may be too short.")
        return

    st.markdown(f'<div style="color:#64748b;font-size:0.85rem;margin-bottom:1rem;">{len(points)} point{"s" if len(points) != 1 else ""} generated</div>', unsafe_allow_html=True)

    for i, point in enumerate(points, 1):
        _render_summary_point(i, point)

    st.divider()
    st.markdown('<div class="piq-section-title">📋 Export as Text</div>', unsafe_allow_html=True)
    full_text = "\n\n".join(
        f"{i}. [{p.get('section', 'General')}] {p['text']}"
        for i, p in enumerate(points, 1)
    )
    st.text_area("Select all and copy", full_text, height=180, label_visibility="collapsed")


def _render_summary_point(index: int, point: dict):
    section = point.get("section") or "General"
    page = point.get("page_number")
    score = point.get("confidence_score", 0)
    text = point.get("text", "")
    evidence = point.get("evidence")

    page_str = f"· Page {page}" if page else ""
    score_str = f"{score:.0%}" if score else ""

    st.markdown(f"""
    <div class="summary-point">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.5rem;">
            <div>
                <span style="color:#64748b;font-weight:700;font-size:0.85rem;">#{index}</span>
                &nbsp;
                <span class="section-tag">{section}</span>
                &nbsp;
                <span style="color:#64748b;font-size:0.8rem;">{page_str}</span>
            </div>
            <span style="color:#a78bfa;font-size:0.8rem;font-weight:600;">{score_str}</span>
        </div>
        <div style="color:#cbd5e1;line-height:1.6;">{text}</div>
    </div>
    """, unsafe_allow_html=True)

    if evidence:
        with st.expander("📎 View source passage"):
            st.markdown(f'<div style="color:#94a3b8;font-style:italic;font-size:0.88rem;">{evidence[:400]}{"..." if len(evidence) > 400 else ""}</div>', unsafe_allow_html=True)
