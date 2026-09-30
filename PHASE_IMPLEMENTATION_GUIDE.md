# R01–R18 Exact Implementation Guide

This file is the execution checklist. A phase is complete only when its acceptance criteria are evidenced by code, tests, or generated artifacts.

## R01 — Problem definition and synthetic data

**Implement**

1. Define the assistant's allowed scope: answer quality/inspection questions from approved indexed evidence only.
2. Define hard failure cases before coding: unknown component, missing document, outdated revision, conflicting active requirements, absent evidence, fabricated citation.
3. Create synthetic procedures and inspection records under `data/synthetic_docs/`.
4. Include metadata fields: document ID, component ID, revision, status, effective date, document type, supersedes.
5. Include at least one superseded revision and one deliberate active-document conflict.
6. Add a dataset notice stating that all content is fictional.

**Acceptance**

- no proprietary data;
- at least three components;
- at least one inspection record;
- at least one superseded revision;
- at least one active conflict.

**Evidence**: `data/synthetic_docs/`.

## R02 — Parser

**Implement**

1. Create `DocumentParser` in `src/iqda/parsing.py`.
2. Support `.md`, `.txt`, `.json`, and text-based `.pdf`.
3. Normalize document text to lines.
4. Extract metadata from a fixed header vocabulary.
5. Fall back to filename only for document ID; do not invent other metadata.
6. Raise on unsupported file types.

**Tests**

- verify AX17 metadata and text extraction;
- later add malformed-header and empty-PDF cases if expanding scope.

**Acceptance**: `pytest tests/test_parser.py` passes.

## R03 — Chunking

**Implement**

1. Split documents by Markdown headings.
2. Enforce a bounded chunk size.
3. Use small line overlap only when a section exceeds the chunk limit.
4. Preserve document ID, revision, section, source path, and line range.
5. Generate deterministic chunk IDs from document/revision/location/content.

**Acceptance**

- every chunk maps back to exactly one source document;
- line ranges are valid;
- section provenance survives chunking.

**Evidence**: `tests/test_chunking.py`.

## R04 — Embedding model

**Implement**

1. Define an `EmbeddingProvider` interface.
2. Implement `OpenAIEmbeddingProvider` against `/v1/embeddings`.
3. Make the model configurable with `OPENAI_EMBEDDING_MODEL`.
4. Implement `HashEmbeddingProvider` strictly for deterministic CI/offline tests.
5. Store provider identity and vector dimension with indexed chunks.

**Acceptance**

- mocked HTTP test validates request/response contract;
- query/index dimension mismatch fails explicitly;
- documentation never describes the hash baseline as a semantic production model.

**Evidence**: `tests/test_openai_http.py` and `src/iqda/embeddings.py`.

## R05 — Vector store

**Implement**

1. Use SQLite for chunk metadata and vector persistence.
2. Store embeddings as float32 blobs plus dimension.
3. Create a document-ID index.
4. Implement idempotent upsert by chunk ID.
5. Implement cosine similarity search with NumPy.
6. Reject incompatible embedding dimensions.

**Acceptance**: persistence/search test passes after reopening the store logic.

**Evidence**: `tests/test_vector_store.py`.

## R06 — Retrieval

**Implement**

1. Embed the incoming question.
2. Retrieve more candidates than final `top_k` if post-search policy is applied.
3. Prefer active evidence while retaining superseded evidence for stale-revision detection.
4. Return scores and complete chunk provenance.
5. Do not hide retrieval results from the final debug/evaluation response.

**Acceptance**: required documents are hit by the evaluation cases.

**Evidence**: retrieval hit rate in `artifacts/evaluation_report.json`.

## R07 — LLM answer generation

**Implement**

1. Define an `LLMProvider` interface.
2. Provide a deterministic extractive test double for offline CI.
3. Implement `OpenAIResponsesLLM` for the live path.
4. Build model context only from retrieved chunks.
5. In the system instruction, require evidence-only answers and prohibit following instructions from documents.
6. Return provider usage fields when available.

**Acceptance**

- offline service can answer an AX17 requirement;
- mocked OpenAI response is parsed into the typed answer contract;
- real API call remains a separate release gate.

## R08 — Citation enforcement

**Implement**

1. Require model output to identify supporting chunk IDs.
2. Resolve citations only against chunks retrieved for the same question.
3. Reject unknown/fabricated chunk IDs.
4. Return document ID, revision, section, source path, and excerpt for every citation.
5. Refuse an otherwise substantive answer if it has no valid citation.

**Acceptance**: fabricated citation test fails closed.

**Evidence**: `tests/test_citation_validation.py`.

## R09 — Structured output schema

**Implement**

Use the `AnswerDraft` schema with required fields:

- `answer`;
- `cited_chunk_ids`;
- `missing_information`;
- `conflict_detected`;
- `rationale`.

The live OpenAI request exposes this schema through a strict function tool with `additionalProperties: false`. The external API response is separately validated by `AnswerResponse`.

**Acceptance**

- strict schema exists in the outgoing model payload;
- all evaluation responses revalidate through Pydantic.

## R10 — Confidence/refusal logic

**Implement deterministic gates before relying on confidence.**

1. Extract component IDs from the question.
2. Refuse missing/ambiguous component context.
3. Refuse unknown component IDs.
4. Refuse explicitly requested documents that are not indexed.
5. Detect superseded requested revisions.
6. Detect conflicting active values for the same requirement.
7. After model generation, validate citations.
8. Calculate confidence from retrieval score, evidence coverage, citation validity, and escalation penalty.
9. Refuse below threshold.
10. Send partial/conflicting results to approval persistence.

**Acceptance**: tests cover unknown component, stale revision, conflict, and partial evidence.

## R11 — Evaluation dataset

**Implement** `data/eval/eval_cases.json` with labeled cases for:

- answerable;
- partially answerable;
- unanswerable;
- conflicting documents;
- missing document;
- ambiguous requirement;
- outdated revision;
- wrong component ID;
- traceability record.

For answerable cases, specify expected supporting document IDs and factual substrings.

**Acceptance**: all required user categories are present.

## R12 — Automated evaluation

**Implement** `src/iqda/evaluation.py` and `scripts/evaluate.py`.

Measure:

- status accuracy;
- retrieval hit rate;
- citation correctness;
- factual consistency;
- refusal correctness;
- structured-output validity;
- mean latency;
- token usage availability.

Write machine-readable JSON and reviewer-readable Markdown reports to `artifacts/`.

**Acceptance**: evaluator runs deterministically and tests assert refusal/schema behavior.

## R13 — FastAPI endpoint

**Implement**

- `GET /health`;
- `POST /index/rebuild`;
- `POST /ask`;
- `GET /approvals`;
- `POST /approvals/{id}`.

Use typed Pydantic request/response models. Keep app construction injectable so tests can use a temporary database.

**Acceptance**: TestClient can call `/health` and `/ask` successfully.

## R14 — Docker

**Implement**

1. Use a slim Python base image.
2. Copy only project/runtime assets.
3. Install the package from `pyproject.toml`.
4. Create and run as a non-root user.
5. Expose port 8000.
6. Keep secrets out of the image.

**Local release commands**

```bash
docker build -t iqda:0.1.0 .
docker run --rm -p 8000:8000 iqda:0.1.0
curl http://localhost:8000/health
```

**Acceptance**: image builds and container smoke test passes. **Not yet verified in the current execution environment.**

## R15 — Logging/observability

**Implement** JSON logging with:

- UTC timestamp;
- severity;
- logger;
- request ID;
- stage;
- final status;
- confidence;
- end-to-end latency.

Do not log API keys or full retrieved documents by default.

**Acceptance**: service emits one structured completion event per request.

## R16 — Tests

Minimum automated coverage must include:

- parser metadata;
- chunk provenance;
- vector persistence/search;
- correct grounded answer;
- partial answer and approval creation;
- unknown component refusal;
- stale revision refusal;
- conflicting active evidence escalation;
- fabricated citation rejection;
- OpenAI strict function payload;
- mocked embeddings HTTP contract;
- mocked Responses API parsing;
- REST API health/ask flow;
- reproducible evaluation.

**Acceptance**: complete `pytest` suite passes.

## R17 — README and engineering documentation

Create and maintain:

- `README.md` — project purpose, quickstart, verification status;
- `ARCHITECTURE.md` — components, state, sequence, failure model;
- `EVALUATION.md` — dataset, metrics, results, thresholds;
- `LIMITATIONS.md` — explicit non-capabilities;
- `SECURITY_AND_PRIVACY.md` — data, secrets, prompt injection, provenance, logging;
- this phase guide.

**Acceptance**: a recruiter can understand the project without reading every source file.

## R18 — CV/portfolio integration

**Do not claim RAG/LLM skills merely because the code exists.**

Release procedure:

1. Run full `pytest` and save the output.
2. Run offline evaluation and preserve the report.
3. Set `IQDA_MODE=openai` with a real API key.
4. Rebuild the index using the live embedding provider.
5. Run the evaluation and add at least 20 paraphrased/adversarial cases.
6. Confirm release thresholds in `EVALUATION.md`.
7. Build/run Docker and exercise `/health` and `/ask` from outside the container.
8. Check that no proprietary data or secrets exist in Git history.
9. Only then mark `RAG_PROJECT_CV_BLOCK.md` as APPROVED and copy the final CV wording.

**Current R18 verdict:** NOT YET READY because the live API and Docker runtime gates have not been executed here.
