#!/usr/bin/env python3
"""Authoritative cross-platform clean-directory acceptance driver."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Sequence

from generate_outputs import OUTPUT_ALLOWLIST

ROOT = Path(__file__).parents[1].resolve()
PRIVATE_PATH_PATTERN = re.compile(
    r"(?<![A-Za-z])(?:[A-Za-z]:[\\/]|\\\\|"
    r"/(?:home|Users|root|tmp|private/var(?:/folders)?)/)"
)
SECRET_PATTERN = re.compile(
    r"(?:gh[pousr]_[A-Za-z0-9]{20,}|sk-[A-Za-z0-9]{20,}|"
    r"AKIA[0-9A-Z]{16}|-----BEGIN [A-Z ]*PRIVATE KEY-----)"
)
STALE_TOKEN = "NOT_ESTABLISHED" + "_BY_FROZEN_SNAPSHOT"
CACHE_NAMES = {"__pycache__", ".ipynb_checkpoints", ".pytest_cache", ".mypy_cache"}
FORBIDDEN_PACKAGE_DIRECTORIES = CACHE_NAMES | {".venv", "build", "generated"}
PRIVATE_PATH_FIXTURE_FILES = {
    "audit/CODEX_VISIBLE_CONVERSATION_LOG_UTF8.txt",
    "mct_reward_simulation.py",
    "scripts/compare_notebook_semantics.py",
    "scripts/execute_notebook.py",
    "scripts/run_smoke_tests.py",
    "scripts/validate_package.py",
    "tests/test_notebook_regression.py",
    "tests/test_path_security.py",
    "tests/test_scoring.py",
}


def run(
    command: Sequence[str], cwd: Path, environment: dict[str, str]
) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(
        list(command),
        cwd=cwd,
        env=environment,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if completed.returncode:
        raise RuntimeError(
            "Command failed: "
            + " ".join(command)
            + "\nSTDOUT:\n"
            + completed.stdout
            + "\nSTDERR:\n"
            + completed.stderr
        )
    return completed


def copy_candidate(destination: Path) -> None:
    def ignore(_directory: str, names: list[str]) -> set[str]:
        return {
            name
            for name in names
            if name in CACHE_NAMES
            or name in {".git", ".venv", "build", "generated"}
            or name.endswith(".pyc")
        }

    shutil.copytree(ROOT, destination, ignore=ignore)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def output_hashes(directory: Path) -> dict[str, str]:
    return {name: sha256(directory / name) for name in OUTPUT_ALLOWLIST}


def scan_tree(
    root: Path, allowed_runtime_directories: set[str] | None = None
) -> dict[str, str]:
    allowed_runtime_directories = allowed_runtime_directories or set()
    text_suffixes = {
        "",
        ".cff",
        ".csv",
        ".json",
        ".ipynb",
        ".md",
        ".py",
        ".sh",
        ".sol",
        ".txt",
        ".xy",
        ".yaml",
        ".yml",
    }
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root).as_posix()
        if (
            path.is_dir()
            and path.name in FORBIDDEN_PACKAGE_DIRECTORIES
            and relative not in allowed_runtime_directories
        ):
            raise RuntimeError(f"Forbidden package directory present: {relative}")
        if not path.is_file():
            continue
        if path.suffix.lower() in {".pyc", ".pyo"}:
            raise RuntimeError(f"Compiled bytecode present: {relative}")
        if path.name.endswith((".tmp.ipynb", ".ipynb~", ".bak")):
            raise RuntimeError(f"Temporary or backup file present: {relative}")
        if path.suffix.lower() not in text_suffixes:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if (
            relative not in PRIVATE_PATH_FIXTURE_FILES
            and PRIVATE_PATH_PATTERN.search(text)
        ):
            raise RuntimeError(f"Private absolute path present: {relative}")
        if SECRET_PATTERN.search(text):
            raise RuntimeError(f"Credential-like secret present: {relative}")
        if STALE_TOKEN in text:
            raise RuntimeError(f"Stale validation vocabulary present: {relative}")
    return {
        "cache_scan": "PASS",
        "private_path_scan": "PASS",
        "secret_scan": "PASS",
        "stale_vocabulary_scan": "PASS",
    }


def compare_snapshots(repo: Path, generated: Path, env: dict[str, str]) -> None:
    for name in OUTPUT_ALLOWLIST:
        if name == "verification_workflow_demo_executed.ipynb":
            continue
        committed_path = repo / "outputs" / name
        generated_path = generated / name
        if committed_path.read_bytes() != generated_path.read_bytes():
            raise RuntimeError(f"Committed output snapshot differs: {name}")
    run(
        [
            sys.executable,
            "-B",
            "scripts/compare_notebook_semantics.py",
            "verification_workflow_demo.ipynb",
            "outputs/verification_workflow_demo_executed.ipynb",
            "generated/verification_workflow_demo_executed.ipynb",
        ],
        repo,
        env,
    )


def run_once(repo: Path, notebook_backend: str) -> dict[str, Any]:
    environment = os.environ.copy()
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    environment["PYTHONUTF8"] = "1"
    runtime_root = repo.parent / "jupyter-runtime"
    environment["IPYTHONDIR"] = str(runtime_root / "ipython")
    environment["JUPYTER_CONFIG_DIR"] = str(runtime_root / "config")
    environment["JUPYTER_DATA_DIR"] = str(runtime_root / "data")
    environment["JUPYTER_RUNTIME_DIR"] = str(runtime_root / "runtime")
    for variable in (
        "IPYTHONDIR",
        "JUPYTER_CONFIG_DIR",
        "JUPYTER_DATA_DIR",
        "JUPYTER_RUNTIME_DIR",
    ):
        Path(environment[variable]).mkdir(parents=True, exist_ok=True)

    run(
        [sys.executable, "-B", "scripts/validate_package.py", "--candidate-root", "."],
        repo,
        environment,
    )

    generated = repo / "generated"
    generated.mkdir()
    (generated / "STALE_SENTINEL.txt").write_text("stale\n", encoding="utf-8")
    (generated / "summary.json").write_text("stale\n", encoding="utf-8")

    generation_command = [
        sys.executable,
        "-B",
        "scripts/generate_outputs.py",
        "--output-dir",
        "generated",
        "--notebook-backend",
        notebook_backend,
    ]
    release_acceptance = notebook_backend == "nbclient"
    if release_acceptance:
        generation_command.append("--acceptance")
    run(generation_command, repo, environment)

    if (generated / "STALE_SENTINEL.txt").exists():
        raise RuntimeError("Stale-output cleaning failed")
    actual_outputs = sorted(path.name for path in generated.iterdir() if path.is_file())
    if actual_outputs != sorted(OUTPUT_ALLOWLIST):
        raise RuntimeError(f"Generated output set differs: {actual_outputs}")

    compare_snapshots(repo, generated, environment)
    run(
        [sys.executable, "-B", "-m", "unittest", "discover", "-s", "tests", "-v"],
        repo,
        environment,
    )
    run(
        [
            sys.executable,
            "-B",
            "-m",
            "unittest",
            "discover",
            "-s",
            "MOF_WorkedExample/tests",
            "-v",
        ],
        repo,
        environment,
    )
    run(
        [sys.executable, "-B", "scripts/validate_release.py", "--json"],
        repo,
        environment,
    )
    scans = scan_tree(repo, {"generated"})
    return {
        "generated_hashes": output_hashes(generated),
        "notebook_backend": notebook_backend,
        "notebook_semantic_equivalence": "PASS",
        "package_integrity": "PASS",
        "release_acceptance_backend": release_acceptance,
        "scans": scans,
        "stale_output_cleaning": "PASS",
        "unit_and_negative_tests": "PASS",
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--notebook-backend",
        choices=("nbclient", "stdlib"),
        default="nbclient",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    arguments = build_parser().parse_args(argv)
    source_scans = scan_tree(ROOT)
    with tempfile.TemporaryDirectory(prefix="paper1-v034-smoke-") as temporary:
        temp_root = Path(temporary)
        repo_one = temp_root / "run-one" / "candidate"
        repo_two = temp_root / "run-two" / "candidate"
        copy_candidate(repo_one)
        copy_candidate(repo_two)
        first = run_once(repo_one, arguments.notebook_backend)
        second = run_once(repo_two, arguments.notebook_backend)
        if first["generated_hashes"] != second["generated_hashes"]:
            raise RuntimeError("Clean-directory reruns produced different artifacts")

    result = {
        "candidate_version": "0.3.4-alpha",
        "clean_directory_runs": 2,
        "generated_hashes": first["generated_hashes"],
        "notebook_backend": arguments.notebook_backend,
        "notebook_semantic_equivalence": first["notebook_semantic_equivalence"],
        "overall_status": "PASS",
        "package_integrity": first["package_integrity"],
        "release_acceptance_backend": first["release_acceptance_backend"],
        "scans": first["scans"],
        "source_package_scans": source_scans,
        "stale_output_cleaning": "PASS",
        "unit_and_negative_tests": "PASS",
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
