from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Iterable

from .embeddings import EmbeddingProvider, HashEmbeddingProvider, cosine
from .providers import AnswerProvider, DeterministicAnswerProvider


_COMPONENT_RE = re.compile(r"\b[A-Z]{2}\d{2}\b")
_NUMBER_RE = re.compile(r"\b\d+(?:\.\d+)?\s*(?:Nm|mm|%)\b", re.I)


@dataclass(frozen=True)
class Chunk:
    document_id: str
    revision: int
    status: str
    component: str | None
    text: str
    source: str
    start_line: int
    end_line: int


@dataclass(frozen=True)
class RetrievalHit:
    chunk: Chunk
    score: float


@dataclass(frozen=True)
class Answer:
    status: str
    text: str
    confidence: float
    citations: tuple[str, ...]
    reasons: tuple[str, ...]


def _parse_frontmatter(lines: list[str]) -> tuple[dict[str, str], int]:
    if not lines or lines[0].strip() != "---":
        return {}, 0
    meta: dict[str, str] = {}
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            return meta, index + 1
        if ":" in line:
            key, value = line.split(":", 1)
            meta[key.strip().lower()] = value.strip()
    return meta, 0


def load_chunks(paths: Iterable[Path]) -> list[Chunk]:
    chunks: list[Chunk] = []
    for path in paths:
        lines = path.read_text(encoding="utf-8").splitlines()
        meta, body_start = _parse_frontmatter(lines)
        body = lines[body_start:]
        start = None
        buf: list[str] = []
        for offset, line in enumerate(body + [""], start=body_start + 1):
            if line.strip():
                if start is None:
                    start = offset
                buf.append(line)
                continue
            if buf and start is not None:
                text = "\n".join(buf).strip()
                chunks.append(
                    Chunk(
                        document_id=meta.get("document_id", path.stem),
                        revision=int(meta.get("revision", "1")),
                        status=meta.get("status", "active").lower(),
                        component=meta.get("component") or None,
                        text=text,
                        source=path.name,
                        start_line=start,
                        end_line=offset - 1,
                    )
                )
                start, buf = None, []
    return chunks


class RAGService:
    def __init__(
        self,
        chunks: list[Chunk],
        embedding_provider: EmbeddingProvider | None = None,
        answer_provider: AnswerProvider | None = None,
    ) -> None:
        self.embedding_provider = embedding_provider or HashEmbeddingProvider()
        self.answer_provider = answer_provider or DeterministicAnswerProvider()
        self.chunks = self._select_current(chunks)
        self._vectors = self.embedding_provider.embed([c.text for c in self.chunks])

    @classmethod
    def from_directory(cls, directory: str | Path, **kwargs: object) -> "RAGService":
        paths = sorted(Path(directory).glob("*.md"))
        return cls(load_chunks(paths), **kwargs)

    @staticmethod
    def _select_current(chunks: list[Chunk]) -> list[Chunk]:
        active = [c for c in chunks if c.status == "active"]
        latest: dict[tuple[str, str | None], int] = {}
        for chunk in active:
            key = (chunk.document_id, chunk.component)
            latest[key] = max(latest.get(key, 0), chunk.revision)
        return [
            c for c in active
            if c.revision == latest[(c.document_id, c.component)]
        ]

    def retrieve(
        self,
        question: str,
        k: int = 3,
        components: set[str] | None = None,
    ) -> list[RetrievalHit]:
        q = self.embedding_provider.embed([question])[0]
        candidates = (
            (c, v)
            for c, v in zip(self.chunks, self._vectors)
            if not components or c.component in components
        )
        ranked = sorted(
            (
                RetrievalHit(chunk=c, score=cosine(q, v))
                for c, v in candidates
            ),
            key=lambda hit: hit.score,
            reverse=True,
        )
        return [hit for hit in ranked[:k] if hit.score > 0.0]

    def ask(self, question: str) -> Answer:
        requested = set(_COMPONENT_RE.findall(question.upper()))
        known = {c.component for c in self.chunks if c.component}
        unknown = requested - known
        if unknown:
            return Answer(
                "refused",
                "",
                0.0,
                (),
                (f"unknown component: {sorted(unknown)[0]}",),
            )

        hits = self.retrieve(
            question,
            components=requested or None,
        )
        if not hits:
            return Answer("refused", "", 0.0, (), ("insufficient evidence",))

        numeric_facts = {
            fact.lower()
            for h in hits
            for fact in _NUMBER_RE.findall(h.chunk.text)
        }
        if len(numeric_facts) > 1 and any(
            "torque" in h.chunk.text.lower() for h in hits
        ):
            return Answer(
                "escalated",
                "",
                0.0,
                tuple(self._citation(h.chunk) for h in hits),
                ("conflicting active requirements",),
            )

        evidence = [h.chunk.text for h in hits]
        text = self.answer_provider.generate(question, evidence)
        if not text or text == "INSUFFICIENT_EVIDENCE":
            return Answer(
                "refused",
                "",
                0.0,
                tuple(self._citation(h.chunk) for h in hits),
                ("provider found insufficient evidence",),
            )

        confidence = max(0.0, min(1.0, hits[0].score))
        return Answer(
            "answered",
            text,
            confidence,
            tuple(self._citation(h.chunk) for h in hits),
            (),
        )

    @staticmethod
    def _citation(chunk: Chunk) -> str:
        return (
            f"{chunk.source}:L{chunk.start_line}-L{chunk.end_line} "
            f"(rev {chunk.revision})"
        )
