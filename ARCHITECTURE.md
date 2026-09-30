# Architecture

The repository separates retrieval, answer generation and validation so each control can be tested independently.

```text
Synthetic Markdown documents
        |
frontmatter + line-aware chunking
        |
embedding provider
  |                 |
offline hash       OpenAI embeddings
(CI baseline)      (optional live path)
        |
cosine retrieval
        |
current-revision/status filtering
        |
answer provider
  |                 |
deterministic       OpenAI Responses
(CI baseline)       (optional live path)
        |
citation + refusal + conflict gates
        |
structured API response
```

## Design boundaries

- The offline hash embedding is deliberately a deterministic regression baseline, not a claim of semantic-model quality.
- The live provider is isolated behind interfaces so tests do not require API credentials.
- Document status and revision selection happen before answer generation.
- Unknown component identifiers are refused rather than guessed.
- Active contradictory numerical requirements are escalated for human review.
