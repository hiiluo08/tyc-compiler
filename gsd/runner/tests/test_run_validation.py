from fastapi.testclient import TestClient

from runner.app.main import app


client = TestClient(app)


def _required_run_keys() -> set[str]:
    return {
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
    }


def test_run_missing_source_rejected() -> None:
    response = client.post("/api/v1/run", json={})
    assert response.status_code == 422


def test_run_timeout_out_of_range_rejected() -> None:
    response_low = client.post(
        "/api/v1/run",
        json={"source": "void main() {}", "timeoutSeconds": 0},
    )
    response_high = client.post(
        "/api/v1/run",
        json={"source": "void main() {}", "timeoutSeconds": 6},
    )
    assert response_low.status_code == 422
    assert response_high.status_code == 422


def test_run_include_ast_must_be_bool() -> None:
    response = client.post(
        "/api/v1/run",
        json={"source": "void main() {}", "includeAst": "true"},
    )
    assert response.status_code == 422


def test_run_include_ast_default_applies() -> None:
    response = client.post("/api/v1/run", json={"source": "void main() {}"})
    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is True
    assert body["status"] == "success"
    assert _required_run_keys().issubset(body.keys())


def test_run_oversized_source_rejected_with_input_too_large() -> None:
    source = "a" * 65537
    response = client.post("/api/v1/run", json={"source": source})
    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is False
    assert body["status"] == "input_too_large"


def test_run_oversized_stdin_rejected_with_input_too_large() -> None:
    stdin = "a" * 16385
    response = client.post(
        "/api/v1/run",
        json={"source": "void main() {}", "stdin": stdin},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is False
    assert body["status"] == "input_too_large"


def test_run_valid_stub_returns_contract_shape() -> None:
    response = client.post(
        "/api/v1/run",
        json={
            "source": "void main() { printString(\"Hello\"); }",
            "stdin": "",
            "timeoutSeconds": 3,
            "includeAst": True,
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert _required_run_keys().issubset(body.keys())
    assert set(body["stages"].keys()) == {
        "parse",
        "ast",
        "semantic",
        "codegen",
        "assemble",
        "run",
    }
    assert set(body["truncated"].keys()) == {"stdout", "stderr"}
