#!/usr/bin/env python3
"""Reject internal workflow/review artifacts from public release candidates."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


FORBIDDEN_DIRECTORY_NAMES = {"audit"}
FORBIDDEN_FILENAME_TOKENS = {
    "AUDIT",
    "ATTESTATION",
    "CONVERSATION",
    "EXECUTIVE_STATUS",
    "GATE_REPORT",
    "HANDOFF",
    "PROMPT",
    "REVIEW_RESULT",
    "TRANSCRIPT",
}
INTERNAL_CONTENT_MARKERS = {
    "----- BEGIN ATTACHED PROMPT -----",
    "COMPLETE USER-VISIBLE TASK PROMPT",
    "EXECUTION_STATUS =",
    "NEXT_ACTION_AUTHORIZED =",
    "PASS_INDEPENDENT_",
    "SIMULATION_IDENTITY =",
}
CONTENT_SCAN_EXEMPTIONS = {
    "scripts/check_release_neutrality.py",
    "tests/test_release_neutrality.py",
}
TEXT_SUFFIXES = {
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


class ReleaseNeutralityError(ValueError):
    """Raised when a public candidate contains an internal workflow artifact."""


def validate_public_release_tree(root: str | Path) -> dict[str, object]:
    root_path = Path(root).resolve(strict=True)
    issues: list[str] = []
    files_scanned = 0
    text_files_scanned = 0

    for path in sorted(root_path.rglob("*")):
        if ".git" in path.relative_to(root_path).parts:
            continue
        relative = path.relative_to(root_path).as_posix()
        if path.is_symlink():
            issues.append(f"symlink:{relative}")
            continue
        if any(part.lower() in FORBIDDEN_DIRECTORY_NAMES for part in Path(relative).parts):
            issues.append(f"forbidden-directory:{relative}")
        if not path.is_file():
            continue
        files_scanned += 1
        upper_name = path.name.upper()
        matched_tokens = sorted(
            token for token in FORBIDDEN_FILENAME_TOKENS if token in upper_name
        )
        if matched_tokens:
            issues.append(
                f"forbidden-filename:{relative}:{','.join(matched_tokens)}"
            )
        if relative in CONTENT_SCAN_EXEMPTIONS or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        text_files_scanned += 1
        text = path.read_text(encoding="utf-8", errors="replace")
        matched_markers = sorted(
            marker for marker in INTERNAL_CONTENT_MARKERS if marker in text
        )
        if matched_markers:
            issues.append(
                f"internal-content:{relative}:{'|'.join(matched_markers)}"
            )

    if issues:
        raise ReleaseNeutralityError(
            "Public-release neutrality failure: " + "; ".join(issues)
        )
    return {
        "files_scanned": files_scanned,
        "forbidden_artifacts": 0,
        "overall_status": "PASS",
        "text_files_scanned": text_files_scanned,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate-root", default=".")
    arguments = parser.parse_args()
    print(
        json.dumps(
            validate_public_release_tree(arguments.candidate_root),
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
