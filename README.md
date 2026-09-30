# Industrial Quality Documentation Assistant

[![CI](https://github.com/lemoniadowyjohn/hermes/actions/workflows/ci.yml/badge.svg)](https://github.com/lemoniadowyjohn/hermes/actions/workflows/ci.yml)

A portfolio-grade, evidence-grounded RAG system for synthetic industrial quality documentation. The project is designed to demonstrate the gap between a chatbot that merely produces plausible text and an applied-AI system that can retrieve evidence, cite it, detect stale/conflicting documentation, refuse unsupported requests, and route uncertain cases to human review.

**Data policy:** all bundled documents are synthetic. No proprietary employer or customer documents are included.

## Problem

Industrial quality work often depends on knowing which requirement applies to which component, revision, batch, and inspection record. A plausible but unsupported answer is unacceptable. The assistant therefore treats answer generation as only one stage in a larger evidence-control workflow.

```text
Documents
  ↓
Parsing + metadata extraction
  ↓
Section-aware chunking
  ↓
Embeddings
  ↓
SQLite vector persistence
  ↓
Retrieval
  ↓
LLM / deterministic test double
  ↓
Strict structured answer
  ↓
Citation + revision + conflict validation
  ↓
Confidence/refusal gate
  ↓
Answer / partial answer / human escalation
```

## Pragmatic technology choices

- **Python 3.11+** for the application and evaluation code.
- **FastAPI + Pydantic** for a small typed REST surface and response validation.
- **SQLite + NumPy cosine similarity** for transparent persistence and vector search. For this portfolio corpus, a separate vector database would add operational complexity without improving the learning objective.
- **OpenAI embeddings and Responses API as the configurable live provider.** The repository also contains deterministic offline providers so CI can test control logic without spending API tokens.
- **scikit-learn HashingVectorizer only as the offline embedding test baseline.** It is explicitly not presented as the production semantic embedding model.
- **pytest** for unit, integration, HTTP-contract, and evaluation tests.
- **Dockerfile** for container packaging.

The live OpenAI implementation uses strict JSON-schema function calling for the answer contract. Model and embedding IDs are environment-configurable so the code does not depend on a hard-coded long-lived model assumption.

## Repository layout

```text
src/iqda/
  api.py             FastAPI application
  parsing.py         Markdown/text/JSON/PDF parsing + metadata
  chunking.py        section-aware chunks with line provenance
  embeddings.py      offline and OpenAI embedding providers
  vector_store.py    SQLite vector persistence + cosine search
  retrieval.py       retrieval policy
  llm.py             offline test double + OpenAI Responses client
  validation.py      citation/revision/component/conflict gates
  confidence.py      confidence calculation
  persistence.py     human-approval persistence
  service.py         end-to-end orchestration
  evaluation.py      reproducible evaluation harness

data/synthetic_docs/ synthetic quality procedures and inspection records
data/eval/            evaluation cases
tests/                automated tests
scripts/              index/evaluation/smoke commands
artifacts/            generated evaluation evidence
```

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"

PYTHONPATH=src python scripts/build_index.py
PYTHONPATH=src python scripts/smoke_test.py
pytest
PYTHONPATH=src python scripts/evaluate.py
PYTHONPATH=src uvicorn iqda.api:app --host 0.0.0.0 --port 8000
```

Example request:

```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"What is the torque requirement for component AX17?"}'
```

The response includes a status, confidence, structured citations, retrieval evidence, reasons, latency, and provider usage when available.

## Run with a real LLM and semantic embeddings

```bash
export IQDA_MODE=openai
export OPENAI_API_KEY=...
export OPENAI_MODEL=<supported Responses API model>
export OPENAI_EMBEDDING_MODEL=text-embedding-3-small

PYTHONPATH=src python scripts/build_index.py
PYTHONPATH=src python scripts/evaluate.py
```

Do not commit `.env` or API keys. The live provider path must be evaluated separately because offline CI deliberately uses deterministic test doubles.

## REST API

- `GET /health` — runtime mode, embedding provider, index state.
- `POST /index/rebuild` — rebuild the local index from configured documents.
- `POST /ask` — retrieve, answer, validate, and apply confidence/refusal logic.
- `GET /approvals` — pending partial/conflict escalations.
- `POST /approvals/{id}` — approve or reject an escalated result with a reviewer note.

## Quality behavior demonstrated

The assistant does not blindly answer. It can reject or escalate when:

- the component ID is missing or ambiguous;
- the component ID is unknown;
- a specifically requested document is absent;
- a user requests a superseded revision while a later active revision exists;
- two active documents contain conflicting requirements;
- the LLM cites a chunk that was not actually retrieved;
- the requested information is missing from the evidence;
- confidence is below the configured threshold.

## Current verification status

Local verification performed in the supplied execution environment:

- automated tests: **passing**;
- synthetic evaluation cases: **10**;
- retrieval hit rate: **100% across 4 eligible evidence-bearing cases**;
- citation correctness: **100% across 4 cited-answer cases**;
- factual consistency checks: **100% across 4 labeled factual cases**;
- refusal correctness: **100%**;
- structured-output validity: **100%**;
- OpenAI HTTP payload/response contracts: **tested with mocked HTTP**;
- real OpenAI API call: **not executed**;
- Docker image build/run: **not executed because no Docker/Podman runtime was available**.

These percentages describe a deliberately small synthetic regression set, not general-world model accuracy.

## Portfolio release gate

**Current verdict: NOT YET READY to claim RAG/LLM skills on the CV.**

The repository is code-complete enough for the offline portfolio demonstration, but the final GenAI claim should wait until both of these are completed on the user's machine:

1. Run the full evaluation in `IQDA_MODE=openai` against a real API key and save the resulting report.
2. Build and run the Docker image, then repeat the smoke test against the containerized API.

After those gates pass without weakening refusal/citation behavior, update `RAG_PROJECT_CV_BLOCK.md` from HOLD to APPROVED.

See `PHASE_IMPLEMENTATION_GUIDE.md`, `ARCHITECTURE.md`, `EVALUATION.md`, `LIMITATIONS.md`, and `SECURITY_AND_PRIVACY.md` for the engineering details.
