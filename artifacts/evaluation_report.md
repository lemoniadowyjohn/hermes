# Evaluation Report

## Summary

- **cases**: 10
- **status_accuracy**: 1.0
- **retrieval_hit_rate**: 1.0
- **retrieval_cases**: 4
- **citation_correctness**: 1.0
- **citation_cases**: 4
- **factual_consistency**: 1.0
- **factual_cases**: 4
- **refusal_correctness**: 1.0
- **structured_output_validity**: 1.0
- **mean_latency_ms**: 0.89
- **token_usage_available**: False

## Cases

| ID | Category | Expected | Actual | Status OK |
|---|---|---|---|---|
| E01 | answerable | answered | answered | True |
| E02 | answerable | answered | answered | True |
| E03 | partially_answerable | partial | partial | True |
| E04 | unanswerable | refused | refused | True |
| E05 | conflicting_documents | escalate | escalate | True |
| E06 | missing_document | refused | refused | True |
| E07 | ambiguous_requirement | refused | refused | True |
| E08 | outdated_revision | refused | refused | True |
| E09 | wrong_component_id | refused | refused | True |
| E10 | answerable_traceability | answered | answered | True |
