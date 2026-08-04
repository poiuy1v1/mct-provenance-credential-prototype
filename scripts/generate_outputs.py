#!/usr/bin/env python3
"""Clean and regenerate the complete deterministic output allow-list."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Sequence

ROOT = Path(__file__).parents[1].resolve()
OUTPUT_ALLOWLIST = (
    "diagnostic_event_scores.csv",
    "diagnostic_sensitivity.csv",
    "release_validation.json",
    "simulation_dry_run_stdout.json",
    "simulation_stdout.json",
    "summary.json",
    "verification_results.csv",
    "verification_workflow_demo_executed.ipynb",
)


def safe_output_path(path: str | Path) -> Path:
    resolved = (ROOT / path).resolve() if not Path(path).is_absolute() else Path(path).resolve()
    if resolved == ROOT or ROOT not in resolved.parents:
        raise ValueError("Output directory must be a child of the candidate root")
    if resolved.name in {"", ".", ".."}:
        raise ValueError("Unsafe output directory")
    return resolved


def clean_output_directory(path: str | Path) -> Path:
    output_dir = safe_output_path(path)
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True)
    return output_dir


def write_lf(path: Path, text: str) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)


def run(command: Sequence[str], env: dict[str, str]) -> str:
    completed = subprocess.run(
        list(command),
        cwd=ROOT,
        env=env,
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
    if completed.stderr:
        raise RuntimeError(
            "Command emitted unexpected stderr: "
            + " ".join(command)
            + "\n"
            + completed.stderr
        )
    return completed.stdout


def generate(output_dir: Path, notebook_backend: str, acceptance: bool) -> dict[str, object]:
    relative_output = output_dir.relative_to(ROOT).as_posix()
    environment = os.environ.copy()
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    environment["PYTHONUTF8"] = "1"
    environment["MCT_OUTPUT_DIR"] = relative_output
    python = sys.executable

    simulation_stdout = run(
        [
            python,
            "-B",
            "mct_reward_simulation.py",
            "--input",
            "data/example_contributions.json",
            "--output-dir",
            relative_output,
        ],
        environment,
    )
    write_lf(output_dir / "simulation_stdout.json", simulation_stdout)

    dry_run_stdout = run(
        [
            python,
            "-B",
            "mct_reward_simulation.py",
            "--input",
            "data/example_contributions.json",
            "--output-dir",
            relative_output,
            "--dry-run",
        ],
        environment,
    )
    write_lf(output_dir / "simulation_dry_run_stdout.json", dry_run_stdout)

    validation_stdout = run(
        [python, "-B", "scripts/validate_release.py", "--json"],
        environment,
    )
    write_lf(output_dir / "release_validation.json", validation_stdout)

    notebook_command = [
        python,
        "-B",
        "scripts/execute_notebook.py",
        "verification_workflow_demo.ipynb",
        f"{relative_output}/verification_workflow_demo_executed.ipynb",
        "--backend",
        notebook_backend,
        "--workdir",
        ".",
    ]
    if acceptance:
        notebook_command.append("--acceptance")
    notebook_stdout = run(notebook_command, environment)
    notebook_report = json.loads(notebook_stdout)

    actual = sorted(path.name for path in output_dir.iterdir() if path.is_file())
    expected = sorted(OUTPUT_ALLOWLIST)
    if actual != expected:
        raise RuntimeError(
            f"Generated output allow-list mismatch; expected={expected}, actual={actual}"
        )
    return {
        "generated_outputs": actual,
        "notebook": notebook_report,
        "output_directory": relative_output,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="outputs")
    parser.add_argument(
        "--notebook-backend",
        choices=("nbclient", "stdlib", "auto"),
        default="nbclient",
    )
    parser.add_argument("--acceptance", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    arguments = build_parser().parse_args(argv)
    output_dir = clean_output_directory(arguments.output_dir)
    report = generate(output_dir, arguments.notebook_backend, arguments.acceptance)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
