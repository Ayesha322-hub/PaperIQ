"""
PaperIQ — Summarizer Service
Generates summaries using a local HuggingFace model.
Model: sshleifer/distilbart-cnn-12-6 (offline, no API key needed)

IMPORTANT: The model is loaded once and cached. First call takes ~30 seconds.
Subsequent calls are fast.
"""

from functools import lru_cache

from app.config import settings
from app.utils.exceptions import SummarizationError

# Minimum input length before we bother summarising
MIN_INPUT_CHARS = 200

# ── Model loader (cached) ─────────────────────────────────────────────────────

@lru_cache(maxsize=1)
def _get_summarizer():
    """Load and cache the summarisation pipeline. Thread-safe via lru_cache."""
    try:
        from transformers import pipeline
        return pipeline(
            task="summarization",
            model=settings.summarization_model,
        )
    except Exception as exc:
        raise SummarizationError(
            f"Failed to load summarisation model '{settings.summarization_model}': {exc}"
        ) from exc


# ── Core summarisation ────────────────────────────────────────────────────────

def summarize_chunk(text: str) -> str:
    """
    Summarise a single text chunk.
    Returns the original text if it's too short to summarise.
    """
    cleaned = text.strip()

    if len(cleaned) < MIN_INPUT_CHARS:
        return cleaned

    try:
        summarizer = _get_summarizer()
        result = summarizer(
            cleaned,
            max_length=160,
            min_length=40,
            do_sample=False,
            truncation=True,
        )
        return result[0]["summary_text"].strip()
    except Exception as exc:
        raise SummarizationError(f"Summarisation failed: {exc}") from exc


def generate_short_summary(sections: list[dict]) -> list[dict]:
    """
    Generate a short summary: one bullet point per major section.

    Returns a list of summary point dicts:
        {
            "text": str,
            "section": str,
            "page_number": int,
            "confidence_score": float,
            "evidence": str,
        }
    """
    # Sections to prioritise for short summary
    priority_sections = {
        "abstract", "introduction", "results",
        "conclusion", "conclusions", "findings",
        "key findings",
    }

    points: list[dict] = []

    for section in sections:
        name_lower = section["section_name"].lower()

        # For short summary, skip References, Appendix, etc.
        if name_lower in {"references", "bibliography", "appendix", "keywords"}:
            continue

        text = section["section_text"]
        if not text or len(text.split()) < 30:
            continue

        # Prioritise abstract and conclusion — always include
        is_priority = any(p in name_lower for p in priority_sections)

        if not is_priority and len(points) >= 5:
            continue

        summary_text = summarize_chunk(text[:3000])  # cap input

        points.append(
            {
                "text": summary_text,
                "section": section["section_name"],
                "page_number": section["start_page"],
                "confidence_score": 0.85 if is_priority else 0.70,
                "evidence": text[:300].strip() + "...",
            }
        )

    return points


def generate_detailed_summary(sections: list[dict]) -> list[dict]:
    """
    Generate one detailed summary point per section.
    """
    points: list[dict] = []

    for section in sections:
        text = section["section_text"]
        if not text or len(text.split()) < 20:
            continue

        summary_text = summarize_chunk(text[:4000])

        points.append(
            {
                "text": summary_text,
                "section": section["section_name"],
                "page_number": section["start_page"],
                "confidence_score": 0.80,
                "evidence": text[:400].strip() + "...",
            }
        )

    return points


def generate_section_wise_summary(sections: list[dict]) -> list[dict]:
    """
    Generate a summary for every detected section, including smaller ones.
    """
    return generate_detailed_summary(sections)


def generate_key_findings(sections: list[dict]) -> list[dict]:
    """
    Focus only on Results, Discussion, Findings, and Conclusion sections.
    """
    focus_keywords = {
        "result", "discussion", "finding", "conclusion",
        "evaluation", "analysis", "outcome",
    }
    filtered = [
        s for s in sections
        if any(kw in s["section_name"].lower() for kw in focus_keywords)
    ]

    if not filtered:
        filtered = sections  # fallback to all sections

    return generate_detailed_summary(filtered)


def generate_beginner_friendly(sections: list[dict], paper_title: str | None = None) -> list[dict]:
    """
    Generate plain-language summaries suitable for students unfamiliar with the topic.
    Uses the same model but with a prompt prefix to guide simpler output.
    """
    priority_sections = {
        "abstract", "introduction", "conclusion", "conclusions",
        "results", "findings",
    }

    points: list[dict] = []

    for section in sections:
        name_lower = section["section_name"].lower()
        if not any(p in name_lower for p in priority_sections):
            continue

        text = section["section_text"]
        if not text or len(text.split()) < 20:
            continue

        # Add a simplification hint in the input
        prefixed = f"Explain in simple terms: {text[:2000]}"
        summary_text = summarize_chunk(prefixed)

        points.append(
            {
                "text": summary_text,
                "section": section["section_name"],
                "page_number": section["start_page"],
                "confidence_score": 0.75,
                "evidence": text[:300].strip() + "...",
            }
        )

    return points


# ── Dispatcher ────────────────────────────────────────────────────────────────

def generate_summary(
    summary_type: str,
    sections: list[dict],
    paper_title: str | None = None,
) -> list[dict]:
    """
    Dispatch to the correct summary generator based on summary_type.

    summary_type values:
        short | detailed | section_wise | key_findings | beginner_friendly
    """
    dispatch = {
        "short": generate_short_summary,
        "detailed": generate_detailed_summary,
        "section_wise": generate_section_wise_summary,
        "key_findings": generate_key_findings,
    }

    if summary_type == "beginner_friendly":
        return generate_beginner_friendly(sections, paper_title)

    func = dispatch.get(summary_type)
    if not func:
        raise SummarizationError(
            f"Unknown summary type: '{summary_type}'. "
            "Valid types: short, detailed, section_wise, key_findings, beginner_friendly."
        )

    return func(sections)
