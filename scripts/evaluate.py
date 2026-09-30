import json
from pathlib import Path

from iqda.config import Settings
from iqda.evaluation import run_evaluation
from iqda.factory import build_components, rebuild_index

if __name__ == "__main__":
    settings = Settings()
    rebuild_index(settings)
    service, *_ = build_components(settings)
    report = run_evaluation(service, "data/eval/eval_cases.json")
    Path("artifacts").mkdir(exist_ok=True)
    Path("artifacts/evaluation_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    lines = ["# Evaluation Report", "", "## Summary", ""]
    for key, value in report["summary"].items():
        lines.append(f"- **{key}**: {value}")
    lines += ["", "## Cases", "", "| ID | Category | Expected | Actual | Status OK |", "|---|---|---|---|---|"]
    for row in report["cases"]:
        lines.append(f"| {row['id']} | {row['category']} | {row['status_expected']} | {row['status_actual']} | {row['status_correct']} |")
    Path("artifacts/evaluation_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(report["summary"], indent=2))
