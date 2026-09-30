from fastapi.testclient import TestClient

from iqda.api import create_app
from iqda.factory import rebuild_index


def test_api_health_and_ask(settings):
    rebuild_index(settings)
    client = TestClient(create_app(settings))
    health = client.get("/health")
    assert health.status_code == 200
    assert health.json()["indexed_documents"] >= 1

    result = client.post("/ask", json={"question": "What is the torque requirement for component AX17?"})
    assert result.status_code == 200
    body = result.json()
    assert body["status"] == "answered"
    assert body["citations"]
