from fastapi.testclient import TestClient

from runner.app.main import app


client = TestClient(app)


def test_ast_missing_source_rejected() -> None:
    response = client.post("/api/v1/ast", json={})
    assert response.status_code == 422


def test_ast_oversized_source_rejected_with_input_too_large() -> None:
    source = "a" * 65537
    response = client.post("/api/v1/ast", json={"source": source})
    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is False
    assert body["status"] == "input_too_large"


def test_ast_valid_stub_returns_contract_shape() -> None:
    response = client.post("/api/v1/ast", json={"source": "void main() {}"})
    assert response.status_code == 200
    body = response.json()
    assert set(body.keys()) == {
        "ok",
        "status",
        "diagnostics",
        "astText",
        "astJson",
        "durationMs",
    }
