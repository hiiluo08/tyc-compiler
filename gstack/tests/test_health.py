from fastapi.testclient import TestClient

from runner.app.main import app


client = TestClient(app)


def test_health_contract_exact() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {
        "ok": True,
        "service": "tyc-runner-gstack",
        "version": "0.1.0",
    }
