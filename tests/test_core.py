from pathlib import Path

from iqda.core import RAGService


DATA = Path(__file__).parents[1] / "data" / "synthetic_docs"


def test_answer_contains_supported_requirement_and_citation():
    service = RAGService.from_directory(DATA)
    result = service.ask("What is the tightening torque for component AX17?")
    assert result.status == "answered"
    assert "32 Nm" in result.text
    assert result.citations


def test_unknown_component_refuses():
    service = RAGService.from_directory(DATA)
    result = service.ask("What is the torque for component ZZ99?")
    assert result.status == "refused"
    assert "unknown component" in result.reasons[0]


def test_superseded_revision_is_not_used():
    service = RAGService.from_directory(DATA)
    assert all(chunk.status == "active" for chunk in service.chunks)
    assert all("28 Nm" not in chunk.text for chunk in service.chunks)
