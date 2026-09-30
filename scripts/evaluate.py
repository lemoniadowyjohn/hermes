from pathlib import Path

from iqda.core import RAGService


DATA = Path(__file__).parents[1] / "data" / "synthetic_docs"


def main() -> int:
    service = RAGService.from_directory(DATA)

    cases = [
        (
            "AX17 active requirement",
            service.ask("What is the tightening torque for component AX17?"),
            lambda result: result.status == "answered" and "32 Nm" in result.text,
        ),
        (
            "BX21 active requirement",
            service.ask("What is the maximum dimensional deviation for component BX21?"),
            lambda result: result.status == "answered" and "0.5 mm" in result.text,
        ),
        (
            "unknown component refusal",
            service.ask("What is the requirement for component ZZ99?"),
            lambda result: result.status == "refused",
        ),
        (
            "superseded revision excluded",
            service.ask("What is the tightening torque for component AX17?"),
            lambda result: "28 Nm" not in result.text,
        ),
    ]

    passed = 0
    for name, result, predicate in cases:
        ok = predicate(result)
        passed += int(ok)
        print(f"{'PASS' if ok else 'FAIL'}: {name}")

    print(f"evaluation: {passed}/{len(cases)} cases passed")
    return 0 if passed == len(cases) else 1


if __name__ == "__main__":
    raise SystemExit(main())
