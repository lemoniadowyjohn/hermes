from __future__ import annotations

from fastapi import FastAPI, HTTPException

from .config import Settings
from .factory import build_components, rebuild_index
from .logging_utils import configure_logging
from .models import AnswerResponse, ApprovalDecision, ApprovalRecord, AskRequest


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or Settings()
    settings.validate()
    service, store, embeddings, approvals = build_components(settings)
    app = FastAPI(title="Industrial Quality Documentation Assistant", version="0.1.0")

    @app.get("/health")
    def health() -> dict:
        return {
            "status": "ok",
            "mode": settings.mode,
            "embedding_provider": embeddings.name,
            "indexed_documents": len(store.all_metadata()),
        }

    @app.post("/index/rebuild")
    def index_rebuild() -> dict:
        count = rebuild_index(settings)
        return {"chunks_indexed": count}

    @app.post("/ask", response_model=AnswerResponse)
    def ask(request: AskRequest) -> AnswerResponse:
        return service.ask(request.question)

    @app.get("/approvals", response_model=list[ApprovalRecord])
    def pending_approvals() -> list[ApprovalRecord]:
        return approvals.list_pending()

    @app.post("/approvals/{approval_id}", response_model=ApprovalRecord)
    def decide_approval(approval_id: str, decision: ApprovalDecision) -> ApprovalRecord:
        try:
            return approvals.decide(approval_id, decision.decision, decision.reviewer_note)
        except KeyError:
            raise HTTPException(status_code=404, detail="approval not found")

    return app


configure_logging()
app = create_app()
