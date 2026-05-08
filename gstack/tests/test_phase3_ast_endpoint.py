from fastapi.testclient import TestClient

from runner.app.main import app

client = TestClient(app)


def test_ast_endpoint_returns_ast_text_and_json() -> None:
    response = client.post("/api/v1/ast", json={"source": "void main() {}"})
    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is True
    assert body["status"] == "success"
    assert isinstance(body["astText"], str)
    assert body["astText"]
    assert isinstance(body["astJson"], dict)
    assert "kind" in body["astJson"]
    assert "fields" in body["astJson"]
