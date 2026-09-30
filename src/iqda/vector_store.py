from __future__ import annotations

import json
import sqlite3
from pathlib import Path
import numpy as np

from .models import Chunk, DocumentMetadata, SearchHit


class SQLiteVectorStore:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_schema(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS chunks (
                    chunk_id TEXT PRIMARY KEY,
                    document_id TEXT NOT NULL,
                    text TEXT NOT NULL,
                    start_line INTEGER NOT NULL,
                    end_line INTEGER NOT NULL,
                    section TEXT,
                    metadata_json TEXT NOT NULL,
                    embedding BLOB NOT NULL,
                    dim INTEGER NOT NULL,
                    embedding_model TEXT NOT NULL
                )
                """
            )
            conn.execute("CREATE INDEX IF NOT EXISTS idx_chunks_document_id ON chunks(document_id)")

    def clear(self) -> None:
        with self._connect() as conn:
            conn.execute("DELETE FROM chunks")

    def upsert(self, chunks: list[Chunk], embeddings: np.ndarray, embedding_model: str) -> None:
        if len(chunks) != len(embeddings):
            raise ValueError("chunks and embeddings length mismatch")
        rows = []
        for chunk, vector in zip(chunks, embeddings, strict=True):
            vec = np.asarray(vector, dtype=np.float32)
            rows.append(
                (
                    chunk.chunk_id,
                    chunk.document_id,
                    chunk.text,
                    chunk.start_line,
                    chunk.end_line,
                    chunk.section,
                    chunk.metadata.model_dump_json(),
                    vec.tobytes(),
                    int(vec.size),
                    embedding_model,
                )
            )
        with self._connect() as conn:
            conn.executemany(
                """
                INSERT INTO chunks VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(chunk_id) DO UPDATE SET
                    document_id=excluded.document_id,
                    text=excluded.text,
                    start_line=excluded.start_line,
                    end_line=excluded.end_line,
                    section=excluded.section,
                    metadata_json=excluded.metadata_json,
                    embedding=excluded.embedding,
                    dim=excluded.dim,
                    embedding_model=excluded.embedding_model
                """,
                rows,
            )

    def search(self, query_vector: np.ndarray, top_k: int = 6) -> list[SearchHit]:
        q = np.asarray(query_vector, dtype=np.float32).reshape(-1)
        with self._connect() as conn:
            rows = conn.execute("SELECT * FROM chunks").fetchall()
        if not rows:
            return []
        compatible = [r for r in rows if r["dim"] == q.size]
        if not compatible:
            raise ValueError("Query embedding dimension does not match indexed embeddings")
        matrix = np.vstack([np.frombuffer(r["embedding"], dtype=np.float32) for r in compatible])
        q_norm = np.linalg.norm(q)
        m_norm = np.linalg.norm(matrix, axis=1)
        denom = np.maximum(m_norm * max(q_norm, 1e-12), 1e-12)
        scores = matrix @ q / denom
        order = np.argsort(scores)[::-1][:top_k]
        hits = []
        for idx in order:
            r = compatible[int(idx)]
            metadata = DocumentMetadata.model_validate_json(r["metadata_json"])
            chunk = Chunk(
                chunk_id=r["chunk_id"],
                document_id=r["document_id"],
                text=r["text"],
                start_line=r["start_line"],
                end_line=r["end_line"],
                section=r["section"],
                metadata=metadata,
            )
            hits.append(SearchHit(chunk=chunk, score=float(scores[int(idx)])))
        return hits

    def all_metadata(self) -> list[DocumentMetadata]:
        with self._connect() as conn:
            rows = conn.execute("SELECT DISTINCT metadata_json FROM chunks").fetchall()
        return [DocumentMetadata.model_validate_json(r[0]) for r in rows]

    def has_document(self, document_id: str) -> bool:
        with self._connect() as conn:
            row = conn.execute("SELECT 1 FROM chunks WHERE document_id=? LIMIT 1", (document_id,)).fetchone()
        return row is not None

    def metadata_for_component(self, component_id: str) -> list[DocumentMetadata]:
        return [m for m in self.all_metadata() if m.component_id == component_id]
