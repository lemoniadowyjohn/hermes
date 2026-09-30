from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI
from pydantic import BaseModel

from .core import RAGService
from .embeddings import OpenAIEmbeddingProvider
from .providers import OpenAIAnswerProvider


class AskRequest(BaseModel):
    question: str


def build_service() -> RAGService:
    data_dir = Path(os.getenv("IQDA_DATA_DIR", "data/synthetic_docs"))
    if os.getenv("IQDA_MODE", "offline").lower() == "openai":
        return RAGService.from_directory(
            data_dir,
            embedding_provider=OpenAIEmbeddingProvider(
                os.getenv("IQDA_EMBEDDING_MODEL", "text-embedding-3-small")
            ),
            answer_provider=OpenAIAnswerProvider(
                os.getenv("IQDA_MODEL", "gpt-5-mini")
            ),
        )
    return RAGService.from_directory(data_dir)


app = FastAPI(
    title="Industrial Quality Documentation Assistant",
    version="0.1.0",
)
_service = build_service()


@app.get("/health")
def health() -> dict[str, object]:
    return {
        "status": "ok",
        "mode": os.getenv("IQDA_MODE", "offline"),
        "chunks": len(_service.chunks),
    }


@app.post("/ask")
def ask(request: AskRequest) -> dict[str, object]:
    answer = _service.ask(request.question)
    return {
        "status": answer.status,
        "answer": answer.text,
        "confidence": answer.confidence,
        "citations": answer.citations,
        "reasons": answer.reasons,
    }
