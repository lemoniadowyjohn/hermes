# Limitations

This is a compact portfolio implementation, not a production document-control platform.

Known limitations:

- the CI retriever uses deterministic feature hashing rather than a semantic embedding model;
- the optional OpenAI path requires separate credentialed evaluation;
- the synthetic corpus is intentionally small;
- no OCR pipeline is included;
- no enterprise identity, authorization or tenant controls are implemented;
- conflict detection is intentionally conservative and focused on simple numerical requirements;
- the FastAPI service uses in-memory indexing and is not designed for large corpora;
- Docker packaging and container health are CI-verified, but this does not constitute production deployment evidence.

The purpose is to make retrieval, provenance, refusal and validation logic inspectable.
