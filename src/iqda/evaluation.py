from __future__ import annotations

import json
from pathlib import Path
from statistics import mean

from .models import AnswerResponse, AnswerStatus, EvalCase
from .service import QualityAssistantService


def _rate(rows: list[dict], field: str, eligible_field: str | None = None) -> tuple[float | None, int]:
    eligible = [r for r in rows if eligible_field is None or r[eligible_field]]
    if not eligible:
        return None, 0
    return sum(bool(r[field]) for r in eligible) / len(eligible), len(eligible)


def run_evaluation(service: QualityAssistantService, cases_path: str | Path) -> dict:
    raw = json.loads(Path(cases_path).read_text(encoding="utf-8"))
    cases = [EvalCase.model_validate(item) for item in raw]
    rows = []
    for case in cases:
        response = service.ask(case.question)
        retrieved_doc_ids = {r["document_id"] for r in response.retrieval}
        cited_doc_ids = {c.document_id for c in response.citations}

        retrieval_eligible = bool(case.expected_doc_ids)
        retrieval_hit = all(doc in retrieved_doc_ids for doc in case.expected_doc_ids) if retrieval_eligible else None

        citation_eligible = bool(case.expected_doc_ids) and case.expected_status in {AnswerStatus.answered, AnswerStatus.partial}
        citation_correct = (
            bool(response.citations)
            and cited_doc_ids.issubset(set(case.expected_doc_ids))
            and bool(cited_doc_ids.intersection(case.expected_doc_ids))
            if citation_eligible
            else None
        )

        factual_eligible = bool(case.expected_answer_contains)
        factual = (
            all(token.lower() in response.answer.lower() for token in case.expected_answer_contains)
            if factual_eligible
            else None
        )

        refusal_expected = case.expected_status in {AnswerStatus.refused, AnswerStatus.escalate}
        refusal_actual = response.status in {AnswerStatus.refused, AnswerStatus.escalate}
        refusal_correct = refusal_expected == refusal_actual
        structured_valid = bool(AnswerResponse.model_validate(response.model_dump()))
        status_correct = response.status == case.expected_status
        rows.append(
            {
                "id": case.id,
                "category": case.category,
                "status_expected": case.expected_status.value,
                "status_actual": response.status.value,
                "status_correct": status_correct,
                "retrieval_eligible": retrieval_eligible,
                "retrieval_hit": retrieval_hit,
                "citation_eligible": citation_eligible,
                "citation_correct": citation_correct,
                "factual_eligible": factual_eligible,
                "factual_consistency": factual,
                "refusal_correct": refusal_correct,
                "structured_valid": structured_valid,
                "latency_ms": response.latency_ms,
                "usage": response.usage.model_dump(),
                "reasons": response.reasons,
            }
        )

    n = len(rows) or 1
    retrieval_rate, retrieval_n = _rate(rows, "retrieval_hit", "retrieval_eligible")
    citation_rate, citation_n = _rate(rows, "citation_correct", "citation_eligible")
    factual_rate, factual_n = _rate(rows, "factual_consistency", "factual_eligible")
    summary = {
        "cases": len(rows),
        "status_accuracy": sum(r["status_correct"] for r in rows) / n,
        "retrieval_hit_rate": retrieval_rate,
        "retrieval_cases": retrieval_n,
        "citation_correctness": citation_rate,
        "citation_cases": citation_n,
        "factual_consistency": factual_rate,
        "factual_cases": factual_n,
        "refusal_correctness": sum(r["refusal_correct"] for r in rows) / n,
        "structured_output_validity": sum(r["structured_valid"] for r in rows) / n,
        "mean_latency_ms": round(mean(r["latency_ms"] for r in rows), 2) if rows else 0.0,
        "token_usage_available": any(r["usage"].get("total_tokens") is not None for r in rows),
    }
    return {"summary": summary, "cases": rows}
