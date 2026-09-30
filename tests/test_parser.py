from iqda.parsing import DocumentParser


def test_parser_extracts_metadata():
    doc = DocumentParser().parse("data/synthetic_docs/QP-AX17-REV2.md")
    assert doc.metadata.document_id == "QP-AX17"
    assert doc.metadata.component_id == "AX17"
    assert doc.metadata.revision == 2
    assert doc.metadata.status == "active"
    assert "Torque requirement" in doc.text
