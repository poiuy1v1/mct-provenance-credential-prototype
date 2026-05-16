#!/usr/bin/env python3
"""
MCT non-financial reward simulation prototype.

This script is a synthetic companion for Paper 1 v207. It demonstrates how
verified MOF research-contribution events could be converted into auditable,
non-financial reputation scores. It is not a cryptocurrency, investment tool,
or production blockchain implementation.

The script deliberately uses only the Python standard library so that reviewers
can run the demonstration without installing third-party packages.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import math
import statistics
import sys
import textwrap
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence

__version__ = "0.3.0-alpha"

BASE_WEIGHTS = {
    "mof_dataset_deposition": 10.0,
    "negative_synthesis_record": 8.0,
    "replication_study": 12.0,
    "peer_validation": 7.0,
    "sample_sharing": 9.0,
    "model_provenance_record": 6.0,
    "metadata_curation": 4.0,
}

VERIFICATION_MULTIPLIER = {
    "curator_verified": 1.00,
    "automated_metadata_check": 0.70,
    "unverified": 0.20,
    "challenged": 0.00,
    "retracted": -1.00,
}

QUALITY_WEIGHTS = {
    "novelty": 0.15,
    "reusability": 0.25,
    "reproducibility": 0.25,
    "validation_level": 0.20,
    "effort_proxy": 0.10,
    "negative_result_value": 0.05,
}

DISCLAIMER = (
    "Synthetic MCT reputation scores are non-financial research-recognition scores. "
    "They have no price, transferability, investment value, or claim on future returns."
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
    if not isinstance(events, list):
        raise ValueError("Input JSON must be a list of contribution-event objects")
    if not events:
        raise ValueError("Input JSON contains no contribution events")
    return events


def validate_minimal_fields(events: List[Dict[str, Any]]) -> None:
    """Lightweight validation that avoids third-party jsonschema dependency."""
    required = {
        "event_id",
        "contribution_type",
        "contributor",
        "research_object",
        "evidence",
        "verification",
        "scoring_inputs",
        "issued_credential",
    }
    for idx, event in enumerate(events):
        missing = sorted(required.difference(event))
        if missing:
            raise ValueError(f"Event index {idx} is missing required fields: {missing}")
        if event["contribution_type"] not in BASE_WEIGHTS:
            raise ValueError(f"Unknown contribution_type in {event.get('event_id')}: {event['contribution_type']}")
        status = event["verification"].get("status")
        if status not in VERIFICATION_MULTIPLIER:
            raise ValueError(f"Unknown verification.status in {event.get('event_id')}: {status}")
        cred = event.get("issued_credential", {})
        if cred.get("non_transferable") is not True or cred.get("locked") is not True:
            raise ValueError(f"Credential for {event.get('event_id')} must be non_transferable=true and locked=true")


def duplicate_penalties(events: List[Dict[str, Any]]) -> Dict[str, float]:
    """Penalize repeated same contributor/material/type events in the synthetic table."""
    keys = []
    for event in events:
        key = (
            event["contributor"]["orcid"],
            event["research_object"].get("material_id", ""),
            event["contribution_type"],
        )
        keys.append(key)
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
    reference_time = max(parse_time(e["verification"]["timestamp_utc"]) for e in events)
    anti_spam = duplicate_penalties(events)
    rows = []
    for event in events:
        contribution_type = event["contribution_type"]
        event_time = parse_time(event["verification"]["timestamp_utc"])
        base = BASE_WEIGHTS.get(contribution_type, 1.0)
        quality = quality_score(event["scoring_inputs"])
        verification = VERIFICATION_MULTIPLIER[event["verification"]["status"]]
        decay = half_life_decay(event_time, reference_time, half_life_days)
        penalty = anti_spam[event["event_id"]]
        score = base * quality * verification * decay * penalty
        rows.append(
            {
                "event_id": event["event_id"],
                "credential_id": event["issued_credential"]["credential_id"],
                "contributor_orcid": event["contributor"]["orcid"],
                "contributor": event["contributor"]["display_name"],
                "material_id": event["research_object"]["material_id"],
                "contribution_type": contribution_type,
                "verification_status": event["verification"]["status"],
                "base_weight": round(base, 4),
                "quality_score": round(quality, 4),
                "verification_multiplier": round(verification, 4),
                "decay_multiplier": round(decay, 4),
                "anti_spam_multiplier": round(penalty, 4),
                "mct_reputation_score": round(score, 4),
                "non_transferable": event["issued_credential"]["non_transferable"],
                "locked": event["issued_credential"]["locked"],
            }
        )
    return rows


def write_csv(rows: Iterable[Dict[str, Any]], path: Path) -> None:
    rows = list(rows)
    if not rows:
        raise ValueError("No rows to write")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def summary(rows: List[Dict[str, Any]], input_file: Path, half_life_days: float) -> Dict[str, Any]:
    by_contributor: Dict[str, float] = defaultdict(float)
    by_type: Dict[str, float] = defaultdict(float)
    for row in rows:
        by_contributor[row["contributor_orcid"]] += float(row["mct_reputation_score"])
        by_type[row["contribution_type"]] += float(row["mct_reputation_score"])
    scores = [float(r["mct_reputation_score"]) for r in rows]
    return {
        "prototype_version": __version__,
        "prototype_scope": "synthetic, non-financial, non-transferable reputation scoring",
        "disclaimer": DISCLAIMER,
        "input_file": str(input_file),
        "half_life_days": half_life_days,
        "num_events": len(rows),
        "score_sum": round(sum(scores), 4),
        "score_mean": round(statistics.mean(scores), 4) if scores else 0,
        "score_min": round(min(scores), 4) if scores else 0,
        "score_max": round(max(scores), 4) if scores else 0,
        "by_contributor_orcid": {k: round(v, 4) for k, v in sorted(by_contributor.items())},
        "by_contribution_type": {k: round(v, 4) for k, v in sorted(by_type.items())},
    }


def sensitivity(events: List[Dict[str, Any]], half_lives: Sequence[float]) -> List[Dict[str, Any]]:
    out = []
    for hl in half_lives:
        rows = score_events(events, half_life_days=hl)
        out.append({"half_life_days": hl, "total_score": round(sum(float(r["mct_reputation_score"]) for r in rows), 4)})
    return out


def parse_half_lives(value: str) -> List[float]:
    try:
        values = [float(v.strip()) for v in value.split(",") if v.strip()]
    except ValueError as exc:
        raise argparse.ArgumentTypeError("Use a comma-separated list of numbers, e.g. 90,180,365,730") from exc
    if not values or any(v <= 0 for v in values):
        raise argparse.ArgumentTypeError("All half-life values must be positive")
    return values


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run a synthetic MCT non-financial reward simulation.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent(
            """
            Examples:
              python3 mct_reward_simulation.py
              python3 mct_reward_simulation.py --input data/example_contributions.json --output-dir outputs
              python3 mct_reward_simulation.py --half-life-days 180 --sensitivity-half-lives 90,180,365,730
              python3 mct_reward_simulation.py --dry-run

            Interpretation:
              Scores are non-financial research-recognition values for synthetic
              contribution events. They are not prices, market values, token balances,
              investment products, or transferable assets.
            """
        ),
    )
    parser.add_argument("--input", default="data/example_contributions.json", help="Path to contribution events JSON")
    parser.add_argument("--output-dir", default="outputs", help="Directory for generated tables")
    parser.add_argument("--half-life-days", type=float, default=365.0, help="Reputation decay half-life in days")
    parser.add_argument(
        "--sensitivity-half-lives",
        type=parse_half_lives,
        default=parse_half_lives("90,180,365,730"),
        help="Comma-separated half-life values for sensitivity analysis",
    )
    parser.add_argument("--dry-run", action="store_true", help="Validate input and print summary without writing output files")
    parser.add_argument("--version", action="version", version=f"mct_reward_simulation.py {__version__}")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    input_path = Path(args.input)
    output_dir = Path(args.output_dir)

    events = load_events(input_path)
    validate_minimal_fields(events)
    rows = score_events(events, half_life_days=args.half_life_days)
    run_summary = summary(rows, input_file=input_path, half_life_days=args.half_life_days)

    if not args.dry_run:
        output_dir.mkdir(parents=True, exist_ok=True)
        write_csv(rows, output_dir / "mct_scores.csv")
        (output_dir / "summary.json").write_text(json.dumps(run_summary, indent=2), encoding="utf-8")
        sensitivity_rows = sensitivity(events, half_lives=args.sensitivity_half_lives)
        write_csv(sensitivity_rows, output_dir / "reward_sensitivity.csv")

    print(json.dumps(run_summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
