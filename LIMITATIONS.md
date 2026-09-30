# Limitations

This project is intentionally scoped as a portfolio system, not a production quality-management platform.

## Data limitations

The corpus is synthetic and small. It does not represent the typography, tables, scanned PDFs, drawings, multilingual terminology, abbreviations, or document-volume distributions found in a real automotive quality environment.

## Parsing limitations

PDF support is text extraction only. There is no OCR, table reconstruction, drawing interpretation, image evidence, or robust form-field extraction. Scanned inspection sheets would need a separate OCR/vision pipeline and their own evaluation set.

## Retrieval limitations

The offline HashingVectorizer is a deterministic CI baseline, not a semantic production embedding model. The SQLite vector search loads compatible vectors and performs linear cosine search, which is suitable for a small corpus but not large-scale ANN retrieval.

There is no cross-encoder reranker, hybrid BM25+dense retrieval, query expansion, or learned retrieval calibration yet.

## Requirement understanding limitations

The current deterministic gates recognize component IDs in a deliberately narrow `AA00` pattern and a small set of requirement labels such as torque, coating, and dimension. A production system would need an explicit ontology or master-data integration rather than regex alone.

## Conflict detection limitations

Conflict detection currently compares normalized requirement strings in active retrieved chunks. It does not perform unit conversion, tolerance equivalence, precedence rules, approval hierarchy, or effective-date interval reasoning beyond a simple active/superseded state.

## LLM limitations

The real LLM path is implemented and HTTP-contract tested with mocks, but it has not been executed in this environment with a real API key. Model behavior, rate limits, token cost, live latency, and live structured-output reliability therefore remain unverified.

## Security limitations

There is no authentication, authorization, tenant isolation, encrypted secret store, document antivirus scanning, data-loss prevention, rate limiting, or enterprise audit trail. The API is suitable only for local portfolio demonstration unless those controls are added.

## Human review limitations

The approval queue is intentionally minimal. It does not implement role-based reviewers, electronic signatures, immutable audit events, escalation SLA, four-eyes approval, or integration with a QMS.

## Deployment limitations

A Dockerfile is provided, but the current execution environment did not expose Docker or Podman, so an actual image build and container smoke test could not be verified here.

## Evaluation limitations

The current 10-case suite is a regression harness, not a statistically meaningful benchmark. The 100% offline result should never be quoted as general model accuracy.
