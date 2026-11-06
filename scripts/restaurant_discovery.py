#!/usr/bin/env python3
"""Deterministic restaurant-discovery proof path.

This is a local fallback for the planned n8n workflow. It deliberately uses
only the Python standard library and a fictional read-only catalog. It is not
an LLM agent, a live restaurant search, or a booking integration.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence


REQUIRED_RECORD_FIELDS = {
    "id",
    "name",
    "city",
    "cuisine",
    "price_level_eur",
    "booking_channel",
    "booking_url",
    "atmosphere",
    "source",
    "last_verified",
}
ALLOWED_BOOKING_CHANNELS = {"online", "offline", "unknown"}
SUPPORTED_CUISINES = {
    "greek": "Greek",
    "mediterranean": "Mediterranean",
    "italian": "Italian",
    "korean": "Korean",
    "turkish": "Turkish",
    "vegan": "Vegan",
    "japanese": "Japanese",
    "sushi": "Sushi",
    "mexican": "Mexican",
    "indian": "Indian",
}


def _iso_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_catalog(path: Path) -> list[dict[str, Any]]:
    """Load and validate the read-only synthetic catalog."""
    with path.open("r", encoding="utf-8") as handle:
        records = json.load(handle)
    if not isinstance(records, list) or not records:
        raise ValueError("catalog must be a non-empty JSON array")
    validated: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for index, record in enumerate(records):
        if not isinstance(record, dict):
            raise ValueError(f"catalog record {index} must be an object")
        missing = REQUIRED_RECORD_FIELDS.difference(record)
        if missing:
            raise ValueError(f"catalog record {index} is missing: {', '.join(sorted(missing))}")
        if not isinstance(record["cuisine"], list) or not all(
            isinstance(value, str) for value in record["cuisine"]
        ):
            raise ValueError(f"catalog record {index}.cuisine must be a string array")
        if record["booking_channel"] not in ALLOWED_BOOKING_CHANNELS:
            raise ValueError(f"catalog record {index}.booking_channel is not tri-state")
        if record["id"] in seen_ids:
            raise ValueError(f"duplicate catalog id: {record['id']}")
        seen_ids.add(record["id"])
        validated.append(record)
    return validated


def _session_id(payload: Any) -> str | None:
    if isinstance(payload, Mapping) and isinstance(payload.get("session_id"), str):
        value = payload["session_id"].strip()
        return value or None
    return None


def _error_output(session_id: str | None, code: str, message: str) -> dict[str, Any]:
    return {
        "session_id": session_id,
        "status": "error",
        "error_code": code,
        "intent": None,
        "preferences": None,
        "matched_restaurants": [],
        "alternative_restaurants": [],
        "message": message,
        "data_mode": "synthetic_demo",
        "availability_checked": False,
        "search_performed": False,
    }


def normalize_input(payload: Any) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    """Validate the external payload before any catalog lookup."""
    if not isinstance(payload, dict):
        return None, _error_output(None, "invalid_payload", "Input must be a JSON object.")
    session_id = _session_id(payload)
    message = payload.get("message")
    if not isinstance(message, str):
        return None, _error_output(session_id, "invalid_message_type", "The message field must be a string.")
    if not message.strip():
        return None, _error_output(session_id, "empty_message", "Please provide a non-empty restaurant preference.")
    return {"session_id": session_id, "message": message.strip()}, None


def extract_preferences(message: str, catalog: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Extract a small documented schema with rules, not an LLM."""
    lower_message = message.casefold()
    city_values = sorted({str(record["city"]) for record in catalog}, key=len, reverse=True)
    city = next(
        (value for value in city_values if re.search(rf"\b{re.escape(value.casefold())}\b", lower_message)),
        None,
    )
    cuisine = next(
        (canonical for alias, canonical in SUPPORTED_CUISINES.items() if re.search(rf"\b{re.escape(alias)}\b", lower_message)),
        None,
    )
    budget_max_eur: int | float | None = None
    budget_patterns = (
        r"(?:under|below|up\s+to|maximum\s+of|max\.?|less\s+than)\s*(?:€|eur(?:os?)?)?\s*(\d+(?:[.,]\d+)?)",
        r"(\d+(?:[.,]\d+)?)\s*(?:€|eur(?:os?)?)",
    )
    for pattern in budget_patterns:
        match = re.search(pattern, lower_message)
        if match:
            number = float(match.group(1).replace(",", "."))
            budget_max_eur = int(number) if number.is_integer() else number
            break
    booking_requested = bool(re.search(r"\b(book|booking|reserve|reservation)\b", lower_message))
    atmosphere_requested = bool(re.search(r"\b(atmosphere|ambience|ambiance)\b", lower_message))
    return {
        "intent": "booking_request" if booking_requested else "discovery",
        "city": city,
        "cuisine": cuisine,
        "budget_max_eur": budget_max_eur,
        "party_size": None,
        "date": None,
        "time": None,
        "booking_requested": booking_requested,
        "atmosphere_requested": atmosphere_requested,
        "extraction_mode": "rule_based_demo",
    }


def _same(value_a: str, value_b: str) -> bool:
    return value_a.casefold() == value_b.casefold()


def _cuisine_matches(record: Mapping[str, Any], requested: str | None) -> bool:
    if requested is None:
        return True
    return any(_same(str(value), requested) for value in record["cuisine"])


def _record_result(record: Mapping[str, Any], reason: str) -> dict[str, Any]:
    return {
        "restaurant_id": record["id"],
        "name": record["name"],
        "reason": reason,
        "city": record["city"],
        "cuisine": record["cuisine"],
        "price_level_eur": record["price_level_eur"],
        "booking_channel": record["booking_channel"],
        "booking_url": record["booking_url"],
        "atmosphere": record["atmosphere"],
        "source": record["source"],
        "last_verified": record["last_verified"],
    }


def _human_request(preferences: Mapping[str, Any]) -> str:
    parts = []
    if preferences["cuisine"]:
        parts.append(str(preferences["cuisine"]))
    if preferences["city"]:
        parts.append(f"in {preferences['city']}")
    if preferences["budget_max_eur"] is not None:
        parts.append(f"up to €{preferences['budget_max_eur']}")
    return " ".join(parts) or "the supplied preferences"


def _build_message(
    preferences: Mapping[str, Any],
    matches: Sequence[Mapping[str, Any]],
    alternatives: Sequence[Mapping[str, Any]],
) -> str:
    if preferences["city"] is None:
        return "Which city should I search? I will not assume a location for this demo."
    request = _human_request(preferences)
    booking_note = (
        " This demo does not place reservations or check live availability."
        if preferences["booking_requested"]
        else " No live availability was checked."
    )
    atmosphere_note = (
        " Atmosphere is not documented in the synthetic catalog."
        if preferences["atmosphere_requested"]
        and any(item["atmosphere"] is None for item in [*matches, *alternatives])
        else ""
    )
    if matches:
        names = ", ".join(str(item["name"]) for item in matches)
        statuses = "; ".join(
            f"{item['name']}: booking channel {item['booking_channel']}" for item in matches
        )
        return f"Found {len(matches)} fictional demo match(es) for {request}: {names}. {statuses}.{booking_note}{atmosphere_note}"
    if alternatives:
        names = ", ".join(str(item["name"]) for item in alternatives)
        return (
            f"No exact fictional demo match was found for {request}. "
            f"Clearly labeled alternatives that relax a requested constraint: {names}."
            f" Booking channel and price details are shown per record; these are not exact matches.{booking_note}{atmosphere_note}"
        )
    return f"No fictional demo restaurant matched {request}; no alternative was returned.{booking_note}"


def run_discovery(
    payload: Any,
    *,
    catalog_path: Path | None = None,
    catalog: Sequence[Mapping[str, Any]] | None = None,
    execution_id: str | None = None,
    executed_at: str | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Run trigger -> transform -> read-only lookup -> observable output."""
    normalized, validation_error = normalize_input(payload)
    execution_id = execution_id or f"local-{uuid.uuid4()}"
    executed_at = executed_at or _iso_now()
    node_trace: list[dict[str, Any]] = [
        {"name": "Input", "stage": "trigger", "status": "success", "items_out": 1},
        {"name": "Normalize & Validate Input", "stage": "transform", "status": "success"},
    ]
    if validation_error:
        node_trace[-1]["status"] = "error"
        node_trace.append({"name": "Observable Output", "stage": "output", "status": "success", "items_out": 1})
        trace = {
            "execution_id": execution_id,
            "executed_at": executed_at,
            "environment": "local-python-runner",
            "n8n_executed": False,
            "success": False,
            "nodes": node_trace,
            "preference_mapping": None,
            "search": {"performed": False, "matched_ids": [], "alternative_ids": []},
            "output_status": validation_error["status"],
        }
        return validation_error, trace

    assert normalized is not None
    try:
        records = list(catalog) if catalog is not None else load_catalog(catalog_path or Path("fixtures/restaurants.demo.json"))
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        output = _error_output(normalized["session_id"], "catalog_unavailable", "The restaurant catalog could not be read; no recommendation was returned.")
        node_trace.extend([
            {"name": "Extract Search Preferences", "stage": "transform", "status": "success"},
            {"name": "Read Synthetic Catalog", "stage": "action", "status": "error", "error": str(exc)},
            {"name": "Observable Output", "stage": "output", "status": "success", "items_out": 1},
        ])
        trace = {
            "execution_id": execution_id,
            "executed_at": executed_at,
            "environment": "local-python-runner",
            "n8n_executed": False,
            "success": False,
            "nodes": node_trace,
            "preference_mapping": None,
            "search": {"performed": False, "matched_ids": [], "alternative_ids": []},
            "output_status": output["status"],
        }
        return output, trace

    preferences = extract_preferences(normalized["message"], records)
    node_trace.append({"name": "Extract Search Preferences", "stage": "transform", "status": "success"})
    if preferences["city"] is None:
        output = {
            "session_id": normalized["session_id"],
            "status": "needs_clarification",
            "intent": preferences["intent"],
            "preferences": preferences,
            "matched_restaurants": [],
            "alternative_restaurants": [],
            "message": _build_message(preferences, [], []),
            "data_mode": "synthetic_demo",
            "availability_checked": False,
            "search_performed": False,
        }
        node_trace.extend([
            {"name": "Enough Information for Discovery?", "stage": "decision", "status": "success", "result": "no"},
            {"name": "Observable Output", "stage": "output", "status": "success", "items_out": 1},
        ])
        trace = {
            "execution_id": execution_id,
            "executed_at": executed_at,
            "environment": "local-python-runner",
            "n8n_executed": False,
            "success": True,
            "nodes": node_trace,
            "preference_mapping": preferences,
            "search": {"performed": False, "matched_ids": [], "alternative_ids": []},
            "output_status": output["status"],
        }
        return output, trace

    city_records = [record for record in records if _same(str(record["city"]), str(preferences["city"]))]
    exact_records = [record for record in city_records if _cuisine_matches(record, preferences["cuisine"])]
    if preferences["budget_max_eur"] is not None:
        exact_records = [
            record for record in exact_records if float(record["price_level_eur"]) <= float(preferences["budget_max_eur"])
        ]
    exact_records.sort(key=lambda record: (float(record["price_level_eur"]), str(record["id"])))
    matches = [
        _record_result(
            record,
            f"{record['city']} record with requested cuisine and within the requested price limit"
            if preferences["budget_max_eur"] is not None
            else f"{record['city']} record matching the requested cuisine",
        )
        for record in exact_records[:5]
    ]
    alternatives: list[dict[str, Any]] = []
    if not matches:
        candidates = [record for record in city_records if not _cuisine_matches(record, preferences["cuisine"])]
        candidates.sort(key=lambda record: (float(record["price_level_eur"]), str(record["id"])))
        alternatives = [
            _record_result(record, "alternative with a relaxed cuisine or budget constraint; not an exact match")
            for record in candidates[:2]
        ]
    output = {
        "session_id": normalized["session_id"],
        "status": "ok" if matches else "no_exact_match",
        "intent": preferences["intent"],
        "preferences": preferences,
        "matched_restaurants": matches,
        "alternative_restaurants": alternatives,
        "message": _build_message(preferences, matches, alternatives),
        "data_mode": "synthetic_demo",
        "availability_checked": False,
        "search_performed": True,
    }
    node_trace.extend([
        {"name": "Enough Information for Discovery?", "stage": "decision", "status": "success", "result": "yes"},
        {"name": "Read Synthetic Catalog", "stage": "action", "status": "success", "items_out": len(records)},
        {"name": "Filter & Rank Matches", "stage": "transform", "status": "success", "items_out": len(matches) + len(alternatives)},
        {"name": "Format Grounded Response", "stage": "transform", "status": "success"},
        {"name": "Observable Output", "stage": "output", "status": "success", "items_out": 1},
    ])
    trace = {
        "execution_id": execution_id,
        "executed_at": executed_at,
        "environment": "local-python-runner",
        "n8n_executed": False,
        "success": True,
        "nodes": node_trace,
        "preference_mapping": preferences,
        "search": {
            "performed": True,
            "catalog_records_read": len(records),
            "matched_ids": [item["restaurant_id"] for item in matches],
            "alternative_ids": [item["restaurant_id"] for item in alternatives],
        },
        "output_status": output["status"],
    }
    return output, trace


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path("fixtures/input.demo.json"))
    parser.add_argument("--catalog", type=Path, default=Path("fixtures/restaurants.demo.json"))
    parser.add_argument("--trace", action="store_true", help="include the sanitized execution trace")
    args = parser.parse_args(argv)
    try:
        with args.input.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
        output, trace = run_discovery(payload, catalog_path=args.catalog)
    except (OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "error", "error_code": "input_unavailable", "message": str(exc)}), file=sys.stderr)
        return 2
    result = {"output": output, "trace": trace} if args.trace else output
    print(json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True))
    return 0 if output["status"] != "error" else 1


if __name__ == "__main__":
    raise SystemExit(main())
