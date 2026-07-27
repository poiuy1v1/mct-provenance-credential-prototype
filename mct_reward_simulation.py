#!/usr/bin/env python3
"""Synthetic diagnostic contribution-scoring demonstration.

This script accompanies the Perspective "Provenance and contribution credentials for
AI-ready MOF research". It demonstrates event-level diagnostic calculations only. It
does not authenticate scientific claims, rank researchers, issue financial assets, or
require a blockchain.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import math
import statistics
import textwrap
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence

__version__ = "0.3.3-alpha"

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
    "metadata_status": {"not_checked": 0.60, "metadata_validated": 1.00, "metadata_invalid": 0.00},
    "evidence_file_status": {"not_checked": 0.90, "evidence_file_present": 1.00, "evidence_file_missing": 0.00},
    "file_integrity_status": {"not_checked": 0.90, "file_integrity_confirmed": 1.00, "file_integrity_failed": 0.00},
    "source_link_status": {"not_checked": 0.85, "source_link_recorded": 0.90, "source_link_resolved": 1.00, "source_link_failed": 0.00},
    "scientific_assessment_status": {
        "not_reviewed": 1.00,
        "simulated_review": 1.00,
        "scientifically_reviewed": 1.05,
        "scientifically_disputed": 0.00,
    },
}

DISCLAIMER = (
    "Diagnostic event scores are synthetic software-test outputs only. They are not prices, "
    "token balances, researcher rankings, hiring or grant metrics, authorship criteria, "
    "governance entitlements, or evidence that a scientific claim is true."
)


def parse_time(value: str) -> dt.datetime:
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    return dt.datetime.fromisoformat(value)


def half_life_decay(event_time: dt.datetime, reference_time: dt.datetime, half_life_days: float) -> float:
    if half_life_days <= 0:
        raise ValueError("half_life_days must be positive")
    age_days = max(0.0, (reference_time - event_time).total_seconds() / 86400.0)
    return math.exp(-math.log(2.0) * age_days / half_life_days)


def quality_score(inputs: Dict[str, Any]) -> float:
    return sum(float(inputs.get(k, 0.0)) * w for k, w in QUALITY_WEIGHTS.items())


def load_events(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")
    events = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(events, list) or not events:
        raise ValueError("Input JSON must be a non-empty list of contribution-event objects")
    return events


def validation_components(validation: Dict[str, Any]) -> Dict[str, float]:
    scientific = validation["scientific_assessment"]["status"]
    states = {
        "metadata_status": validation["metadata_status"],
        "evidence_file_status": validation["evidence_file_status"],
        "file_integrity_status": validation["file_integrity_status"],
        "source_link_status": validation["source_link_status"],
        "scientific_assessment_status": scientific,
    }
    components: Dict[str, float] = {}
    for field, state in states.items():
        try:
            components[field] = VALIDATION_MULTIPLIERS[field][state]
        except KeyError as exc:
            raise ValueError(f"Unsupported {field}: {state}") from exc
    return components


def composite_validation_multiplier(validation: Dict[str, Any]) -> float:
    product = 1.0
    for value in validation_components(validation).values():
        product *= value
    return product


def validate_minimal_fields(events: List[Dict[str, Any]]) -> None:
    required = {"event_id", "contribution_type", "contributor", "research_object", "evidence", "validation", "scoring_inputs", "issued_credential"}
    for idx, event in enumerate(events):
        missing = sorted(required.difference(event))
        if missing:
            raise ValueError(f"Event index {idx} is missing required fields: {missing}")
        if event["contribution_type"] not in BASE_WEIGHTS:
            raise ValueError(f"Unknown contribution_type in {event.get('event_id')}: {event['contribution_type']}")
        validation_components(event["validation"])
        verifier = event["validation"].get("verifier", {})
        contributor_orcid = event["contributor"]["orcid"]
        if verifier.get("type") == "person" and verifier.get("identifier") == contributor_orcid:
            raise ValueError(f"Self-verification is not allowed for {event.get('event_id')}")
        cred = event["issued_credential"]
        if cred.get("non_transferable") is not True or cred.get("locked") is not True:
            raise ValueError(f"Credential for {event.get('event_id')} must be non_transferable=true and locked=true")


def duplicate_penalties(events: List[Dict[str, Any]]) -> Dict[str, float]:
    keys = [(e["contributor"]["orcid"], e["research_object"].get("material_id", ""), e["contribution_type"]) for e in events]
    seen = Counter()
    penalties: Dict[str, float] = {}
    for event, key in zip(events, keys):
        seen[key] += 1
        penalty = max(0.20, 1.0 - 0.15 * (seen[key] - 1))
        if event["scoring_inputs"].get("anti_spam_flag"):
            penalty *= 0.60
        penalties[event["event_id"]] = penalty
    return penalties


def score_events(events: List[Dict[str, Any]], half_life_days: float = 365.0) -> List[Dict[str, Any]]:
    validate_minimal_fields(events)
    reference_time = max(parse_time(e["validation"]["timestamp_utc"]) for e in events)
    anti_spam = duplicate_penalties(events)
    rows: List[Dict[str, Any]] = []
    for event in events:
        validation = event["validation"]
        components = validation_components(validation)
        validation_multiplier = composite_validation_multiplier(validation)
        event_time = parse_time(validation["timestamp_utc"])
        base = BASE_WEIGHTS[event["contribution_type"]]
        quality = quality_score(event["scoring_inputs"])
        decay = half_life_decay(event_time, reference_time, half_life_days)
        penalty = anti_spam[event["event_id"]]
        score = base * quality * validation_multiplier * decay * penalty
        rows.append({
            "event_id": event["event_id"],
            "credential_id": event["issued_credential"]["credential_id"],
            "contributor_orcid": event["contributor"]["orcid"],
            "material_id": event["research_object"]["material_id"],
            "contribution_type": event["contribution_type"],
            "metadata_status": validation["metadata_status"],
            "evidence_file_status": validation["evidence_file_status"],
            "file_integrity_status": validation["file_integrity_status"],
            "source_link_status": validation["source_link_status"],
            "scientific_assessment_status": validation["scientific_assessment"]["status"],
            "metadata_multiplier": round(components["metadata_status"], 4),
            "evidence_file_multiplier": round(components["evidence_file_status"], 4),
            "file_integrity_multiplier": round(components["file_integrity_status"], 4),
            "source_link_multiplier": round(components["source_link_status"], 4),
            "scientific_assessment_multiplier": round(components["scientific_assessment_status"], 4),
            "composite_validation_multiplier": round(validation_multiplier, 4),
            "base_weight": round(base, 4),
            "quality_score": round(quality, 4),
            "decay_multiplier": round(decay, 4),
            "anti_spam_multiplier": round(penalty, 4),
            "diagnostic_event_score": round(score, 4),
            "non_transferable": event["issued_credential"]["non_transferable"],
        })
    return rows


def write_csv(rows: Iterable[Dict[str, Any]], path: Path) -> None:
    rows = list(rows)
    if not rows:
        raise ValueError("No rows to write")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def summary(rows: List[Dict[str, Any]], input_file: Path, half_life_days: float) -> Dict[str, Any]:
    by_type: Dict[str, float] = defaultdict(float)
    for row in rows:
        by_type[row["contribution_type"]] += float(row["diagnostic_event_score"])
    scores = [float(r["diagnostic_event_score"]) for r in rows]
    return {
        "prototype_version": __version__,
        "prototype_scope": "synthetic diagnostic contribution scoring; not a researcher-ranking metric",
        "disclaimer": DISCLAIMER,
        "input_file": str(input_file),
        "half_life_days": half_life_days,
        "num_events": len(rows),
        "diagnostic_score_sum": round(sum(scores), 4),
        "diagnostic_score_mean": round(statistics.mean(scores), 4) if scores else 0,
        "diagnostic_score_min": round(min(scores), 4) if scores else 0,
        "diagnostic_score_max": round(max(scores), 4) if scores else 0,
        "by_contribution_type": {k: round(v, 4) for k, v in sorted(by_type.items())},
    }


def sensitivity(events: List[Dict[str, Any]], half_lives: Sequence[float]) -> List[Dict[str, Any]]:
    rows = []
    for half_life in half_lives:
        scores = score_events(events, half_life_days=half_life)
        rows.append({"half_life_days": half_life, "diagnostic_score_sum": round(sum(float(r["diagnostic_event_score"]) for r in scores), 4)})
    return rows


def parse_half_lives(value: str) -> List[float]:
    try:
        values = [float(v.strip()) for v in value.split(",") if v.strip()]
    except ValueError as exc:
        raise argparse.ArgumentTypeError("Use comma-separated positive numbers, e.g. 90,180,365,730") from exc
    if not values or any(v <= 0 for v in values):
        raise argparse.ArgumentTypeError("All half-life values must be positive")
    return values


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run a synthetic diagnostic MOF contribution-event calculation.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""
        Interpretation:
          Outputs are diagnostic software-test values for synthetic events. They are not
          researcher rankings, prices, token balances, hiring or grant metrics, authorship
          criteria, or scientific-validation decisions.
        """),
    )
    parser.add_argument("--input", default="data/example_contributions.json")
    parser.add_argument("--output-dir", default="outputs")
    parser.add_argument("--half-life-days", type=float, default=365.0)
    parser.add_argument("--sensitivity-half-lives", type=parse_half_lives, default=parse_half_lives("90,180,365,730"))
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--version", action="version", version=f"mct_reward_simulation.py {__version__}")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    input_path = Path(args.input)
    output_dir = Path(args.output_dir)
    events = load_events(input_path)
    rows = score_events(events, args.half_life_days)
    run_summary = summary(rows, input_path, args.half_life_days)
    if not args.dry_run:
        output_dir.mkdir(parents=True, exist_ok=True)
        write_csv(rows, output_dir / "diagnostic_event_scores.csv")
        (output_dir / "summary.json").write_text(json.dumps(run_summary, indent=2) + "\n", encoding="utf-8")
        write_csv(sensitivity(events, args.sensitivity_half_lives), output_dir / "diagnostic_sensitivity.csv")
    print(json.dumps(run_summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
