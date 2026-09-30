from __future__ import annotations

import re
from dataclasses import dataclass, field

from .models import AnswerDraft, Citation, SearchHit


COMPONENT_RE = re.compile(r"\b[A-Z]{2}\d{2}\b")
DOC_RE = re.compile(r"\b(?:QP|WI|INSP)-[A-Z0-9-]+\b", re.I)
REV_RE = re.compile(r"\brevision\s*(\d+)\b", re.I)


@dataclass
class GateResult:
    hard_stop: bool = False
    escalate: bool = False
    reasons: list[str] = field(default_factory=list)


class EvidenceValidator:
    def validate_citations(self, draft: AnswerDraft, hits: list[SearchHit]) -> tuple[list[Citation], list[str]]:
        by_id = {h.chunk.chunk_id: h.chunk for h in hits}
        reasons: list[str] = []
        citations: list[Citation] = []
        seen = set()
        for chunk_id in draft.cited_chunk_ids:
            if chunk_id in seen:
                continue
            seen.add(chunk_id)
            chunk = by_id.get(chunk_id)
            if not chunk:
                reasons.append(f"citation_not_retrieved:{chunk_id}")
                continue
            citations.append(
                Citation(
                    chunk_id=chunk.chunk_id,
                    document_id=chunk.document_id,
                    revision=chunk.metadata.revision,
                    section=chunk.section,
                    source_path=chunk.metadata.source_path,
                    excerpt=chunk.text[:280].replace("\n", " "),
                )
            )
        if draft.answer and not draft.answer.lower().startswith("insufficient") and not citations:
            reasons.append("answer_without_valid_citation")
        return citations, reasons

    @staticmethod
    def component_ids(question: str) -> list[str]:
        return COMPONENT_RE.findall(question.upper())

    @staticmethod
    def document_ids(question: str) -> list[str]:
        return [x.upper() for x in DOC_RE.findall(question.upper())]

    @staticmethod
    def requested_revision(question: str) -> int | None:
        m = REV_RE.search(question)
        return int(m.group(1)) if m else None

    @staticmethod
    def requirement_values(hits: list[SearchHit], field_name: str, component_id: str | None) -> set[str]:
        pattern = re.compile(rf"^{re.escape(field_name)}:\s*(.+)$", re.I | re.M)
        values: set[str] = set()
        for hit in hits:
            md = hit.chunk.metadata
            if md.status.lower() != "active":
                continue
            if component_id and md.component_id != component_id:
                continue
            m = pattern.search(hit.chunk.text)
            if m:
                values.add(m.group(1).strip())
        return values
