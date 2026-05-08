import json
import pathlib
import subprocess

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
BASELINE = REPO_ROOT / "gsd/.planning/phases/5/isolation-baseline.json"


def _path_from_status_line(line: str) -> str:
    return line[3:].split(" -> ")[-1]


def test_phase5_isolation_delta() -> None:
    assert BASELINE.exists(), "missing phase 5 baseline"
    baseline = json.loads(BASELINE.read_text(encoding="utf-8"))
    baseline_status = set(baseline.get("status_lines", []))
    baseline_hashes = baseline.get("dirty_non_gsd_hashes", {})
    now_status = set(subprocess.check_output(["git", "status", "--porcelain"], text=True).splitlines())

    added = [line for line in (now_status - baseline_status) if line.strip()]
    bad = [line for line in added if not _path_from_status_line(line).startswith("gsd/")]
    assert not bad, f"new non-gsd changes introduced: {bad}"

    for path, old_hash in baseline_hashes.items():
        p = REPO_ROOT / path
        assert p.exists(), f"pre-existing non-gsd file removed: {path}"
        new_hash = subprocess.check_output(["git", "hash-object", str(p)], text=True).strip()
        assert new_hash == old_hash, f"pre-existing non-gsd file changed: {path}"


def test_phase5_no_new_root_runtime_or_build_artifacts() -> None:
    baseline = json.loads(BASELINE.read_text(encoding="utf-8"))
    baseline_status = set(baseline.get("status_lines", []))
    now_status = set(subprocess.check_output(["git", "status", "--porcelain"], text=True).splitlines())

    for line in (now_status - baseline_status):
        path = _path_from_status_line(line)
        assert not path.startswith("build/"), f"new root build artifact changed: {line}"
        assert not path.startswith("src/runtime/"), f"new root runtime artifact changed: {line}"
