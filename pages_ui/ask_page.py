"""
PaperIQ — Ask Questions Page
"""

import streamlit as st
from api_client import APIError, ask_question

# Suggested starter questions
SUGGESTED_QUESTIONS = [
    "What is the main objective of this study?",
    "What dataset did the researchers use?",
    "What methods or algorithms were applied?",
    "What were the main results and accuracy?",
    "What are the limitations of this study?",
    "What future work do the authors suggest?",
]


def render():
    paper_id = st.session_state.get("paper_id")
    if not paper_id:
        st.warning("No paper loaded. Please upload a paper first.")
        return

    detail = st.session_state.get("paper_detail") or {}
    title = detail.get("title") or "Untitled Paper"

    st.markdown("## 💬 Ask Questions")
    st.markdown(f"**Paper:** {title}")
    st.divider()

    # ── Suggested questions ───────────────────────────────────────────────────
    st.markdown("### 💡 Suggested Questions")
    st.caption("Click any question to ask it, or type your own below.")

    cols = st.columns(3)
    for i, q in enumerate(SUGGESTED_QUESTIONS):
        with cols[i % 3]:
            if st.button(q, key=f"sugg_{i}", use_container_width=True):
                st.session_state.pending_question = q
                st.rerun()

    st.divider()

    # ── Question input ────────────────────────────────────────────────────────
    st.markdown("### ✍️ Your Question")
    default_q = st.session_state.pop("pending_question", "")

    question = st.text_input(
        "Ask anything about the paper",
        value=default_q,
        placeholder="e.g. What dataset was used? What were the key results?",
        max_chars=500,
    )

    if st.button("🔍 Get Answer", type="primary", use_container_width=True, disabled=not question.strip()):
        if len(question.strip()) < 3:
            st.warning("Please enter a longer question (at least 3 characters).")
        else:
            with st.spinner("Searching paper for relevant passages..."):
                try:
                    result = ask_question(paper_id, question.strip())
                    # Prepend to history
                    history = st.session_state.get("qa_history", [])
                    history.insert(0, {"question": question.strip(), "result": result})
                    st.session_state.qa_history = history[:10]  # keep last 10
                    st.rerun()
                except APIError as e:
                    st.error(f"❌ {e.detail}")

    # ── Q&A History ───────────────────────────────────────────────────────────
    history = st.session_state.get("qa_history", [])

    if history:
        st.divider()

        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"### 🗂️ Answers ({len(history)})")
        with col2:
            if st.button("🗑️ Clear History"):
                st.session_state.qa_history = []
                st.rerun()

        for i, item in enumerate(history):
            _render_qa_item(i, item["question"], item["result"])


def _render_qa_item(index: int, question: str, result: dict):
    answer = result.get("answer", "")
    evidence_list = result.get("evidence", [])

    with st.container():
        # Question
        st.markdown(
            f'<div style="background:#f0f4ff;padding:0.7rem 1rem;border-radius:8px;'
            f'margin-bottom:0.5rem;"><strong>Q: {question}</strong></div>',
            unsafe_allow_html=True,
        )

        # Answer
        st.markdown(f"**Answer:** {answer}")

        # Evidence
        if evidence_list:
            with st.expander(f"📎 {len(evidence_list)} supporting passage{'s' if len(evidence_list) != 1 else ''}"):
                for ev in evidence_list:
                    section = ev.get("section") or "Unknown"
                    page = ev.get("page_number")
                    score = ev.get("similarity_score", 0)
                    text = ev.get("text", "")

                    st.markdown(
                        f'<div class="evidence-card">'
                        f'<div class="meta">📍 {section}'
                        + (f' · Page {page}' if page else '')
                        + f'<span class="score" style="float:right">Match: {score:.0%}</span></div>'
                        f'<div>{text[:400]}{"..." if len(text) > 400 else ""}</div>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )
        else:
            st.caption("No supporting passages found.")

        st.markdown("---")
