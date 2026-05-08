import subprocess

from fastapi.testclient import TestClient

from runner.app.main import app

client = TestClient(app)


def test_run_semantic_error_preserves_ast_include_ast_true() -> None:
    response = client.post(
        "/api/v1/run",
        json={"source": 'void main() { int x = "abc"; }', "includeAst": True},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "semantic_error"
    assert body["astText"] is not None
    assert body["astJson"] is not None


def test_run_syntax_error_has_parse_stage_diagnostic() -> None:
    response = client.post("/api/v1/run", json={"source": "void main( { }"})
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "syntax_error"
    assert body["diagnostics"]
    assert body["diagnostics"][0]["stage"] == "parse"


def test_run_runtime_error_mapping(monkeypatch) -> None:
    class FakeResult:
        returncode = 1
        stdout = ""
        stderr = "runtime failed"

    monkeypatch.setattr(
        "runner.app.runtime_workspace.RuntimeWorkspace.execute",
        lambda *args, **kwargs: FakeResult(),
    )

    response = client.post(
        "/api/v1/run",
        json={"source": 'void main() { printString("x"); }', "timeoutSeconds": 2},
    )
    body = response.json()
    assert body["status"] == "runtime_error"
    assert "runtime failed" in body["stderr"]


def test_run_timeout_mapping(monkeypatch) -> None:
    def _raise_timeout(*args, **kwargs):
        raise subprocess.TimeoutExpired(cmd=["java"], timeout=1)

    monkeypatch.setattr(
        "runner.app.runtime_workspace.RuntimeWorkspace.execute",
        _raise_timeout,
    )

    response = client.post(
        "/api/v1/run",
        json={"source": 'void main() { printString("x"); }', "timeoutSeconds": 1},
    )
    body = response.json()
    assert body["status"] == "timeout"
