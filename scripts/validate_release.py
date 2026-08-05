#!/usr/bin/env python3
"""Deterministic schema and boundary-policy validator."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Callable

import jsonschema

ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT))
CANDIDATE_VERSION = "0.3.4-alpha"
HISTORICAL_DOI = "10.5281/zenodo.21643012"
STALE_VOCABULARY = {"NOT_ESTABLISHED" + "_BY_FROZEN_SNAPSHOT"}


def load_json(relative_path: str) -> Any:
    return json.loads((ROOT / relative_path).read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def check_schema_and_events() -> dict[str, Any]:
    events = load_json("data/example_contributions.json")
    schema = load_json("contribution_schema.json")
    jsonschema.Draft202012Validator(schema).validate(events)
    require(len(events) == 6, "Expected six synthetic contribution events")
    require(
        len({event["event_id"] for event in events}) == len(events),
        "Duplicate event_id detected",
    )
    require(
        all(event["schema_version"] == CANDIDATE_VERSION for event in events),
        "Contribution event version mismatch",
    )
    require(
        all(event["issued_credential"]["non_transferable"] for event in events),
        "Transferable credential detected",
    )
    require(
        all(event["issued_credential"]["locked"] for event in events),
        "Unlocked credential detected",
    )
    require(
        all(
            event["validation"]["scientific_assessment"]["status"]
            == "not_reviewed"
            for event in events
        ),
        "Distributed fixture claims scientific review",
    )
    require(
        all(
            event["contributor"]["orcid"]
            != event["validation"]["verifier"]["identifier"]
            for event in events
        ),
        "Self-verification detected",
    )
    return {
        "candidate_version": CANDIDATE_VERSION,
        "contribution_events": len(events),
        "non_transferable_boundary": "PASS",
        "scientific_assessment_boundary": "PASS",
        "self_verification_rejection": "PASS",
    }


def check_mof_profile() -> dict[str, Any]:
    schema = load_json("MOF_WorkedExample/mof_research_object_profile.schema.json")
    instance = load_json("MOF_WorkedExample/synthetic_uio66_research_object.json")
    jsonschema.Draft202012Validator(schema).validate(instance)
    require(instance["synthetic_example"] is True, "MOF profile is not synthetic")
    evidence_files = sorted(
        path.name
        for path in (ROOT / "MOF_WorkedExample" / "evidence").iterdir()
        if path.is_file()
    )
    require(len(evidence_files) == 2, "Expected two packaged synthetic evidence files")
    return {
        "mof_profile": "PASS",
        "synthetic_evidence_files": evidence_files,
    }


def check_score() -> dict[str, Any]:
    import mct_reward_simulation as scoring

    events = scoring.load_events("data/example_contributions.json", ROOT)
    rows = scoring.score_events(events, 365.0)
    run_summary = scoring.summary(rows, "data/example_contributions.json", 365.0)
    require(
        run_summary["diagnostic_score_sum"] == 23.0324,
        "Authoritative diagnostic score drift",
    )
    require(len(rows) == 6, "Diagnostic row-count drift")
    return {
        "authoritative_diagnostic_score": run_summary["diagnostic_score_sum"],
        "diagnostic_rows": len(rows),
        "ranking_output": "ABSENT",
    }


def check_metadata() -> dict[str, Any]:
    citation = (ROOT / "CITATION.cff").read_text(encoding="utf-8")
    zenodo = load_json(".zenodo.json")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    require(
        'version: "0.3.4-alpha"' in citation,
        "CITATION.cff candidate version mismatch",
    )
    require(not re.search(r"(?m)^doi:", citation), "Candidate CFF fabricates a DOI")
    require(
        not re.search(r"(?m)^date-released:", citation),
        "Candidate CFF fabricates a release date",
    )
    require(zenodo.get("version") == CANDIDATE_VERSION, "Zenodo version mismatch")
    require("doi" not in zenodo, "Candidate Zenodo metadata fabricates a DOI")
    require(
        "publication_date" not in zenodo,
        "Candidate Zenodo metadata fabricates a publication date",
    )
    require(
        "not been pushed, tagged, released, or archived" in readme,
        "README lacks unpublished-candidate boundary",
    )
    require(HISTORICAL_DOI in readme, "README omits historical provenance DOI")
    return {
        "candidate_doi": "ABSENT",
        "candidate_release_date": "ABSENT",
        "historical_v0.3.3_doi": HISTORICAL_DOI,
        "metadata_boundary": "PASS",
    }


def check_stale_vocabulary() -> dict[str, Any]:
    suffixes = {".py", ".json", ".md", ".csv", ".yml", ".yaml", ".cff", ".ipynb"}
    intentional_negative_fixtures = {
        "scripts/compare_notebook_semantics.py",
        "scripts/validate_release.py",
        "tests/test_notebook_regression.py",
    }
    matches: list[str] = []
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in suffixes:
            continue
        if any(part in {"__pycache__", ".git", ".venv"} for part in path.parts):
            continue
        relative_path = path.relative_to(ROOT).as_posix()
        if relative_path in intentional_negative_fixtures:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for token in STALE_VOCABULARY:
            if token in text:
                matches.append(relative_path)
    require(not matches, "Stale validation vocabulary found: " + ", ".join(matches))
    return {"stale_validation_vocabulary": "ABSENT"}


def run_checks() -> dict[str, Any]:
    checks: list[tuple[str, Callable[[], dict[str, Any]]]] = [
        ("schema_and_events", check_schema_and_events),
        ("mof_profile", check_mof_profile),
        ("score", check_score),
        ("metadata", check_metadata),
        ("stale_vocabulary", check_stale_vocabulary),
    ]
    details: dict[str, Any] = {}
    failures: list[dict[str, str]] = []
    for name, check in checks:
        try:
            details[name] = check()
        except Exception as error:  # surfaced deterministically in the report
            failures.append({"check": name, "error": str(error)})
    return {
        "candidate_version": CANDIDATE_VERSION,
        "failures": failures,
        "overall_status": "PASS" if not failures else "FAIL",
        "results": details,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    arguments = parser.parse_args(argv)
    result = run_checks()
    if arguments.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"release validation: {result['overall_status']}")
        for failure in result["failures"]:
            print(f"- {failure['check']}: {failure['error']}")
    return 0 if result["overall_status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
