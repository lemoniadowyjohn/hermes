from iqda.evaluation import run_evaluation


def test_evaluation_suite_is_reproducible(service):
    report = run_evaluation(service, "data/eval/eval_cases.json")
    summary = report["summary"]
    assert summary["cases"] == 10
    assert summary["structured_output_validity"] == 1.0
    assert summary["refusal_correctness"] == 1.0
    assert summary["status_accuracy"] >= 0.9
