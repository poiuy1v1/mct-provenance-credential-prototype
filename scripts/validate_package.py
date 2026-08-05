#!/usr/bin/env python3
"""Validate candidate manifest, checksums, path hygiene and package file set."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from pathlib import Path, PurePosixPath

MANIFEST_NAME = "MANIFEST.csv"
CHECKSUM_NAME = "CHECKSUMS_SHA256.txt"
FORBIDDEN_DIRECTORIES = {
    ".ipynb_checkpoints",
    ".mypy_cache",
    ".pytest_cache",
    ".venv",
    "__pycache__",
    "build",
    "generated",
}
CHECKSUM_PATTERN = re.compile(r"^([0-9a-f]{64})  (.+)$")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_relative_path(value: str) -> str:
    pure = PurePosixPath(value)
    if (
        not value
        or "\\" in value
        or pure.is_absolute()
        or pure.anchor
        or ".." in pure.parts
        or pure.as_posix() != value
    ):
        raise ValueError(f"Unsafe or non-canonical manifest path: {value!r}")
    return value


def is_git_metadata_path(path: Path, root: Path) -> bool:
    relative = path.relative_to(root)
    return ".git" in relative.parts


def inventory(root: Path) -> dict[str, Path]:
    files: dict[str, Path] = {}
    for path in sorted(root.rglob("*")):
        if is_git_metadata_path(path, root):
            continue
        relative = path.relative_to(root).as_posix()
        if path.is_symlink():
            raise ValueError(f"Symlink must not be packaged: {relative}")
        if path.is_dir():
            if path.name in FORBIDDEN_DIRECTORIES:
                raise ValueError(f"Forbidden package directory: {relative}")
            continue
        if path.suffix.lower() in {".pyc", ".pyo"}:
            raise ValueError(f"Compiled bytecode must not be packaged: {relative}")
        if path.name.endswith((".tmp.ipynb", ".ipynb~", ".bak")):
            raise ValueError(f"Temporary or backup file must not be packaged: {relative}")
        files[validate_relative_path(relative)] = path
    return files


def read_manifest(path: Path) -> dict[str, tuple[int, str]]:
    rows: dict[str, tuple[int, str]] = {}
    observed_order: list[str] = []
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != ["relative_path", "bytes", "sha256", "role"]:
            raise ValueError(f"Unexpected manifest columns: {reader.fieldnames}")
        for row in reader:
            relative = validate_relative_path(row["relative_path"])
            if relative in rows:
                raise ValueError(f"Duplicate manifest entry: {relative}")
            observed_order.append(relative)
            if not row["role"]:
                raise ValueError(f"Empty manifest role: {relative}")
            digest = row["sha256"]
            if not re.fullmatch(r"[0-9a-f]{64}", digest):
                raise ValueError(f"Invalid manifest SHA-256: {relative}")
            rows[relative] = (int(row["bytes"]), digest)
    if observed_order != sorted(observed_order):
        raise ValueError("Manifest entries are not sorted by relative path")
    return rows


def read_checksums(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    observed_order: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line:
            continue
        match = CHECKSUM_PATTERN.fullmatch(line)
        if not match:
            raise ValueError(f"Invalid checksum line: {line!r}")
        digest, relative = match.groups()
        relative = validate_relative_path(relative)
        if relative in values:
            raise ValueError(f"Duplicate checksum entry: {relative}")
        observed_order.append(relative)
        values[relative] = digest
    if observed_order != sorted(observed_order):
        raise ValueError("Checksum entries are not sorted by relative path")
    return values


def validate(root: Path) -> dict[str, object]:
    root = root.resolve(strict=True)
    files = inventory(root)
    manifest_path = root / MANIFEST_NAME
    checksum_path = root / CHECKSUM_NAME
    if not manifest_path.is_file() or not checksum_path.is_file():
        raise ValueError("Candidate manifest or checksum file is missing")

    manifest = read_manifest(manifest_path)
    expected_manifest = set(files) - {MANIFEST_NAME, CHECKSUM_NAME}
    if set(manifest) != expected_manifest:
        raise ValueError(
            "Manifest file set mismatch: "
            f"missing={sorted(expected_manifest - set(manifest))}, "
            f"unexpected={sorted(set(manifest) - expected_manifest)}"
        )
    for relative, (size, digest) in manifest.items():
        path = files[relative]
        if path.stat().st_size != size or sha256(path) != digest:
            raise ValueError(f"Manifest size/hash mismatch: {relative}")

    checksums = read_checksums(checksum_path)
    expected_checksums = set(files) - {CHECKSUM_NAME}
    if set(checksums) != expected_checksums:
        raise ValueError(
            "Checksum file set mismatch: "
            f"missing={sorted(expected_checksums - set(checksums))}, "
            f"unexpected={sorted(set(checksums) - expected_checksums)}"
        )
    for relative, digest in checksums.items():
        if sha256(files[relative]) != digest:
            raise ValueError(f"Checksum mismatch: {relative}")

    return {
        "candidate_root": root.name,
        "checksum_entries": len(checksums),
        "manifest_entries": len(manifest),
        "overall_status": "PASS",
        "symlinks": 0,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate-root", default=".")
    arguments = parser.parse_args()
    print(json.dumps(validate(Path(arguments.candidate_root)), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
