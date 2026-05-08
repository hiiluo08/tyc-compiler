import shutil
import subprocess
from pathlib import Path


def main() -> None:
    runner_dir = Path(__file__).resolve().parents[1]
    repo_root = runner_dir.parents[1]

    build_dir = runner_dir / "build"
    runtime_assets_dir = runner_dir / "runtime_assets"
    vendor_grammar_dir = runner_dir / "compiler_vendor" / "grammar"

    antlr_jar = repo_root / "external" / "antlr-4.13.2-complete.jar"
    grammar_file = vendor_grammar_dir / "TyC.g4"
    lexererr_file = vendor_grammar_dir / "lexererr.py"

    if not antlr_jar.exists():
        raise FileNotFoundError(f"Missing ANTLR jar: {antlr_jar}")
    if not grammar_file.exists():
        raise FileNotFoundError(f"Missing grammar file: {grammar_file}")

    build_dir.mkdir(parents=True, exist_ok=True)
    runtime_assets_dir.mkdir(parents=True, exist_ok=True)

    subprocess.run(
        [
            "java",
            "-jar",
            str(antlr_jar),
            "-Dlanguage=Python3",
            "-visitor",
            "-no-listener",
            "-o",
            str(build_dir),
            str(grammar_file),
        ],
        check=True,
    )

    (build_dir / "__init__.py").touch()
    shutil.copy2(lexererr_file, build_dir / "lexererr.py")

    root_runtime_dir = repo_root / "src" / "runtime"
    shutil.copy2(root_runtime_dir / "jasmin.jar", runtime_assets_dir / "jasmin.jar")
    shutil.copy2(root_runtime_dir / "io.java", runtime_assets_dir / "io.java")

    subprocess.run(
        ["javac", "io.java"],
        cwd=runtime_assets_dir,
        check=True,
    )


if __name__ == "__main__":
    main()
