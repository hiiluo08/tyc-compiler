from fastapi.testclient import TestClient

from runner.app.main import app


client = TestClient(app)


def test_run_stub_has_required_top_level_fields() -> None:
    response = client.post("/api/v1/run", json={"source": "void main() {}"})
    body = response.json()
    for key in [
        "ok",
        "status",
        "stdout",
        "stderr",
        "diagnostics",
        "astText",
        "astJson",
        "stages",
        "durationMs",
        "truncated",
    ]:
        assert key in body


def test_ast_stub_has_required_top_level_fields() -> None:
    response = client.post("/api/v1/ast", json={"source": "void main() {}"})
    body = response.json()
    for key in ["ok", "status", "diagnostics", "astText", "astJson", "durationMs"]:
        assert key in body
