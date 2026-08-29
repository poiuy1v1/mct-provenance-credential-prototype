#!/usr/bin/env python3
"""Synthetic diagnostic contribution scoring for the v0.3.6-alpha candidate.

The constants, multiplicative score equation, canonical event ordering, and
diagnostic labels are retained unchanged from the frozen v0.3.4-alpha
execution baseline. The v0.3.5 semantic restoration adds only non-scoring
provenance fields.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import math
import os
import statistics
from collections import Counter, defaultdict
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any, Iterable

__version__ = "0.3.6-alpha"

BASE_WEIGHTS = {
    "mof_dataset_deposition": 10.0,
    "negative_synthesis_record": 8.0,
    "replication_study": 12.0,
    "peer_validation": 7.0,
    "sample_sharing": 9.0,
    "model_provenance_record": 6.0,
    "metadata_curation": 4.0,
}

QUALITY_WEIGHTS = {
    "novelty": 0.1875,
    "reusability": 0.3125,
    "reproducibility": 0.3125,
    "effort_proxy": 0.1250,
    "negative_result_value": 0.0625,
}

VALIDATION_MULTIPLIERS = {
    "metadata_status": {
        "not_checked": 0.60,
        "metadata_validated": 1.00,
        "metadata_invalid": 0.00,
    },
    "evidence_file_status": {
        "not_checked": 0.90,
        "evidence_file_present": 1.00,
        "evidence_file_missing": 0.00,
    },
    "file_integrity_status": {
        "not_checked": 0.90,
        "file_integrity_confirmed": 1.00,
        "file_integrity_failed": 0.00,
    },
    "source_link_status": {
        "not_checked": 0.85,
        "source_link_recorded": 0.90,
        "source_link_resolved": 1.00,
        "source_link_failed": 0.00,
    },
    "scientific_assessment_status": {
        "not_reviewed": 1.00,
        "simulated_review": 1.00,
        "scientifically_reviewed": 1.05,
        "scientifically_disputed": 0.00,
    },
}

DISCLAIMER = (
    "Diagnostic event scores are synthetic software-test outputs only. They are "
    "not prices, token balances, researcher rankings, hiring or grant metrics, "
    "authorship criteria, governance entitlements, or evidence that a scientific "
    "claim is true."
)


def parse_time(value: str) -> dt.datetime:
    return dt.datetime.fromisoformat(
        value[:-1] + "+00:00" if value.endswith("Z") else value
    )


def canonical_event_key(event: dict[str, Any]) -> tuple[dt.datetime, str]:
    """Return the frozen deterministic order used for duplicate handling."""

    return parse_time(event["validation"]["timestamp_utc"]), event["event_id"]


def half_life_decay(
    event_time: dt.datetime, reference_time: dt.datetime, half_life_days: float
) -> float:
    age_days = max(
        0.0, (reference_time - event_time).total_seconds() / 86400.0
    )
    return math.exp(-math.log(2.0) * age_days / half_life_days)


def quality_score(scoring_inputs: dict[str, Any]) -> float:
    return sum(
        float(scoring_inputs.get(component, 0.0)) * weight
        for component, weight in QUALITY_WEIGHTS.items()
    )


def _validated_input_path(
    input_file: str | Path, authorised_root: str | Path | None = None
) -> tuple[str, Path]:
    """Return a portable label and a contained concrete input path.

    Both Windows and POSIX flavours are inspected regardless of the host OS.
    This prevents a Windows path from being mistaken for a relative path on
    POSIX (and vice versa), while still accepting either separator for a safe
    project-relative input label.
    """

    raw = os.fspath(input_file)
    if not isinstance(raw, str) or not raw or "\x00" in raw:
        raise ValueError("input_file must be a non-empty, NUL-free path")

    windows_path = PureWindowsPath(raw)
    posix_path = PurePosixPath(raw)
    if (
        windows_path.drive
        or windows_path.root
        or windows_path.anchor
        or windows_path.is_absolute()
    ):
        raise ValueError("input_file must not use a Windows drive, root, or UNC path")
    if posix_path.root or posix_path.anchor or posix_path.is_absolute():
        raise ValueError("input_file must not use a POSIX absolute path")
    if ".." in windows_path.parts or ".." in posix_path.parts:
        raise ValueError("input_file must not contain parent traversal")

    portable_path = PurePosixPath(raw.replace("\\", "/"))
    parts = tuple(part for part in portable_path.parts if part not in {"", "."})
    if not parts:
        raise ValueError("input_file must identify a project-relative file")
    if ".." in parts:
        raise ValueError("input_file must not contain parent traversal")

    root = Path.cwd() if authorised_root is None else Path(authorised_root)
    root = root.resolve(strict=True)
    concrete = root.joinpath(*parts).resolve(strict=False)
    try:
        concrete.relative_to(root)
    except ValueError as error:
        raise ValueError("input_file must resolve inside the authorised root") from error

    return PurePosixPath(*parts).as_posix(), concrete


def load_events(
    path: str | Path, authorised_root: str | Path | None = None
) -> list[dict[str, Any]]:
    _, concrete = _validated_input_path(path, authorised_root)
    if not concrete.is_file():
        raise FileNotFoundError(f"Input file does not exist: {stable_input_label(path, authorised_root)}")
    return json.loads(concrete.read_text(encoding="utf-8"))


def validation_components(validation: dict[str, Any]) -> dict[str, float]:
    states = {
        "metadata_status": validation["metadata_status"],
        "evidence_file_status": validation["evidence_file_status"],
        "file_integrity_status": validation["file_integrity_status"],
        "source_link_status": validation["source_link_status"],
        "scientific_assessment_status": validation["scientific_assessment"][
            "status"
        ],
    }
    return {
        field: VALIDATION_MULTIPLIERS[field][state]
        for field, state in states.items()
    }


def duplicate_penalties(events: Iterable[dict[str, Any]]) -> dict[str, float]:
    """Calculate the inherited penalty in canonical timestamp/event-id order."""

    seen: Counter[tuple[str, str, str]] = Counter()
    penalties: dict[str, float] = {}
    for event in sorted(events, key=canonical_event_key):
        key = (
            event["contributor"]["orcid"],
            event["research_object"]["material_id"],
            event["contribution_type"],
        )
        seen[key] += 1
        penalty = max(0.20, 1.0 - 0.15 * (seen[key] - 1))
        if event["scoring_inputs"].get("anti_spam_flag"):
            penalty *= 0.60
        penalties[event["event_id"]] = penalty
    return penalties


def score_events(
    events: Iterable[dict[str, Any]], half_life_days: float = 365.0
) -> list[dict[str, Any]]:
    ordered_events = sorted(list(events), key=canonical_event_key)
    if not ordered_events:
        raise ValueError("At least one contribution event is required")
    if half_life_days <= 0:
        raise ValueError("half_life_days must be positive")

    reference_time = max(
        parse_time(event["validation"]["timestamp_utc"])
        for event in ordered_events
    )
    penalties = duplicate_penalties(ordered_events)
    rows: list[dict[str, Any]] = []

    for event in ordered_events:
        validation = event["validation"]
        components = validation_components(validation)
        validation_multiplier = math.prod(components.values())
        quality = quality_score(event["scoring_inputs"])
        decay = half_life_decay(
            parse_time(validation["timestamp_utc"]),
            reference_time,
            half_life_days,
        )
        base_weight = BASE_WEIGHTS[event["contribution_type"]]
        penalty = penalties[event["event_id"]]
        score = base_weight * quality * validation_multiplier * decay * penalty

        rows.append(
            {
                "event_id": event["event_id"],
                "credential_id": event["issued_credential"]["credential_id"],
                "contributor_orcid": event["contributor"]["orcid"],
                "material_id": event["research_object"]["material_id"],
                "contribution_type": event["contribution_type"],
                "metadata_status": validation["metadata_status"],
                "evidence_file_status": validation["evidence_file_status"],
                "file_integrity_status": validation["file_integrity_status"],
                "source_link_status": validation["source_link_status"],
                "scientific_assessment_status": validation[
                    "scientific_assessment"
                ]["status"],
                "metadata_multiplier": round(components["metadata_status"], 4),
                "evidence_file_multiplier": round(
                    components["evidence_file_status"], 4
                ),
                "file_integrity_multiplier": round(
                    components["file_integrity_status"], 4
                ),
                "source_link_multiplier": round(
                    components["source_link_status"], 4
                ),
                "scientific_assessment_multiplier": round(
                    components["scientific_assessment_status"], 4
                ),
                "composite_validation_multiplier": round(
                    validation_multiplier, 4
                ),
                "base_weight": round(base_weight, 4),
                "quality_score": round(quality, 4),
                "decay_multiplier": round(decay, 4),
                "anti_spam_multiplier": round(penalty, 4),
                "diagnostic_event_score": round(score, 4),
                "non_transferable": True,
            }
        )
    return rows


def write_csv(rows: Iterable[dict[str, Any]], path: str | Path) -> None:
    materialized = list(rows)
    if not materialized:
        raise ValueError("Cannot serialize an empty CSV")
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(materialized[0]))
        writer.writeheader()
        writer.writerows(materialized)


def write_json(value: Any, path: str | Path) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(value, indent=2, sort_keys=True) + "\n")


def stable_input_label(
    input_file: str | Path, authorised_root: str | Path | None = None
) -> str:
    """Serialize a root-relative input path with stable POSIX separators.

    Absolute, drive-relative, UNC and traversal paths are rejected consistently
    on every host. Existing symlinks are resolved before the containment check.
    """

    label, _ = _validated_input_path(input_file, authorised_root)
    return label


def summary(
    rows: Iterable[dict[str, Any]], input_file: str | Path, half_life_days: float
) -> dict[str, Any]:
    materialized = list(rows)
    by_type: defaultdict[str, float] = defaultdict(float)
    for row in materialized:
        by_type[row["contribution_type"]] += float(row["diagnostic_event_score"])
    scores = [float(row["diagnostic_event_score"]) for row in materialized]
    return {
        "prototype_version": __version__,
        "prototype_scope": (
            "synthetic diagnostic contribution scoring; not a researcher-ranking metric"
        ),
        "disclaimer": DISCLAIMER,
        "input_file": stable_input_label(input_file),
        "half_life_days": half_life_days,
        "num_events": len(materialized),
        "diagnostic_score_sum": round(sum(scores), 4),
        "diagnostic_score_mean": round(statistics.mean(scores), 4),
        "diagnostic_score_min": round(min(scores), 4),
        "diagnostic_score_max": round(max(scores), 4),
        "by_contribution_type": {
            key: round(value, 4) for key, value in sorted(by_type.items())
        },
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/example_contributions.json")
    parser.add_argument("--output-dir", default="outputs")
    parser.add_argument("--half-life-days", type=float, default=365.0)
    parser.add_argument("--dry-run", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    arguments = build_parser().parse_args(argv)
    events = load_events(arguments.input)
    rows = score_events(events, arguments.half_life_days)
    run_summary = summary(rows, arguments.input, arguments.half_life_days)

    if not arguments.dry_run:
        output_dir = Path(arguments.output_dir)
        write_csv(rows, output_dir / "diagnostic_event_scores.csv")
        write_json(run_summary, output_dir / "summary.json")
        sensitivity = [
            {
                "half_life_days": value,
                "diagnostic_score_sum": round(
                    sum(
                        float(row["diagnostic_event_score"])
                        for row in score_events(events, value)
                    ),
                    4,
                ),
            }
            for value in (90.0, 180.0, 365.0, 730.0)
        ]
        write_csv(sensitivity, output_dir / "diagnostic_sensitivity.csv")

    print(json.dumps(run_summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
