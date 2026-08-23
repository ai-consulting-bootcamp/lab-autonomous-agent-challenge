#!/usr/bin/env python3
"""Deterministic intake-triage agent for the Intellectus lab prototype."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RULES = ROOT / "config" / "routing_rules.json"


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def is_missing(value: Any) -> bool:
    return value is None or (isinstance(value, str) and not value.strip())


def validate(payload: dict[str, Any], rules: dict[str, Any]) -> tuple[list[str], list[str]]:
    missing = [field for field in rules["required_fields"] if is_missing(payload.get(field))]
    errors: list[str] = []

    urgency = payload.get("urgency")
    if urgency is not None and urgency not in rules["allowed_urgency"]:
        errors.append(f"urgency must be one of: {', '.join(rules['allowed_urgency'])}")

    sensitivity = payload.get("data_sensitivity")
    if sensitivity is not None and sensitivity not in rules["allowed_data_sensitivity"]:
        errors.append(
            "data_sensitivity must be one of: "
            + ", ".join(rules["allowed_data_sensitivity"])
        )

    beneficiary_count = payload.get("beneficiary_count")
    if beneficiary_count is not None and (
        isinstance(beneficiary_count, bool)
        or not isinstance(beneficiary_count, int)
        or beneficiary_count < 1
    ):
        errors.append("beneficiary_count must be a positive integer")

    return missing, errors


def beneficiary_points(count: int, rules: dict[str, Any]) -> int:
    for band in rules["beneficiary_bands"]:
        if count >= band["minimum"]:
            return band["points"]
    raise ValueError("routing configuration has no beneficiary fallback band")


def stable_intake_id(payload: dict[str, Any]) -> str:
    event_id = str(payload.get("event_id", "")).strip().lower()
    normalised = re.sub(r"[^a-z0-9]+", "_", event_id).strip("_")
    return "intake_" + (normalised or "missing_event_id")


def triage(payload: dict[str, Any], rules: dict[str, Any]) -> dict[str, Any]:
    """Validate one intake and return the destination record."""
    missing, errors = validate(payload, rules)
    base = {
        "intake_id": stable_intake_id(payload),
        "source_event_id": payload.get("event_id"),
        "organization_name": payload.get("organization_name"),
        "processed_at": payload.get("submitted_at"),
        "rules_version": rules["version"],
        "review_required": True,
    }

    if missing or errors:
        return {
            **base,
            "status": "needs_information",
            "http_status": 422,
            "route": "intake_follow_up",
            "priority_score": None,
            "priority_band": None,
            "readiness_score": 0,
            "missing_fields": missing,
            "validation_errors": errors,
            "risk_flags": ["incomplete_or_invalid_intake"],
            "summary": "The intake was not scored because required or valid data is missing.",
        }

    urgency = payload["urgency"]
    sensitivity = payload["data_sensitivity"]
    challenge = payload["challenge_statement"].strip()
    outcome = payload["requested_outcome"].strip()

    score = (
        rules["urgency_points"][urgency]
        + beneficiary_points(payload["beneficiary_count"], rules)
        + rules["sensitivity_points"][sensitivity]
        + (10 if len(outcome) >= 15 else 3)
        + (5 if len(challenge) >= 80 else 2)
    )
    score = min(score, 100)

    readiness_checks = [
        len(challenge) >= 80,
        len(outcome) >= 15,
        payload["beneficiary_count"] > 0,
        urgency in rules["allowed_urgency"],
        sensitivity in rules["allowed_data_sensitivity"],
    ]
    readiness = sum(readiness_checks) * 20

    if score >= rules["critical_priority_threshold"]:
        band = "critical"
    elif score >= rules["high_priority_threshold"]:
        band = "high"
    else:
        band = "standard"

    senior_review = sensitivity == "special_category" or score >= rules["senior_review_threshold"]
    route = "senior_impact_consultant" if senior_review else "impact_consultant"

    risk_flags = []
    if sensitivity != "none":
        risk_flags.append(f"{sensitivity}_data_requires_authorised_handling")
    if payload["beneficiary_count"] >= 1000:
        risk_flags.append("high_beneficiary_reach")
    if urgency in {"high", "critical"}:
        risk_flags.append("time_sensitive_case")

    return {
        **base,
        "status": "ready_for_consultant_review",
        "http_status": 200,
        "route": route,
        "priority_score": score,
        "priority_band": band,
        "readiness_score": readiness,
        "missing_fields": [],
        "validation_errors": [],
        "risk_flags": risk_flags,
        "summary": (
            f"{payload['organization_name']} submitted a {urgency}-urgency challenge "
            f"affecting approximately {payload['beneficiary_count']} beneficiaries. "
            "A consultant must verify the diagnosis before client use."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run one Intellectus intake event.")
    parser.add_argument("--input", required=True, type=Path, help="Path to input JSON")
    parser.add_argument("--output", required=True, type=Path, help="Path to output JSON")
    parser.add_argument("--rules", type=Path, default=DEFAULT_RULES, help="Routing rules JSON")
    args = parser.parse_args()

    payload = load_json(args.input)
    rules = load_json(args.rules)
    result = triage(payload, rules)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2, ensure_ascii=False)
        handle.write("\n")

    print(json.dumps({
        "event_id": payload.get("event_id"),
        "status": result["status"],
        "route": result["route"],
        "output": str(args.output),
    }))
    return 0 if result["http_status"] == 200 else 2


if __name__ == "__main__":
    raise SystemExit(main())
