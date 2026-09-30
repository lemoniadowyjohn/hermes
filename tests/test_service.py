from iqda.models import AnswerStatus


def test_answerable_is_cited(service):
    response = service.ask("What is the torque requirement for component AX17?")
    assert response.status == AnswerStatus.answered
    assert "8.5 ± 0.5 Nm" in response.answer
    assert response.citations
    assert {c.document_id for c in response.citations} == {"QP-AX17"}


def test_partial_goes_to_approval(service):
    response = service.ask("For component AX17, give the torque and coating requirement.")
    assert response.status == AnswerStatus.partial
    assert "coating" in response.missing_information
    assert response.approval_id


def test_unknown_component_refuses(service):
    response = service.ask("What is the torque requirement for component AX71?")
    assert response.status == AnswerStatus.refused
    assert any("unknown_component_id" in r for r in response.reasons)


def test_outdated_revision_refuses(service):
    response = service.ask("According to revision 1, what is the torque requirement for component AX17?")
    assert response.status == AnswerStatus.refused
    assert any("outdated_revision_requested" in r for r in response.reasons)


def test_conflicting_active_docs_escalate(service):
    response = service.ask("What is the torque requirement for component BX42?")
    assert response.status == AnswerStatus.escalate
    assert response.approval_id
    assert any("conflicting_active_evidence" in r for r in response.reasons)
