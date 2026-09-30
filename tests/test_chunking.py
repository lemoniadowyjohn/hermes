from iqda.chunking import SectionChunker
from iqda.parsing import DocumentParser


def test_chunker_preserves_provenance():
    doc = DocumentParser().parse("data/synthetic_docs/QP-AX17-REV2.md")
    chunks = SectionChunker(max_chars=500).chunk(doc)
    assert chunks
    assert all(c.document_id == "QP-AX17" for c in chunks)
    assert all(c.start_line <= c.end_line for c in chunks)
    assert any(c.section == "Assembly requirement" for c in chunks)
