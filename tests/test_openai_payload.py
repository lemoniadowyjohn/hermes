from iqda.llm import OpenAIResponsesLLM


def test_openai_payload_uses_strict_function_calling(service):
    hits = service.retriever.retrieve("AX17 torque requirement")
    client = OpenAIResponsesLLM(api_key="test", model="gpt-test")
    payload = client.build_payload("What is the torque requirement for component AX17?", hits)
    tool = payload["tools"][0]
    assert tool["type"] == "function"
    assert tool["name"] == "submit_quality_answer"
    assert tool["strict"] is True
    assert tool["parameters"]["additionalProperties"] is False
    assert payload["tool_choice"]["name"] == "submit_quality_answer"
