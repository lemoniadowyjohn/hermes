from __future__ import annotations

from .embeddings import EmbeddingProvider
from .models import SearchHit
from .vector_store import SQLiteVectorStore


class Retriever:
    def __init__(self, embeddings: EmbeddingProvider, store: SQLiteVectorStore, top_k: int = 6):
        self.embeddings = embeddings
        self.store = store
        self.top_k = top_k

    def retrieve(self, query: str) -> list[SearchHit]:
        vector = self.embeddings.embed([query])[0]
        hits = self.store.search(vector, top_k=self.top_k * 2)
        # Prefer active/current evidence, while retaining superseded evidence for stale-revision detection.
        hits.sort(
            key=lambda h: (
                h.chunk.metadata.status.lower() == "active",
                h.score,
            ),
            reverse=True,
        )
        return hits[: self.top_k]
