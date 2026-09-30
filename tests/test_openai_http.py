import json
import httpx
import numpy as np

from iqda.embeddings import OpenAIEmbeddingProvider
from iqda.llm import OpenAIResponsesLLM


def test_openai_embedding_http_contract():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/v1/embeddings"
        payload = json.loads(request.content)
        assert payload["model"] == "text-embedding-3-small"
        assert payload["input"] == ["hello"]
        return httpx.Response(200, json={"data": [{"index": 0, "embedding": [0.1, 0.2, 0.3]}]})

    client = httpx.Client(transport=httpx.MockTransport(handler))
    provider = OpenAIEmbeddingProvider("test", client=client)
    vector = provider.embed(["hello"])
    assert vector.shape == (1, 3)
    assert vector.dtype == np.float32


def test_openai_response_parses_strict_function_result(service):
    hits = service.retriever.retrieve("AX17 torque")

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/v1/responses"
        payload = json.loads(request.content)
        assert payload["tools"][0]["strict"] is True
        arguments = {
            "answer": "Torque: 8.5 ± 0.5 Nm.",
            "cited_chunk_ids": [hits[0].chunk.chunk_id],
            "missing_information": [],
            "conflict_detected": False,
            "rationale": "Grounded in active evidence.",
        }
        return httpx.Response(
            200,
            json={
                "output": [
                    {
                        "type": "function_call",
                        "name": "submit_quality_answer",
                        "arguments": json.dumps(arguments),
                        "call_id": "call_1",
                    }
                ],
                "usage": {"input_tokens": 100, "output_tokens": 40, "total_tokens": 140},
            },
        )

    client = httpx.Client(transport=httpx.MockTransport(handler))
    llm = OpenAIResponsesLLM("test", "gpt-test", client=client)
    draft, usage = llm.answer("What is the torque requirement for component AX17?", hits)
    assert "8.5" in draft.answer
    assert usage.total_tokens == 140
