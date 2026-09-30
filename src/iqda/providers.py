from __future__ import annotations

from typing import Protocol, Sequence


class AnswerProvider(Protocol):
    def generate(self, question: str, evidence: Sequence[str]) -> str: ...


class DeterministicAnswerProvider:
    """Offline provider used for CI. It only returns text already present in evidence."""

    def generate(self, question: str, evidence: Sequence[str]) -> str:
        terms = {t.strip("?.:,;()[]").lower() for t in question.split() if len(t) > 2}
        candidates = []
        for block in evidence:
            for sentence in block.replace("\n", " ").split("."):
                sentence = sentence.strip()
                if sentence:
                    overlap = len(
                        terms
                        & {t.strip("?.:,;()[]").lower() for t in sentence.split()}
                    )
                    candidates.append((overlap, sentence))
        if not candidates:
            return ""
        return max(candidates, key=lambda item: item[0])[1] + "."


class OpenAIAnswerProvider:
    """Optional live LLM adapter. Requires the `llm` extra and OPENAI_API_KEY."""

    def __init__(self, model: str = "gpt-5-mini") -> None:
        from openai import OpenAI
        self.client = OpenAI()
        self.model = model

    def generate(self, question: str, evidence: Sequence[str]) -> str:
        joined = "\n\n".join(f"[E{i+1}] {item}" for i, item in enumerate(evidence))
        response = self.client.responses.create(
            model=self.model,
            input=(
                "Answer only from the supplied evidence. If the evidence does not support "
                "the answer, return exactly INSUFFICIENT_EVIDENCE.\n\n"
                f"Evidence:\n{joined}\n\nQuestion: {question}"
            ),
        )
        return response.output_text.strip()
