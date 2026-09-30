from pathlib import Path
import pytest

from iqda.config import Settings
from iqda.factory import build_components, rebuild_index


@pytest.fixture
def settings(tmp_path: Path) -> Settings:
    return Settings(
        mode="offline",
        db_path=tmp_path / "iqda.db",
        docs_dir=Path("data/synthetic_docs"),
        top_k=6,
        confidence_threshold=0.55,
        openai_api_key=None,
        openai_model="gpt-5.6-luna",
        openai_embedding_model="text-embedding-3-small",
    )


@pytest.fixture
def service(settings):
    rebuild_index(settings)
    service, *_ = build_components(settings)
    return service
