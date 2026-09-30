from __future__ import annotations

from abc import ABC, abstractmethod
import httpx
import numpy as np
from sklearn.feature_extraction.text import HashingVectorizer


class EmbeddingProvider(ABC):
    name: str

    @abstractmethod
    def embed(self, texts: list[str]) -> np.ndarray:
        raise NotImplementedError


class HashEmbeddingProvider(EmbeddingProvider):
    """Deterministic offline baseline for tests/dev; not a semantic production model."""

    name = "hashing-vectorizer-dev"

    def __init__(self, n_features: int = 4096):
        self.vectorizer = HashingVectorizer(
            n_features=n_features,
            alternate_sign=False,
            norm="l2",
            ngram_range=(1, 2),
            lowercase=True,
        )

    def embed(self, texts: list[str]) -> np.ndarray:
        if not texts:
            return np.empty((0, self.vectorizer.n_features), dtype=np.float32)
        matrix = self.vectorizer.transform(texts)
        return matrix.toarray().astype(np.float32)


class OpenAIEmbeddingProvider(EmbeddingProvider):
    def __init__(
        self,
        api_key: str,
        model: str = "text-embedding-3-small",
        base_url: str = "https://api.openai.com/v1",
        timeout: float = 30.0,
        client: httpx.Client | None = None,
    ):
        self.api_key = api_key
        self.model = model
        self.name = f"openai:{model}"
        self.base_url = base_url.rstrip("/")
        self.client = client or httpx.Client(timeout=timeout)

    def embed(self, texts: list[str]) -> np.ndarray:
        if not texts:
            return np.empty((0, 0), dtype=np.float32)
        response = self.client.post(
            f"{self.base_url}/embeddings",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={"model": self.model, "input": texts},
        )
        response.raise_for_status()
        payload = response.json()
        vectors = [row["embedding"] for row in sorted(payload["data"], key=lambda x: x["index"])]
        return np.asarray(vectors, dtype=np.float32)
