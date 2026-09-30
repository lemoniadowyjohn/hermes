# Industrial Quality Documentation Assistant

> **Repository identity:** the GitHub slug `hermes` is historical. This repository contains the **Industrial Quality Documentation Assistant** RAG portfolio project. It is **not** the separate Hermes/OpenClaw agent-orchestration R&D project referenced in Michał Dembski's CV/LinkedIn. The agent-orchestration work remains a separate personal R&D track.

[![CI](https://github.com/lemoniadowyjohn/hermes/actions/workflows/ci.yml/badge.svg)](https://github.com/lemoniadowyjohn/hermes/actions/workflows/ci.yml)

A portfolio-grade, evidence-grounded RAG system for synthetic industrial quality documentation. The project demonstrates retrieval, citations, stale/conflicting-document detection, refusal of unsupported requests, structured validation, confidence handling and human escalation.

**Data policy:** all bundled documents are synthetic. No proprietary employer or customer documents are included.

## Claim boundary

This project is portfolio/project evidence, not professional employer delivery. Current public claims must remain bounded to the evidence in this repository.

**Release gate:** do not describe this project as production RAG/LLM experience until both a real-provider evaluation and Docker build/run smoke test have been completed and saved as evidence.

## Architecture

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

## Technology choices

- Python 3.11+
- FastAPI + Pydantic
- SQLite + NumPy cosine similarity
- configurable OpenAI embeddings / Responses provider
- deterministic offline providers for CI
- pytest
- Dockerfile for packaging

## Current verification status

- automated tests: passing
- synthetic evaluation cases: 10
- retrieval hit rate: 100% across 4 eligible evidence-bearing cases
- citation correctness: 100% across 4 cited-answer cases
- factual consistency checks: 100% across 4 labeled factual cases
- refusal correctness: 100%
- structured-output validity: 100%
- real OpenAI API evaluation: **not yet executed**
- Docker build/run: **not yet executed**

These percentages describe a deliberately small synthetic regression set; they are not general-world accuracy claims.

## Portfolio status

**HOLD for broad RAG/LLM CV skill claims** until:

1. the live-provider evaluation is executed and saved;
2. the Docker image is built and smoke-tested;
3. the evidence is re-read and the release status is explicitly changed to APPROVED.

The code and detailed engineering documentation remain the evidence source for this portfolio project.
