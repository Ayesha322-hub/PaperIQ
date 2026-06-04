"""
PaperIQ — Embedding Service
Generates vector embeddings for chunks using sentence-transformers.
Model: sentence-transformers/all-MiniLM-L6-v2 (local, offline)

Embeddings are stored as JSON in the database and loaded into NumPy for comparison.
"""

from functools import lru_cache

import numpy as np

from app.config import settings
from app.utils.exceptions import EmbeddingError


@lru_cache(maxsize=1)
def _get_model():
    """Load and cache the embedding model. First call downloads ~80 MB."""
    try:
        from sentence_transformers import SentenceTransformer
        return SentenceTransformer(settings.embedding_model)
    except Exception as exc:
        raise EmbeddingError(
            f"Failed to load embedding model '{settings.embedding_model}': {exc}"
        ) from exc


def embed_text(text: str) -> list[float]:
    """
    Generate a single embedding vector for a text string.
    Returns a Python list of floats (for JSON storage).
    """
    if not text or not text.strip():
        raise EmbeddingError("Cannot embed empty text.")

    try:
        model = _get_model()
        embedding = model.encode(text.strip(), convert_to_numpy=True)
        return embedding.tolist()
    except EmbeddingError:
        raise
    except Exception as exc:
        raise EmbeddingError(f"Embedding failed: {exc}") from exc


def embed_batch(texts: list[str]) -> list[list[float]]:
    """
    Generate embeddings for a list of texts in one efficient batch call.
    Returns a list of embedding vectors.
    """
    if not texts:
        return []

    cleaned = [t.strip() for t in texts if t and t.strip()]
    if not cleaned:
        return []

    try:
        model = _get_model()
        embeddings = model.encode(cleaned, convert_to_numpy=True, batch_size=32)
        return [e.tolist() for e in embeddings]
    except Exception as exc:
        raise EmbeddingError(f"Batch embedding failed: {exc}") from exc


def cosine_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """
    Compute cosine similarity between two embedding vectors.
    Returns a float between -1 and 1 (higher = more similar).
    """
    a = np.array(vec_a, dtype=np.float32)
    b = np.array(vec_b, dtype=np.float32)

    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return float(np.dot(a, b) / (norm_a * norm_b))
