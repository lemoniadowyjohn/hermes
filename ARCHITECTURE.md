# Architecture

## Design objective

The architecture optimizes for **auditability and failure visibility**, not maximum framework abstraction. A reviewer should be able to follow a question from source document through retrieval, model output, validation, confidence gating, and human escalation.

## Components

### 1. Document parser

`DocumentParser` accepts Markdown, text, JSON, and text-based PDF files. It extracts document ID, component ID, revision, status, effective date, document type, supersession relationship, and source path. Parsed text is retained with line boundaries so later chunks preserve provenance.

### 2. Section chunker

`SectionChunker` splits on Markdown headings and then applies bounded character windows. Every chunk retains document metadata, section, and source line range. Chunk IDs are deterministic hashes of document/revision/location/content.

### 3. Embedding provider

The application uses an interface with two implementations:

- `HashEmbeddingProvider`: deterministic CI/test baseline only;
- `OpenAIEmbeddingProvider`: live semantic embedding provider.

Provider identity is stored with vectors so incompatible query/index dimensions fail loudly rather than silently mixing embeddings.

### 4. Vector persistence

`SQLiteVectorStore` stores chunk text, metadata, embedding vectors, dimensions, and embedding provider identity. Search uses NumPy cosine similarity over the small corpus. This is intentionally simple and inspectable. A production corpus with millions of chunks would require an ANN-capable vector system.

### 5. Retrieval

`Retriever` embeds the question, searches the store, and prioritizes active documents while still allowing superseded evidence to remain discoverable for stale-revision checks.

### 6. LLM boundary

`LLMProvider` isolates model-specific behavior. The live provider uses the Responses API and forces a strict `submit_quality_answer` function call with a JSON schema containing:

- answer;
- cited chunk IDs;
- missing information;
- conflict flag;
- rationale.

Documents are explicitly treated as untrusted evidence, not instructions.

### 7. Deterministic validation

The model is not trusted to decide whether its own answer is safe. `EvidenceValidator` performs deterministic checks for:

- component IDs;
- requested document IDs;
- requested revisions;
- active-vs-superseded evidence;
- conflicting active requirement values;
- citation IDs that were not retrieved.

### 8. Confidence and refusal

`compute_confidence` combines retrieval similarity, evidence coverage, citation validity, and escalation penalties. Hard safety/evidence failures bypass confidence and stop the answer directly.

### 9. Human approval persistence

Partial answers and explicit conflicts produce approval records in SQLite. The REST API exposes a minimal review flow with approve/reject decisions and reviewer notes.

### 10. Evaluation harness

The evaluation layer executes the same service used by the API. It records expected vs actual status and computes retrieval, citation, factual, refusal, schema, latency, and token-usage metrics.

## End-to-end sequence

```text
Client
  │ POST /ask
  ▼
FastAPI
  ▼
QualityAssistantService
  ├── preflight component/document/revision checks
  ├── Retriever
  │     ├── embed query
  │     └── SQLite cosine search
  ├── conflict gate
  ├── LLMProvider
  │     └── strict structured answer + citation IDs
  ├── citation validator
  ├── confidence gate
  ├── optional ApprovalStore write
  ▼
AnswerResponse
```

## State boundaries

**Persisted:** index chunks/vectors, document metadata, human-approval records.

**Not persisted by default:** prompts, raw model responses, API keys, user conversation history. This reduces accidental retention in a portfolio prototype.

## Failure model

The system prefers explicit failure states over silent degradation:

- embedding dimension mismatch → exception;
- invalid provider mode → startup failure;
- model omits required strict function call → exception;
- fabricated citation → rejected;
- missing component/document → refusal;
- outdated revision → refusal;
- conflicting active evidence → escalation;
- partially supported multi-part request → partial answer + approval queue.

## Why no orchestration framework

The project is specifically intended to prove understanding of RAG fundamentals. Direct interfaces make the retrieval boundary, context construction, output schema, validation, and evaluation code visible. A framework could be introduced later if application breadth justifies it, but it would not solve a current requirement.
