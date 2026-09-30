# Security and Privacy

## Data handling policy

The repository contains only synthetic data. Do not replace it with proprietary employer, supplier, customer, drawing, inspection, or production documents in a public repository.

## Secrets

API keys must be supplied through environment variables. `.env` is git-ignored. Keys must never be embedded in source code, test fixtures, example outputs, Docker images, or committed shell history.

## Document trust boundary

Retrieved documents are treated as **untrusted data**. The model system instruction explicitly says not to follow instructions embedded inside documents. This reduces, but does not eliminate, retrieval-based prompt-injection risk.

Additional production controls should include:

- document-source allowlists;
- ingestion-time content classification;
- prompt-injection detection;
- escaping/delimiting retrieved context;
- least-privilege tool access;
- tool argument validation;
- no side-effecting model tools without explicit authorization.

## Evidence integrity

The service does not accept free-form citation text as proof. The model returns chunk IDs, and the validator resolves only IDs that were actually retrieved for the current request. Unknown citation IDs are rejected.

For production, add content hashes, signed document metadata, source-system IDs, ingestion timestamps, and immutable provenance records.

## Revision safety

Superseded documents are not silently treated as current. Explicit requests for an outdated revision are refused when a newer active revision exists. Conflicting active requirements are escalated instead of automatically choosing a value.

## Privacy and retention

The prototype persists index content and human-approval records in SQLite. It does not persist API keys or full prompt/model response logs by default. If real data is ever used, define retention, deletion, backup, access-control, and data-residency policies before ingestion.

## Logging

Structured logs contain request IDs, status, confidence, latency, and stage metadata. They intentionally avoid raw document text and secrets. Production deployments should apply centralized log retention, access control, redaction, and correlation IDs.

## Network and API security

The prototype API has no authentication or TLS termination. Run it only on a trusted local interface during portfolio testing. A real deployment would require authentication, authorization, HTTPS, rate limiting, request-size limits, and network policy.

## Supply chain

Dependencies are version-bounded in `pyproject.toml`. A production CI pipeline should additionally perform dependency locking, vulnerability scanning, SBOM generation, container scanning, and periodic dependency review.
