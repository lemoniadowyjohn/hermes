from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    mode: str = os.getenv("IQDA_MODE", "offline")
    db_path: Path = Path(os.getenv("IQDA_DB_PATH", "data/iqda.db"))
    docs_dir: Path = Path(os.getenv("IQDA_DOCS_DIR", "data/synthetic_docs"))
    top_k: int = int(os.getenv("IQDA_TOP_K", "6"))
    confidence_threshold: float = float(os.getenv("IQDA_CONFIDENCE_THRESHOLD", "0.55"))
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY") or None
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-5.6-luna")
    openai_embedding_model: str = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")

    def validate(self) -> None:
        if self.mode not in {"offline", "openai"}:
            raise ValueError("IQDA_MODE must be 'offline' or 'openai'")
        if self.mode == "openai" and not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required when IQDA_MODE=openai")
