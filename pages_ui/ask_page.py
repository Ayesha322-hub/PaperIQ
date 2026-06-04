"""
PaperIQ — Ask Questions Page
"""
import streamlit as st
from api_client import APIError, ask_question

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

    st.markdown(f"""
    <div class="piq-hero">
        <h1>💬 Ask <span class="accent">Questions</span></h1>
        <p>{title}</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="piq-section-title">💡 Suggested Questions</div>', unsafe_allow_html=True)
    st.markdown('<div style="color:#94a3b8;font-size:0.85rem;margin-bottom:0.8rem;">Click any question to ask it instantly</div>', unsafe_allow_html=True)

    cols = st.columns(3)
    for i, q in enumerate(SUGGESTED_QUESTIONS):
        with cols[i % 3]:
            if st.button(q, key=f"sugg_{i}", use_container_width=True):
                st.session_state.pending_question = q
                st.rerun()

    st.divider()

    st.markdown('<div class="piq-section-title">✍️ Your Question</div>', unsafe_allow_html=True)
    default_q = st.session_state.pop("pending_question", "")

    question = st.text_input(
        "Ask anything about the paper",
        value=default_q,
        placeholder="e.g. What dataset was used? What were the key results?",
        max_chars=500,
        label_visibility="collapsed",
    )

    if st.button("🔍  Get Answer", type="primary", use_container_width=True, disabled=not question.strip()):
        if len(question.strip()) < 3:
            st.warning("Please enter a longer question (at least 3 characters).")
        else:
            with st.spinner("Searching paper for relevant passages..."):
                try:
                    result = ask_question(paper_id, question.strip())
                    history = st.session_state.get("qa_history", [])
                    history.insert(0, {"question": question.strip(), "result": result})
                    st.session_state.qa_history = history[:10]
                    st.rerun()
                except APIError as e:
                    st.error(f"❌ {e.detail}")

    history = st.session_state.get("qa_history", [])
    if history:
        st.divider()
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f'<div class="piq-section-title">🗂️ Answers ({len(history)})</div>', unsafe_allow_html=True)
        with col2:
            if st.button("🗑️  Clear"):
                st.session_state.qa_history = []
                st.rerun()

        for i, item in enumerate(history):
            _render_qa_item(i, item["question"], item["result"])


def _render_qa_item(index: int, question: str, result: dict):
    answer = result.get("answer", "")
    evidence_list = result.get("evidence", [])

    st.markdown(f"""
    <div class="piq-card" style="margin-bottom:0.5rem;">
        <div style="color:#a78bfa;font-size:0.78rem;font-weight:600;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:0.4rem;">Question</div>
        <div style="color:#e2e8f0;font-weight:600;">{question}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="piq-card">
        <div style="color:#a78bfa;font-size:0.78rem;font-weight:600;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:0.4rem;">Answer</div>
        <div style="color:#cbd5e1;line-height:1.7;">{answer}</div>
    </div>
    """, unsafe_allow_html=True)

    if evidence_list:
        with st.expander(f"📎 {len(evidence_list)} supporting passage{'s' if len(evidence_list) != 1 else ''}"):
            for ev in evidence_list:
                section = ev.get("section") or "Unknown"
                page = ev.get("page_number")
                score = ev.get("similarity_score", 0)
                text = ev.get("text", "")

                st.markdown(f"""
                <div class="evidence-card">
                    <div class="meta">📍 {section}{f" · Page {page}" if page else ""}
                    <span class="score" style="float:right;">Match: {score:.0%}</span></div>
                    <div>{text[:400]}{"..." if len(text) > 400 else ""}</div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.markdown('<div style="color:#64748b;font-size:0.85rem;margin-bottom:0.5rem;">No supporting passages found.</div>', unsafe_allow_html=True)

    st.markdown('<hr style="border-color:rgba(139,92,246,0.1);margin:1rem 0;">', unsafe_allow_html=True)
