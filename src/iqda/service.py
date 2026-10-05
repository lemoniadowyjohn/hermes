from __future__ import annotations

import logging
import time
import uuid

from .confidence import compute_confidence
from .llm import LLMProvider
from .models import AnswerResponse, AnswerStatus, Usage
from .persistence import ApprovalStore
from .retrieval import Retriever
from .validation import EvidenceValidator
from .vector_store import SQLiteVectorStore


class QualityAssistantService:
    def __init__(
        self,
        retriever: Retriever,
        llm: LLMProvider,
        store: SQLiteVectorStore,
        approval_store: ApprovalStore,
        confidence_threshold: float = 0.55,
    ):
        self.retriever = retriever
        self.llm = llm
        self.store = store
        self.approval_store = approval_store
        self.confidence_threshold = confidence_threshold
        self.validator = EvidenceValidator()
        self.log = logging.getLogger("iqda.service")

    def ask(self, question: str) -> AnswerResponse:
        start = time.perf_counter()
        request_id = str(uuid.uuid4())
        reasons: list[str] = []
        hard_stop = False
        escalate = False

        component_ids = self.validator.component_ids(question)
        component_id = component_ids[0] if len(component_ids) == 1 else None
        if len(component_ids) > 1:
            hard_stop = True
            reasons.append("multiple_component_ids_ambiguous")
        elif not component_ids:
            hard_stop = True
            reasons.append("component_id_missing_or_ambiguous")
        elif not self.store.metadata_for_component(component_id):
            hard_stop = True
            reasons.append(f"unknown_component_id:{component_id}")

        for doc_id in self.validator.document_ids(question):
            if not self.store.has_document(doc_id):
                hard_stop = True
                reasons.append(f"missing_document:{doc_id}")

        hits = self.retriever.retrieve(question) if not hard_stop else []

        requested_rev = self.validator.requested_revision(question)
        if component_id and requested_rev is not None:
            metadata = self.store.metadata_for_component(component_id)
            active_revs = [m.revision for m in metadata if m.status.lower() == "active" and m.revision is not None]
            if active_revs and requested_rev < max(active_revs):
                hard_stop = True
                reasons.append(f"outdated_revision_requested:{requested_rev}<active:{max(active_revs)}")

        if not hard_stop and component_id:
            q = question.lower()
            field_map = {
                "torque": "Torque requirement",
                "coating": "Coating requirement",
                "dimension": "Inspection dimension",
            }
            for token, field_name in field_map.items():
                if token in q or (token == "dimension" and any(x in q for x in ["measure", "size"])):
                    values = self.validator.requirement_values(hits, field_name, component_id)
                    if len(values) > 1:
                        hard_stop = True
                        escalate = True
                        reasons.append(f"conflicting_active_evidence:{field_name}:{sorted(values)}")

        if hard_stop:
            draft_answer = "I cannot provide a quality requirement from the available evidence."
            response = AnswerResponse(
                question=question,
                answer=draft_answer,
                status=AnswerStatus.escalate if escalate else AnswerStatus.refused,
                confidence=0.0,
                citations=[],
                reasons=reasons,
                missing_information=[],
                retrieval=[],
                request_id=request_id,
                latency_ms=round((time.perf_counter() - start) * 1000, 2),
                usage=Usage(),
            )
            if response.status == AnswerStatus.escalate:
                response.approval_id = self.approval_store.create(question, response)
            self._log(response)
            return response

        draft, usage = self.llm.answer(question, hits)
        citations, citation_errors = self.validator.validate_citations(draft, hits)
        reasons.extend(citation_errors)
        if draft.conflict_detected:
            escalate = True
            reasons.append("llm_reported_conflict")

        confidence = compute_confidence(hits, draft, citation_errors, hard_stop=False, escalate=escalate)

        if citation_errors or not citations:
            status = AnswerStatus.refused
            answer = "I cannot provide a supported answer because citation validation failed."
        elif draft.missing_information:
            status = AnswerStatus.partial
            answer = draft.answer
            reasons.append("partial_evidence")
        elif confidence < self.confidence_threshold:
            status = AnswerStatus.refused
            answer = "I cannot provide a sufficiently supported answer from the retrieved evidence."
            reasons.append("confidence_below_threshold")
        elif escalate:
            status = AnswerStatus.escalate
            answer = draft.answer
        else:
            status = AnswerStatus.answered
            answer = draft.answer

        response = AnswerResponse(
            question=question,
            answer=answer,
            status=status,
            confidence=confidence,
            citations=citations if status in {AnswerStatus.answered, AnswerStatus.partial, AnswerStatus.escalate} else [],
            reasons=reasons,
            missing_information=draft.missing_information,
            retrieval=[
                {
                    "chunk_id": h.chunk.chunk_id,
                    "document_id": h.chunk.document_id,
                    "revision": h.chunk.metadata.revision,
                    "status": h.chunk.metadata.status,
                    "score": round(h.score, 4),
                }
                for h in hits
            ],
            request_id=request_id,
            latency_ms=round((time.perf_counter() - start) * 1000, 2),
            usage=usage,
        )
        if status in {AnswerStatus.partial, AnswerStatus.escalate}:
            response.approval_id = self.approval_store.create(question, response)
        self._log(response)
        return response

    def _log(self, response: AnswerResponse) -> None:
        self.log.info(
            "answer_completed",
            extra={
                "request_id": response.request_id,
                "stage": "answer",
                "latency_ms": response.latency_ms,
                "status": response.status.value,
                "confidence": response.confidence,
            },
        )
