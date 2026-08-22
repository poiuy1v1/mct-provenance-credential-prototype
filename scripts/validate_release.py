#!/usr/bin/env python3
"""Deterministic offline schema, policy, score, and metadata validator."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import sys
from pathlib import Path, PurePosixPath
from typing import Any, Callable

from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource


ROOT = Path(__file__).parents[1].resolve()
MOF_DIR = ROOT / "MOF_WorkedExample"
MOF_SCHEMA_REF = "MOF_WorkedExample/mof_research_object_profile.schema.json"
CANDIDATE_VERSION = "0.3.5-alpha"
PREVIOUS_VERSION_DOI = "10.5281/zenodo.21826427"
HISTORICAL_V033_DOI = "10.5281/zenodo.21643012"
CANONICAL_EVENT_IDS = [f"MCT-EVT-{index:04d}" for index in range(1, 7)]
STALE_VOCABULARY = {"NOT_ESTABLISHED" + "_BY_FROZEN_SNAPSHOT"}
STAGE_STALE_PUBLIC_MARKERS = (
    "Current local " + "candidate version",
    "local implementation " + "candidate only",
    "LOCAL_" + "CANDIDATE_ONLY",
    "candidate_" + "stage",
    "remote_ci_" + "executed",
    "unrun cross-platform CI " + "configuration",
)


def load_json(relative_path: str | Path) -> Any:
    path = Path(relative_path)
    if not path.is_absolute():
        path = ROOT / path
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_contribution_validator() -> Draft202012Validator:
    """Build an offline validator whose relative MOF reference is locally supplied."""

    schema = load_json("contribution_schema.json")
    profile_schema = load_json(
        "MOF_WorkedExample/mof_research_object_profile.schema.json"
    )
    Draft202012Validator.check_schema(schema)
    Draft202012Validator.check_schema(profile_schema)

    def retrieve(uri: str) -> Resource[Any]:
        if uri.replace(chr(92), "/").lstrip("./") == MOF_SCHEMA_REF:
            return Resource.from_contents(profile_schema)
        raise LookupError(f"Offline schema resource is not packaged: {uri}")

    registry = Registry(retrieve=retrieve)
    return Draft202012Validator(
        schema,
        registry=registry,
        format_checker=FormatChecker(),
    )


def safe_evidence_path(value: str, root: Path) -> Path:
    pure = PurePosixPath(value)
    if (
        not value
        or chr(92) in value
        or ":" in value
        or pure.is_absolute()
        or pure.anchor
        or ".." in pure.parts
        or pure.as_posix() != value
    ):
        raise ValueError(f"Unsafe evidence path: {value!r}")
    resolved_root = root.resolve(strict=True)
    candidate = resolved_root.joinpath(*pure.parts).resolve(strict=False)
    try:
        candidate.relative_to(resolved_root)
    except ValueError as error:
        raise ValueError(f"Evidence path escapes candidate root: {value!r}") from error
    return candidate


def validate_event_policy(event: dict[str, Any], root: Path = ROOT) -> dict[str, Any]:
    """Apply bounded offline file, source-link, and scientific-boundary policy."""

    validation = event["validation"]
    evidence = event["evidence"]
    files = evidence.get("files", [])
    claims_presence = validation["evidence_file_status"] == "evidence_file_present"
    claims_integrity = (
        validation["file_integrity_status"] == "file_integrity_confirmed"
    )
    if (claims_presence or claims_integrity) and not files:
        raise ValueError(
            f"{event['event_id']} claims packaged evidence without evidence.files"
        )
    if claims_integrity and not claims_presence:
        raise ValueError(
            f"{event['event_id']} confirms integrity without file-presence status"
        )

    seen_paths: set[str] = set()
    seen_hashes: set[str] = set()
    checked = 0
    for item in files:
        relative = item["path"]
        digest = item["sha256"]
        if relative in seen_paths:
            raise ValueError(f"Duplicate evidence path: {relative}")
        if digest in seen_hashes:
            raise ValueError(f"Duplicate evidence hash: {digest}")
        seen_paths.add(relative)
        seen_hashes.add(digest)
        path = safe_evidence_path(relative, root)
        if claims_presence and not path.is_file():
            raise ValueError(f"Missing evidence file: {relative}")
        if claims_integrity:
            if not path.is_file():
                raise ValueError(f"Cannot hash missing evidence file: {relative}")
            if sha256(path) != digest:
                raise ValueError(f"Evidence hash mismatch: {relative}")
            checked += 1

    if validation["source_link_status"] == "source_link_resolved":
        raise ValueError(
            f"Offline validator cannot claim source resolution: {event['event_id']}"
        )
    require(
        validation["scientific_assessment"]["status"] == "not_reviewed",
        f"Synthetic event claims scientific review: {event['event_id']}",
    )
    return {
        "evidence_hashes_checked": checked,
        "file_integrity_is_scientific_review": False,
        "scientific_assessment_status": "not_reviewed",
        "source_resolution_performed": False,
    }


def _load_mof_validator_module() -> Any:
    path = MOF_DIR / "validate_mof_worked_example.py"
    spec = importlib.util.spec_from_file_location("paper1_mof_validator", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Cannot load packaged MOF validator")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def check_schema_and_events() -> dict[str, Any]:
    events = load_json("data/example_contributions.json")
    schema = load_json("contribution_schema.json")
    require(schema.get("type") == "array", "Contribution schema is not array-based")
    validator = build_contribution_validator()
    validator.validate(events)
    require(len(events) == 6, "Expected exactly six synthetic contribution events")
    require(
        [event["event_id"] for event in events] == CANONICAL_EVENT_IDS,
        "Canonical event ID/order drift",
    )
    require(
        all(event["schema_version"] == CANDIDATE_VERSION for event in events),
        "Contribution event version mismatch",
    )
    require(
        "domain_profile" in events[0]["research_object"],
        "First event does not exercise the MOF branch",
    )
    require(
        all(
            "domain_profile" not in event["research_object"] for event in events[1:]
        ),
        "A non-first canonical event unexpectedly exercises the MOF branch",
    )
    validator.validate([events[0]])
    validator.validate([events[1]])

    standalone = load_json("MOF_WorkedExample/synthetic_uio66_research_object.json")
    require(
        events[0]["research_object"]["domain_profile"] == standalone,
        "Inline MOF profile is not JSON-value identical to the standalone profile",
    )
    policy_results = [validate_event_policy(event) for event in events]
    require(
        all(event["issued_credential"]["non_transferable"] for event in events),
        "Transferable credential detected",
    )
    require(
        all(event["issued_credential"]["locked"] for event in events),
        "Unlocked credential detected",
    )
    return {
        "candidate_version": CANDIDATE_VERSION,
        "canonical_event_ids": CANONICAL_EVENT_IDS,
        "contribution_events": len(events),
        "generic_branch": "PASS",
        "inline_standalone_profile_identity": "PASS",
        "mof_branch_relative_ref": "PASS",
        "non_transferable_boundary": "PASS",
        "offline_event_policy": policy_results,
        "scientific_assessment_boundary": "PASS",
        "top_level_array_api": "PASS",
    }


def check_mof_profile() -> dict[str, Any]:
    schema = load_json("MOF_WorkedExample/mof_research_object_profile.schema.json")
    instance = load_json("MOF_WorkedExample/synthetic_uio66_research_object.json")
    Draft202012Validator(
        schema,
        format_checker=FormatChecker(),
    ).validate(instance)
    module = _load_mof_validator_module()
    result = module.validate_instance(instance, MOF_DIR)
    require(instance["profile_version"] == CANDIDATE_VERSION, "MOF version drift")
    require(
        instance["validation"]["scientific_assessment"]["status"]
        == "not_reviewed",
        "MOF profile claims scientific review",
    )
    require(
        instance["source_anchoring"]["repository_url"]
        == "https://github.com/poiuy1v1/mct-provenance-credential-prototype",
        "MOF profile does not use the stable repository-root URL",
    )
    return {
        "mof_profile": "PASS",
        "policy": result,
        "synthetic_evidence_files": [
            item["file"] for item in instance["characterisation_evidence"]
        ],
    }


def check_score() -> dict[str, Any]:
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    import mct_reward_simulation as scoring

    require(scoring.__version__ == CANDIDATE_VERSION, "Scoring version drift")
    events = scoring.load_events("data/example_contributions.json", ROOT)
    rows = scoring.score_events(events, 365.0)
    run_summary = scoring.summary(rows, "data/example_contributions.json", 365.0)
    require(
        [row["event_id"] for row in rows] == CANONICAL_EVENT_IDS,
        "Scored event ID/order drift",
    )
    require(
        run_summary["diagnostic_score_sum"] == 23.0324,
        "Authoritative diagnostic score drift",
    )
    require(len(rows) == 6, "Diagnostic row-count drift")
    return {
        "authoritative_diagnostic_score": run_summary["diagnostic_score_sum"],
        "diagnostic_rows": len(rows),
        "ranking_output": "ABSENT",
        "scoring_version": scoring.__version__,
    }


def _zenodo_dois(text: str) -> set[str]:
    return set(re.findall(r"10\.5281/zenodo\.\d+", text))


def check_metadata() -> dict[str, Any]:
    citation = (ROOT / "CITATION.cff").read_text(encoding="utf-8")
    zenodo = load_json(".zenodo.json")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    reproducibility = (ROOT / "REPRODUCIBILITY.md").read_text(encoding="utf-8")
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    release_notes = (ROOT / "RELEASE_NOTES_v0.3.5-alpha.md").read_text(
        encoding="utf-8"
    )

    require('version: "0.3.5-alpha"' in citation, "CITATION.cff version mismatch")
    require(not re.search(r"(?m)^doi:", citation), "CFF fabricates a DOI")
    require(
        not re.search(r"(?m)^date-released:", citation),
        "CFF fabricates a release date",
    )
    require(zenodo.get("version") == CANDIDATE_VERSION, "Zenodo version mismatch")
    require("doi" not in zenodo, "Zenodo metadata fabricates a DOI")
    require(
        "publication_date" not in zenodo,
        "Zenodo metadata fabricates a publication date",
    )
    require(
        zenodo.get("related_identifiers")
        == [
            {
                "identifier": PREVIOUS_VERSION_DOI,
                "relation": "isNewVersionOf",
                "scheme": "doi",
            }
        ],
        "Zenodo previous-version relation mismatch",
    )
    require(
        "Current version: **`v0.3.5-alpha`**." in readme,
        "README lacks the versioned-source statement",
    )
    require(
        release_notes.startswith("# v0.3.5-alpha"),
        "v0.3.5 release notes heading mismatch",
    )
    combined = "\n".join(
        [readme, reproducibility, changelog, release_notes, json.dumps(zenodo)]
    )
    lower = " ".join(combined.lower().split())
    require(
        "restoration" in lower and "v0.3.4" in lower,
        "Restoration/integration history is unclear",
    )
    require(
        "source metadata does not embed" in lower,
        "Durable source-metadata DOI/date boundary is absent",
    )
    require(
        "live remote ci execution status is external evidence" in lower,
        "External live-CI evidence boundary is absent",
    )
    require(
        "thin synthetic mof research-object adapter" in lower,
        "Safe MOF positioning is absent",
    )
    require("does not claim mpif" in lower, "MPIF non-claim is absent")
    require("not a universal" in lower, "Universal-standard non-claim is absent")
    observed_dois = _zenodo_dois(combined + "\n" + citation)
    require(
        observed_dois <= {PREVIOUS_VERSION_DOI, HISTORICAL_V033_DOI},
        "An unissued v0.3.5 Zenodo DOI appears in source metadata",
    )
    stage_stale_matches = [
        marker for marker in STAGE_STALE_PUBLIC_MARKERS if marker.lower() in lower
    ]
    require(
        not stage_stale_matches,
        "Stage-stale public assertions remain: " + ", ".join(stage_stale_matches),
    )
    return {
        "release_stage": "VERSIONED_SOURCE",
        "current_version_doi": "NOT_EMBEDDED_IN_SOURCE_METADATA",
        "current_version_release_date": "NOT_EMBEDDED_IN_SOURCE_METADATA",
        "metadata_state": "VERSIONED_SOURCE_METADATA",
        "previous_version_doi": PREVIOUS_VERSION_DOI,
    }


def check_workflow() -> dict[str, Any]:
    workflow = (ROOT / ".github/workflows/smoke-test.yml").read_text(encoding="utf-8")
    require("ubuntu-latest" in workflow, "Ubuntu CI configuration is missing")
    require("windows-latest" in workflow, "Windows CI configuration is missing")
    require(
        "python scripts/run_smoke_tests.py --notebook-backend nbclient" in workflow,
        "CI no longer invokes the authoritative smoke workflow",
    )
    return {
        "remote_ci_execution_claim": "EXTERNAL_TO_PACKAGE",
        "ubuntu_configuration": "PRESENT",
        "windows_configuration": "PRESENT",
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
        if any(
            part in {"__pycache__", ".git", ".venv", "generated"}
            for part in path.parts
        ):
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
        ("workflow", check_workflow),
        ("stale_vocabulary", check_stale_vocabulary),
    ]
    details: dict[str, Any] = {}
    failures: list[dict[str, str]] = []
    for name, check in checks:
        try:
            details[name] = check()
        except Exception as error:
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
