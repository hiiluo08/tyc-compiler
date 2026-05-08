import json
import pathlib
import subprocess


BASELINE = pathlib.Path("gsd/.planning/phases/1/isolation-baseline.txt")


def _path_from_status_line(line: str) -> str:
    return line[3:].split(" -> ")[-1]


def test_isolation_no_new_or_mutated_non_gsd_changes() -> None:
    assert BASELINE.exists(), "missing isolation baseline"

    baseline = json.loads(BASELINE.read_text(encoding="utf-8"))
    baseline_status = set(baseline.get("status_lines", []))
    baseline_hashes = baseline.get("dirty_non_gsd_hashes", {})

    current_status = set(
        subprocess.check_output(["git", "status", "--porcelain"], text=True).splitlines()
    )

    added_lines = sorted([line for line in (current_status - baseline_status) if line.strip()])
    added_outside = [
        line for line in added_lines if not _path_from_status_line(line).startswith("gsd/")
    ]
    assert not added_outside, f"new non-gsd changes introduced: {added_outside}"

    for path, old_hash in baseline_hashes.items():
        file_path = pathlib.Path(path)
        assert file_path.exists(), f"pre-existing non-gsd file removed: {path}"
        new_hash = subprocess.check_output(["git", "hash-object", path], text=True).strip()
        assert new_hash == old_hash, f"pre-existing non-gsd file changed: {path}"


def test_isolation_no_root_build_or_runtime_artifacts_touched() -> None:
    baseline = json.loads(BASELINE.read_text(encoding="utf-8"))
    baseline_status = set(baseline.get("status_lines", []))
    current_status = set(
        subprocess.check_output(["git", "status", "--porcelain"], text=True).splitlines()
    )

    for line in current_status - baseline_status:
        path = _path_from_status_line(line)
        assert not path.startswith("build/"), f"root build artifact changed: {line}"
        assert not path.startswith("src/runtime/"), f"root runtime artifact changed: {line}"
