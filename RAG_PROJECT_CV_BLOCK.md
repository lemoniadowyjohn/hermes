# RAG Project CV Block

## Status

**HOLD — DO NOT COPY TO CV YET**

Reason: the repository and offline regression suite run successfully, and mocked OpenAI HTTP contracts pass, but a real LLM/embedding API evaluation and a Docker build/run have not yet been executed in the current verification environment.

## Approval gate

Change this file to `APPROVED` only after:

1. real-provider index build succeeds;
2. real-provider evaluation meets the release thresholds in `EVALUATION.md`;
3. citation/refusal safety cases remain passing;
4. Docker image builds and the containerized API passes a smoke test;
5. repository/history review confirms no proprietary data or secrets.

## Future CV wording after approval

**Industrial Quality Documentation Assistant — Applied AI Portfolio Project**

- Built an evidence-grounded documentation assistant over synthetic industrial quality and inspection records, with revision-aware retrieval, source citations, conflict detection, and refusal/escalation when evidence is missing or inconsistent.
- Implemented a reproducible evaluation harness covering answerable, partial, unanswerable, conflicting, missing-document, ambiguous, stale-revision, and wrong-component scenarios, including retrieval, citation, factual-consistency, refusal, schema-validity, latency, and usage metrics.
- Exposed the workflow through a typed REST API with persistent human-review records, automated tests, structured logging, and container packaging.

### Technology line — add only after the approval gate passes

Python · FastAPI · Pydantic · RAG · embeddings · vector retrieval · LLM API · structured outputs/function calling · SQLite · pytest · Docker

## Interview-safe description before approval

If discussing the project before the gate is complete, describe it as an **implemented portfolio prototype with offline regression tests and mocked provider-contract tests**, not as a validated production LLM deployment.
