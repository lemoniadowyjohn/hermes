from __future__ import annotations

from .chunking import SectionChunker
from .config import Settings
from .embeddings import HashEmbeddingProvider, OpenAIEmbeddingProvider
from .llm import ExtractiveQualityLLM, OpenAIResponsesLLM
from .parsing import DocumentParser
from .persistence import ApprovalStore
from .retrieval import Retriever
from .service import QualityAssistantService
from .vector_store import SQLiteVectorStore


def build_components(settings: Settings):
    settings.validate()
    store = SQLiteVectorStore(settings.db_path)
    if settings.mode == "openai":
        embeddings = OpenAIEmbeddingProvider(settings.openai_api_key or "", settings.openai_embedding_model)
        llm = OpenAIResponsesLLM(settings.openai_api_key or "", settings.openai_model)
    else:
        embeddings = HashEmbeddingProvider()
        llm = ExtractiveQualityLLM()
    retriever = Retriever(embeddings, store, settings.top_k)
    approvals = ApprovalStore(settings.db_path)
    service = QualityAssistantService(retriever, llm, store, approvals, settings.confidence_threshold)
    return service, store, embeddings, approvals


def rebuild_index(settings: Settings) -> int:
    service, store, embeddings, _ = build_components(settings)
    parser = DocumentParser()
    chunker = SectionChunker()
    docs = parser.parse_directory(settings.docs_dir)
    chunks = [chunk for doc in docs for chunk in chunker.chunk(doc)]
    vectors = embeddings.embed([c.text for c in chunks])
    store.clear()
    store.upsert(chunks, vectors, embeddings.name)
    return len(chunks)
