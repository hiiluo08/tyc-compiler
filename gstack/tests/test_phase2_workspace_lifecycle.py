from pathlib import Path

from runner.app.runtime_workspace import RuntimeWorkspace


def test_workspace_created_and_cleaned_up(tmp_path: Path) -> None:
    runtime_assets = tmp_path / "runtime_assets"
    runtime_assets.mkdir(parents=True, exist_ok=True)
    (runtime_assets / "jasmin.jar").write_bytes(b"jar")
    (runtime_assets / "io.class").write_bytes(b"class")

    ws_path = None
    with RuntimeWorkspace(runtime_assets) as ws:
        ws_path = ws.path
        assert ws_path.exists()
        assert (ws.path / "jasmin.jar").exists()
        assert (ws.path / "io.class").exists()

    assert ws_path is not None
    assert not ws_path.exists()
