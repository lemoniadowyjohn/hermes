from __future__ import annotations

from .models import AnswerDraft, SearchHit


def compute_confidence(
    hits: list[SearchHit],
    draft: AnswerDraft,
    citation_errors: list[str],
    hard_stop: bool,
    escalate: bool,
) -> float:
    if hard_stop:
        return 0.0
    top_score = max((h.score for h in hits), default=0.0)
    retrieval = max(0.0, min(1.0, (top_score + 0.05) / 0.75))
    requested = len(draft.cited_chunk_ids) + len(draft.missing_information)
    coverage = len(draft.cited_chunk_ids) / requested if requested else 0.0
    citation = 0.0 if citation_errors else (1.0 if draft.cited_chunk_ids else 0.25)
    confidence = 0.45 * retrieval + 0.35 * coverage + 0.20 * citation
    if escalate:
        confidence *= 0.45
    return round(max(0.0, min(1.0, confidence)), 3)
