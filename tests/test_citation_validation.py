from iqda.models import AnswerDraft
from iqda.validation import EvidenceValidator


def test_fabricated_citation_is_rejected(service):
    hits = service.retriever.retrieve("AX17 torque")
    draft = AnswerDraft(
        answer="Torque is 8.5 Nm",
        cited_chunk_ids=["fabricated::chunk"],
        missing_information=[],
        rationale="test",
    )
    citations, errors = EvidenceValidator().validate_citations(draft, hits)
    assert not citations
    assert errors
    assert errors[0].startswith("citation_not_retrieved")
