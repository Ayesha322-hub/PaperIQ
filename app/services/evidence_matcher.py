"""
PaperIQ — Evidence Matcher Service
Finds the most relevant chunks for a query using cosine similarity.
Used by both the /ask endpoint and the /summaries endpoint for evidence passages.
"""

from app.services.embedding_service import cosine_similarity, embed_text
from app.utils.exceptions import EmbeddingError


def find_relevant_chunks(
    query: str,
    chunks: list[dict],
    limit: int = 3,
    min_score: float = 0.2,
) -> list[dict]:
    """
    Return the top-K most relevant chunks for a query.

    Each chunk dict must have:
        - "chunk_text": str
        - "section_name": str
        - "page_number": int
        - "embedding": list[float] | None  (pre-computed, or computed on the fly)

    Returns chunks sorted by similarity score (highest first), with
    "similarity_score" added to each result dict.

    Args:
        query:     The user's question or search text.
        chunks:    List of chunk dicts (from the database).
        limit:     Maximum number of results to return.
        min_score: Minimum similarity score threshold.
    """
    if not chunks or not query.strip():
        return []

    try:
        query_embedding = embed_text(query)
    except EmbeddingError:
        return []

    scored: list[tuple[float, dict]] = []

    for chunk in chunks:
        chunk_embedding = chunk.get("embedding")

        # Compute on the fly if not pre-stored
        if not chunk_embedding:
            try:
                chunk_embedding = embed_text(chunk.get("chunk_text", ""))
            except EmbeddingError:
                continue

        score = cosine_similarity(query_embedding, chunk_embedding)

        if score >= min_score:
            scored.append((score, chunk))

    # Sort by score descending
    scored.sort(key=lambda x: x[0], reverse=True)

    results = []
    for score, chunk in scored[:limit]:
        results.append(
            {
                **chunk,
                "similarity_score": round(score, 4),
            }
        )

    return results


def answer_question(
    question: str,
    chunks: list[dict],
    top_k: int = 3,
) -> dict:
    """
    Retrieve the most relevant passages and compose a simple answer.

    For the MVP, the "answer" is the top matching chunk's text.
    This can be upgraded to a generative QA model later.

    Returns:
        {
            "answer": str,
            "evidence": list[dict],
        }
    """
    relevant = find_relevant_chunks(query=question, chunks=chunks, limit=top_k)

    if not relevant:
        return {
            "answer": (
                "No relevant passages were found in this paper for your question. "
                "Try rephrasing or asking about a different topic."
            ),
            "evidence": [],
        }

    # Use the highest-scoring chunk as the answer
    top_chunk = relevant[0]
    answer_text = top_chunk.get("chunk_text", "").strip()

    # Truncate very long answers
    if len(answer_text) > 800:
        answer_text = answer_text[:800] + "..."

    evidence = [
        {
            "section": chunk.get("section_name"),
            "page_number": chunk.get("page_number"),
            "text": chunk.get("chunk_text", "")[:500],
            "similarity_score": chunk.get("similarity_score", 0.0),
        }
        for chunk in relevant
    ]

    return {
        "answer": answer_text,
        "evidence": evidence,
    }
