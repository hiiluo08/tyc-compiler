from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_returns_ok():
    response = client.get("/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["ok"] is True
    assert payload["service"] == "tyc-runner-openspec"


def test_run_success_print_string():
    source = 'void main() { printString("Hello TyC"); }'
    response = client.post(
        "/api/v1/run",
        json={"source": source, "stdin": "", "timeoutSeconds": 3, "includeAst": True},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["ok"] is True
    assert payload["status"] == "success"
    assert payload["stdout"] == "Hello TyC"


def test_run_with_stdin_read_int():
    source = """
void main() {
    int x = readInt();
    printInt(x + 1);
}
"""
    response = client.post(
        "/api/v1/run",
        json={"source": source, "stdin": "41\n", "timeoutSeconds": 3, "includeAst": True},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["ok"] is True
    assert payload["status"] == "success"
    assert payload["stdout"] == "42"


def test_run_syntax_error():
    source = "void main( { }"
    response = client.post(
        "/api/v1/run",
        json={"source": source, "stdin": "", "timeoutSeconds": 3, "includeAst": True},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["ok"] is False
    assert payload["status"] == "syntax_error"
    assert payload["diagnostics"][0]["stage"] == "parse"


def test_run_semantic_error_preserves_ast():
    source = 'void main() { int x = "abc"; }'
    response = client.post(
        "/api/v1/run",
        json={"source": source, "stdin": "", "timeoutSeconds": 3, "includeAst": True},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["ok"] is False
    assert payload["status"] == "semantic_error"
    assert payload["astText"]
    assert payload["astJson"]


def test_run_runtime_error():
    source = """
void main() {
    int x = 1 / 0;
    printInt(x);
}
"""
    response = client.post(
        "/api/v1/run",
        json={"source": source, "stdin": "", "timeoutSeconds": 3, "includeAst": True},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["ok"] is False
    assert payload["status"] == "runtime_error"


def test_run_timeout():
    source = """
void main() {
    while (1) {}
}
"""
    response = client.post(
        "/api/v1/run",
        json={"source": source, "stdin": "", "timeoutSeconds": 1, "includeAst": True},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["ok"] is False
    assert payload["status"] == "timeout"


def test_ast_endpoint_returns_ast():
    response = client.post("/api/v1/ast", json={"source": "void main() {}"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["ok"] is True
    assert payload["status"] == "success"
    assert payload["astText"]
    assert payload["astJson"]


def test_invalid_timeout_rejected():
    response = client.post(
        "/api/v1/run",
        json={
            "source": "void main() {}",
            "stdin": "",
            "timeoutSeconds": 99,
            "includeAst": True,
        },
    )

    assert response.status_code == 422


def test_missing_source_rejected():
    response = client.post("/api/v1/run", json={"stdin": ""})
    assert response.status_code == 422
