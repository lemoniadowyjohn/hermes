# Verification Receipt

Verification date: 2026-09-30

## Hosted CI authority

GitHub Actions run **36718957001** verified the public Industrial Quality Documentation Assistant after retrieval and decimal-handling fixes.

Verified results:

- unit tests: **4 passed**;
- synthetic evaluation: **4/4 cases passed**;
- AX17 active requirement: **PASS**;
- BX21 active dimensional requirement: **PASS**;
- unknown-component refusal: **PASS**;
- superseded-revision exclusion: **PASS**;
- Docker image build: **PASS**;
- container startup: **PASS**;
- HTTP health endpoint: **PASS**;
- observed health payload: `{"status":"ok","mode":"offline","chunks":6}`.

## Defects closed during verification

1. **Missing runtime server dependency** — the Dockerfile invoked `uvicorn`, but it was not declared as a production dependency. `uvicorn>=0.30` is now included in `pyproject.toml`.
2. **Explicit-component retrieval ordering** — component filtering previously happened after global top-k selection. It now happens before ranking for explicitly named components.
3. **Decimal truncation** — the deterministic answer provider previously split every period as a sentence boundary, truncating values such as `0.5 mm` to `0.`. Sentence segmentation is now decimal-safe.
4. **Regression coverage** — BX21 retrieval/value preservation is covered by a dedicated unit test.

## Remaining release boundary

The optional OpenAI embedding/answer-provider path exists, but a credentialed live-provider evaluation has not yet been executed and saved as public evidence.

Therefore the repository supports claims such as:

- built a bounded industrial RAG portfolio implementation;
- implemented retrieval, citations, revision/status filtering, refusal/escalation and deterministic evaluation;
- containerized and CI-smoke-tested the FastAPI service;
- implemented an optional OpenAI integration path.

It does **not** yet support claims of production OpenAI deployment, production LLM operations, or validated real-provider quality.
