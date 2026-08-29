#!/usr/bin/env python3
"""Bounded offline validation for the synthetic UiO-66 worked example."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import urlparse

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parent
PROFILE_VERSION = "0.3.6-alpha"
ID_RE = re.compile(
    r"^(did:[a-z0-9]+:[A-Za-z0-9._:%-]+|"
    r"https://orcid.org/\d{4}-\d{4}-\d{4}-\d{3}[0-9X])$"
)


class ValidationPolicyError(ValueError):
    """Raised when the synthetic worked-example project policy is violated."""


def load_json(path: str | Path) -> object:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _local_evidence_path(root: Path, relative_path: str) -> Path:
    root = root.resolve()
    candidate = (root / relative_path).resolve()
    try:
        candidate.relative_to(root)
    except ValueError as error:
        raise ValidationPolicyError(
            f"evidence path escapes worked-example root: {relative_path}"
        ) from error
    return candidate


def _reject_offline_resolution(status: str, context: str) -> None:
    if status == "source_link_resolved":
        raise ValidationPolicyError(
            f"offline validator cannot claim {context} source resolution"
        )


def validate_instance(instance: dict[str, object], root: Path = ROOT) -> dict[str, str]:
    """Validate schema, local bytes and project policy without network access."""

    root = Path(root)
    schema = load_json(root / "mof_research_object_profile.schema.json")
    Draft202012Validator(
        schema,
        format_checker=FormatChecker(),
    ).validate(instance)

    if instance["profile_version"] != PROFILE_VERSION:
        raise ValidationPolicyError("worked-example profile version mismatch")

    validation = instance["validation"]
    contributor_id = validation["contributor_id"]
    verifier_id = validation["verifier_id"]
    if not ID_RE.fullmatch(contributor_id) or not ID_RE.fullmatch(verifier_id):
        raise ValidationPolicyError("invalid contributor/verifier identifier")
    if validation["independent_verifier"] and contributor_id == verifier_id:
        raise ValidationPolicyError(
            "project policy requires distinct contributor and verifier identities "
            "for this synthetic independently-verified worked example"
        )

    conflict = validation["conflict_declaration"]
    if not conflict["declared"] and not re.search(
        r"\b(no|none|not)\b", conflict["details"], re.IGNORECASE
    ):
        raise ValidationPolicyError("explicit no-conflict wording required")

    repository_url = instance["source_anchoring"]["repository_url"]
    parsed_url = urlparse(repository_url)
    if parsed_url.scheme != "https" or not parsed_url.netloc:
        raise ValidationPolicyError("repository_url must be absolute HTTPS")
    _reject_offline_resolution(validation["source_link_status"], "profile")

    evidence_paths: set[str] = set()
    evidence_hashes: set[str] = set()
    evidence_records = instance["characterisation_evidence"]
    for evidence in evidence_records:
        relative_path = evidence["file"]
        expected_hash = evidence["sha256"]
        if relative_path in evidence_paths:
            raise ValidationPolicyError("duplicate evidence file path")
        if expected_hash in evidence_hashes:
            raise ValidationPolicyError("duplicate evidence hash")
        evidence_paths.add(relative_path)
        evidence_hashes.add(expected_hash)

        local_path = _local_evidence_path(root, relative_path)
        claims_presence = evidence["file_status"] == "evidence_file_present"
        claims_integrity = evidence["integrity_status"] == "file_integrity_confirmed"
        if (claims_presence or claims_integrity) and not local_path.is_file():
            raise ValidationPolicyError(f"missing evidence file: {relative_path}")
        if claims_integrity:
            actual_hash = hashlib.sha256(local_path.read_bytes()).hexdigest()
            if actual_hash != expected_hash:
                raise ValidationPolicyError(f"hash mismatch: {relative_path}")
        _reject_offline_resolution(evidence["source_link_status"], "evidence")

    if validation["evidence_file_status"] == "evidence_file_present" and any(
        evidence["file_status"] != "evidence_file_present"
        for evidence in evidence_records
    ):
        raise ValidationPolicyError(
            "aggregate evidence-file status conflicts with evidence records"
        )
    if validation["file_integrity_status"] == "file_integrity_confirmed" and any(
        evidence["integrity_status"] != "file_integrity_confirmed"
        for evidence in evidence_records
    ):
        raise ValidationPolicyError(
            "aggregate file-integrity status conflicts with evidence records"
        )

    scientific_status = validation["scientific_assessment"]["status"]
    if scientific_status != "not_reviewed":
        raise ValidationPolicyError(
            "synthetic worked example must remain scientifically not_reviewed"
        )
    if not instance["reported_outcome"]["state"].startswith("reported_"):
        raise ValidationPolicyError("unreviewed outcomes must use reported_* state")

    return {
        "schema": "PASS",
        "identity_project_policy": "PASS",
        "conflict": "PASS",
        "source_link_offline_policy": "PASS",
        "evidence_files": "PASS",
        "hashes": "PASS",
        "scientific_boundary": "PASS",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--instance",
        default="synthetic_uio66_research_object.json",
    )
    parser.add_argument("--json", action="store_true")
    arguments = parser.parse_args()
    instance_path = Path(arguments.instance)
    if not instance_path.is_absolute():
        instance_path = ROOT / instance_path
    result = validate_instance(load_json(instance_path))
    if arguments.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("PASS: bounded offline v0.3.6-alpha MOF worked-example validation")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
