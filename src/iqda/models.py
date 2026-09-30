from __future__ import annotations

from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field


class DocumentMetadata(BaseModel):
    document_id: str
    component_id: str | None = None
    revision: int | None = None
    status: str = "unknown"
    effective_date: str | None = None
    document_type: str | None = None
    supersedes: str | None = None
    source_path: str


class ParsedDocument(BaseModel):
    metadata: DocumentMetadata
    text: str
    lines: list[str]


class Chunk(BaseModel):
    chunk_id: str
    document_id: str
    text: str
    start_line: int
    end_line: int
    section: str | None = None
    metadata: DocumentMetadata


class SearchHit(BaseModel):
    chunk: Chunk
    score: float


class Usage(BaseModel):
    input_tokens: int | None = None
    output_tokens: int | None = None
    total_tokens: int | None = None


class AnswerDraft(BaseModel):
    answer: str
    cited_chunk_ids: list[str] = Field(default_factory=list)
    missing_information: list[str] = Field(default_factory=list)
    conflict_detected: bool = False
    rationale: str = ""


class Citation(BaseModel):
    chunk_id: str
    document_id: str
    revision: int | None = None
    section: str | None = None
    source_path: str
    excerpt: str


class AnswerStatus(str, Enum):
    answered = "answered"
    partial = "partial"
    refused = "refused"
    escalate = "escalate"


class AnswerResponse(BaseModel):
    question: str
    answer: str
    status: AnswerStatus
    confidence: float = Field(ge=0.0, le=1.0)
    citations: list[Citation] = Field(default_factory=list)
    reasons: list[str] = Field(default_factory=list)
    missing_information: list[str] = Field(default_factory=list)
    retrieval: list[dict[str, Any]] = Field(default_factory=list)
    request_id: str
    latency_ms: float
    usage: Usage = Field(default_factory=Usage)
    approval_id: str | None = None


class AskRequest(BaseModel):
    question: str = Field(min_length=3, max_length=2000)


class ApprovalDecision(BaseModel):
    decision: str = Field(pattern="^(approved|rejected)$")
    reviewer_note: str | None = Field(default=None, max_length=2000)


class ApprovalRecord(BaseModel):
    id: str
    question: str
    response_json: str
    decision: str
    reviewer_note: str | None = None
    created_at: str
    updated_at: str


class EvalCase(BaseModel):
    id: str
    category: str
    question: str
    expected_status: AnswerStatus
    expected_doc_ids: list[str] = Field(default_factory=list)
    expected_answer_contains: list[str] = Field(default_factory=list)
    notes: str = ""
