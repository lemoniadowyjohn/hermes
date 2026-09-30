# Evaluation

The repository includes a deliberately small synthetic regression evaluation in `scripts/evaluate.py`.

It checks four bounded behaviors:

1. the current AX17 torque requirement is retrieved;
2. the current BX21 dimensional requirement is retrieved;
3. an unknown component is refused rather than guessed;
4. a superseded AX17 revision is not returned.

Run:

```bash
python scripts/evaluate.py
```

The evaluation is a regression check for this synthetic corpus. It is **not** a benchmark of general LLM accuracy or retrieval quality on real industrial documentation.

The optional OpenAI provider path remains a separate integration path and is not required for the deterministic CI acceptance gate.
