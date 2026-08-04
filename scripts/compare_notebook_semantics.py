#!/usr/bin/env python3
"""Strict source/execution/output regression for the demonstration notebook."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

EXPECTED_OUTPUTS = [
    {"event_count": 6, "schema_version": "0.3.4-alpha"},
    {"diagnostic_score_sum": 23.0324, "row_count": 6},
    {
        "observed_validation_states": {
            "evidence_file_status": ["evidence_file_present", "not_checked"],
            "file_integrity_status": ["file_integrity_confirmed", "not_checked"],
            "metadata_status": ["metadata_validated"],
            "scientific_assessment_status": ["not_reviewed"],
            "source_link_status": ["source_link_recorded"],
        },
        "output": "verification_results.csv",
        "verification_results_sha256": "5d245030b0d64878d8d2cb73754c1b66a417770d02bc694ffe148e6eec5171d9",
        "verification_row_count": 6,
    },
]

STALE_VALIDATION_TERMS = {
    "scientific_validation_status",
    "scientific_status",
    "integrity_verified_as_scientific",
    "NOT_ESTABLISHED" + "_BY_FROZEN_SNAPSHOT",
}

PRIVATE_PATH_PATTERN = re.compile(
    r"(?<![A-Za-z])(?:[A-Za-z]:[\\/]|\\\\|"
    r"/(?:home|Users|root|tmp|private/var(?:/folders)?)/)"
)
SECRET_PATTERN = re.compile(
    r"(?:gh[pousr]_[A-Za-z0-9]{20,}|sk-[A-Za-z0-9]{20,}|"
    r"AKIA[0-9A-Z]{16}|-----BEGIN [A-Z ]*PRIVATE KEY-----)"
)


class NotebookRegressionError(ValueError):
    pass


def load_notebook(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def source_text(cell: dict[str, Any]) -> str:
    source = cell.get("source", "")
    return "".join(source) if isinstance(source, list) else str(source)


def output_text(output: dict[str, Any]) -> str:
    text = output.get("text", "")
    return "".join(text) if isinstance(text, list) else str(text)


def code_cells(notebook: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        cell for cell in notebook.get("cells", []) if cell.get("cell_type") == "code"
    ]


def parse_deterministic_output(cell: dict[str, Any]) -> dict[str, Any]:
    outputs = cell.get("outputs", [])
    if not outputs:
        raise NotebookRegressionError("Mandatory deterministic output was cleared")
    if any(output.get("output_type") == "error" for output in outputs):
        raise NotebookRegressionError("Notebook contains an error output")
    if any(
        output.get("output_type") == "stream" and output.get("name") == "stderr"
        for output in outputs
    ):
        raise NotebookRegressionError("Notebook contains stderr output")
    unsupported = [
        output.get("output_type")
        for output in outputs
        if output.get("output_type") != "stream"
    ]
    if unsupported:
        raise NotebookRegressionError(
            f"Unexpected deterministic output type(s): {unsupported}"
        )
    lines = [
        line
        for output in outputs
        for line in output_text(output).splitlines()
        if line.strip()
    ]
    if len(lines) != 1:
        raise NotebookRegressionError(
            "Each verification cell must emit exactly one JSON output line"
        )
    try:
        value = json.loads(lines[0])
    except json.JSONDecodeError as error:
        raise NotebookRegressionError(
            "Deterministic notebook output is not valid JSON"
        ) from error
    if not isinstance(value, dict):
        raise NotebookRegressionError("Deterministic notebook output is not an object")
    return value


def validate_notebooks(
    source_notebook: dict[str, Any], executed_notebook: dict[str, Any]
) -> None:
    source_structure = [
        (cell.get("id"), cell.get("cell_type"), source_text(cell))
        for cell in source_notebook.get("cells", [])
    ]
    executed_structure = [
        (cell.get("id"), cell.get("cell_type"), source_text(cell))
        for cell in executed_notebook.get("cells", [])
    ]
    if source_structure != executed_structure:
        raise NotebookRegressionError("Notebook source/cell-order regression detected")

    source_code = code_cells(source_notebook)
    executed_code = code_cells(executed_notebook)
    if len(executed_code) != len(EXPECTED_OUTPUTS):
        raise NotebookRegressionError(
            f"Expected {len(EXPECTED_OUTPUTS)} executed code cells"
        )
    if any(
        cell.get("execution_count") is not None or cell.get("outputs")
        for cell in source_code
    ):
        raise NotebookRegressionError(
            "Source notebook must remain unexecuted and output-free"
        )
    if any(cell.get("execution_count") is None for cell in executed_code):
        raise NotebookRegressionError("Null execution count detected")
    execution_counts = [cell.get("execution_count") for cell in executed_code]
    if any(type(count) is not int or count <= 0 for count in execution_counts):
        raise NotebookRegressionError(
            f"Invalid execution count type or value: {execution_counts}"
        )
    if execution_counts != list(range(1, len(executed_code) + 1)):
        raise NotebookRegressionError(
            f"Unexpected execution counts: {execution_counts}"
        )

    serialized = json.dumps(executed_notebook, ensure_ascii=False)
    if PRIVATE_PATH_PATTERN.search(serialized):
        raise NotebookRegressionError("Private absolute path detected")
    if SECRET_PATTERN.search(serialized):
        raise NotebookRegressionError("Credential-like secret detected")
    stale = sorted(term for term in STALE_VALIDATION_TERMS if term in serialized)
    if stale:
        raise NotebookRegressionError(
            "Stale validation vocabulary detected: " + ", ".join(stale)
        )

    actual_outputs = [parse_deterministic_output(cell) for cell in executed_code]
    if actual_outputs != EXPECTED_OUTPUTS:
        raise NotebookRegressionError(
            "Deterministic notebook output regression detected: "
            + json.dumps(actual_outputs, sort_keys=True)
        )


def compare(source_path: str | Path, executed_path: str | Path) -> None:
    if Path(source_path).read_bytes() == Path(executed_path).read_bytes():
        raise NotebookRegressionError(
            "Executed snapshot is byte-identical to the unexecuted source"
        )
    validate_notebooks(load_notebook(source_path), load_notebook(executed_path))


def executed_semantics(notebook: dict[str, Any]) -> list[dict[str, Any]]:
    """Return the execution-relevant notebook representation."""

    semantics: list[dict[str, Any]] = []
    for cell in notebook.get("cells", []):
        item: dict[str, Any] = {
            "cell_type": cell.get("cell_type"),
            "id": cell.get("id"),
            "source": source_text(cell),
        }
        if cell.get("cell_type") == "code":
            item["execution_count"] = cell.get("execution_count")
            item["deterministic_output"] = parse_deterministic_output(cell)
        semantics.append(item)
    return semantics


def compare_executed_snapshots(
    source_path: str | Path,
    committed_path: str | Path,
    regenerated_path: str | Path,
) -> None:
    source = load_notebook(source_path)
    committed = load_notebook(committed_path)
    regenerated = load_notebook(regenerated_path)
    validate_notebooks(source, committed)
    validate_notebooks(source, regenerated)
    if executed_semantics(committed) != executed_semantics(regenerated):
        raise NotebookRegressionError(
            "Regenerated nbclient notebook is not semantically equivalent "
            "to the committed snapshot"
        )


def main(argv: list[str] | None = None) -> int:
    arguments = sys.argv[1:] if argv is None else argv
    if len(arguments) not in {2, 3}:
        raise SystemExit(
            "usage: compare_notebook_semantics.py SOURCE.ipynb "
            "COMMITTED_EXECUTED.ipynb [REGENERATED_EXECUTED.ipynb]"
        )
    try:
        if len(arguments) == 2:
            compare(arguments[0], arguments[1])
        else:
            compare_executed_snapshots(arguments[0], arguments[1], arguments[2])
    except NotebookRegressionError as error:
        raise SystemExit(str(error)) from error
    if len(arguments) == 2:
        print("[OK] notebook source, execution state, and deterministic outputs match")
    else:
        print("[OK] committed and regenerated nbclient notebooks are semantically equivalent")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
