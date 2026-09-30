from iqda.chunking import SectionChunker
from iqda.embeddings import HashEmbeddingProvider
from iqda.parsing import DocumentParser
from iqda.vector_store import SQLiteVectorStore


def test_vector_store_persists_and_searches(tmp_path):
    doc = DocumentParser().parse("data/synthetic_docs/QP-AX17-REV2.md")
    chunks = SectionChunker().chunk(doc)
    embed = HashEmbeddingProvider()
    vectors = embed.embed([c.text for c in chunks])
    store = SQLiteVectorStore(tmp_path / "v.db")
    store.upsert(chunks, vectors, embed.name)
    query = embed.embed(["AX17 torque requirement"])[0]
    hits = store.search(query, top_k=3)
    assert hits
    assert hits[0].chunk.document_id == "QP-AX17"
