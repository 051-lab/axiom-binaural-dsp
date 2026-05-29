#!/usr/bin/env python3
"""Validate structured Axiom listening records."""

from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
from typing import Any


VALID_DECISIONS = {"accept", "reject", "needs_retest", "no_decision"}
VALID_SOURCE_TYPES = {"private_owned", "cc0", "generated", "streamed_reference", "unknown"}
REQUIRED_HOST_SETTINGS = (
    "jdsp_limiter_threshold_db",
    "jdsp_limiter_release_ms",
    "jdsp_postgain_db",
    "crossfeed_enabled",
)
REQUIRED_SLIDER_SETTINGS = (
    "sub_harmonics_gain_db",
    "global_side_width_percent",
    "fletcher_munson_sensitivity_percent",
    "low_mid_width_percent",
    "high_width_percent",
    "stft_resonance_suppression_percent",
)
REQUIRED_OBSERVATIONS = (
    "bass",
    "punch",
    "center_image",
    "width",
    "air",
    "harshness",
    "loudness",
    "fatigue",
    "artifacts",
    "overall",
)


def is_number(value: Any) -> bool:
    return isinstance(value, int | float) and not isinstance(value, bool)


def is_non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def valid_timestamp(value: str) -> bool:
    try:
        dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return True


def escaped(value: Any) -> str:
    return str(value).replace("|", "\\|")


def validate_record(record: Any) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    if not isinstance(record, dict):
        return {"status": "fail", "errors": ["record must be a JSON object"], "warnings": []}

    if record.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    for key in ("recorded_at", "listener", "axiom_version", "comparison_version", "device", "route"):
        if not is_non_empty_string(record.get(key)):
            errors.append(f"{key} must be a non-empty string")
    if is_non_empty_string(record.get("recorded_at")) and not valid_timestamp(record["recorded_at"]):
        errors.append("recorded_at must be an ISO-8601 timestamp")

    decision = record.get("decision")
    if decision not in VALID_DECISIONS:
        errors.append(f"decision must be one of: {', '.join(sorted(VALID_DECISIONS))}")

    host = record.get("host_settings")
    if not isinstance(host, dict):
        errors.append("host_settings must be an object")
    else:
        for key in REQUIRED_HOST_SETTINGS:
            if key == "crossfeed_enabled":
                if not isinstance(host.get(key), bool):
                    errors.append("host_settings.crossfeed_enabled must be boolean")
            elif not is_number(host.get(key)):
                errors.append(f"host_settings.{key} must be numeric")

    sliders = record.get("slider_settings")
    if not isinstance(sliders, dict):
        errors.append("slider_settings must be an object")
    else:
        for key in REQUIRED_SLIDER_SETTINGS:
            if not is_number(sliders.get(key)):
                errors.append(f"slider_settings.{key} must be numeric")

    observations = record.get("observations")
    if not isinstance(observations, dict):
        errors.append("observations must be an object")
    else:
        for key in REQUIRED_OBSERVATIONS:
            if not is_non_empty_string(observations.get(key)):
                errors.append(f"observations.{key} must be a non-empty string")

    material = record.get("material")
    if not isinstance(material, list) or not material:
        errors.append("material must be a non-empty list")
    else:
        for index, item in enumerate(material):
            prefix = f"material[{index}]"
            if not isinstance(item, dict):
                errors.append(f"{prefix} must be an object")
                continue
            for key in ("label", "license_scope", "comparison_target", "timestamp_or_excerpt", "notes"):
                if not is_non_empty_string(item.get(key)):
                    errors.append(f"{prefix}.{key} must be a non-empty string")
            if item.get("source_type") not in VALID_SOURCE_TYPES:
                errors.append(f"{prefix}.source_type must be one of: {', '.join(sorted(VALID_SOURCE_TYPES))}")
            if item.get("source_type") in {"private_owned", "streamed_reference"}:
                warnings.append(f"{prefix} uses private or streamed material; keep the full record out of public git")

    if decision == "accept" and not is_non_empty_string(record.get("acceptance_rationale")):
        errors.append("acceptance_rationale must be set when decision is accept")
    if decision == "reject" and not is_non_empty_string(record.get("rejection_rationale")):
        errors.append("rejection_rationale must be set when decision is reject")

    return {"status": "fail" if errors else "pass", "errors": errors, "warnings": warnings}


def markdown(record: dict[str, Any], validation: dict[str, Any]) -> str:
    lines = [
        "# Axiom Listening Record",
        "",
        f"Validation: **{validation['status'].upper()}**",
        "",
        "| Field | Value |",
        "| --- | --- |",
        f"| Version | `{escaped(record.get('axiom_version', ''))}` |",
        f"| Compared against | `{escaped(record.get('comparison_version', ''))}` |",
        f"| Decision | `{escaped(record.get('decision', ''))}` |",
        f"| Device | {escaped(record.get('device', ''))} |",
        f"| Route | {escaped(record.get('route', ''))} |",
        "",
        "## Material",
        "",
        "| Label | Source type | License scope | Comparison target | Excerpt | Notes |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for item in record.get("material", []):
        lines.append(
            f"| {escaped(item.get('label', ''))} | {escaped(item.get('source_type', ''))} | "
            f"{escaped(item.get('license_scope', ''))} | {escaped(item.get('comparison_target', ''))} | "
            f"{escaped(item.get('timestamp_or_excerpt', ''))} | {escaped(item.get('notes', ''))} |"
        )
    lines.extend(["", "## Observations", "", "| Area | Notes |", "| --- | --- |"])
    observations = record.get("observations", {})
    for key in REQUIRED_OBSERVATIONS:
        lines.append(f"| {key} | {escaped(observations.get(key, ''))} |")
    if validation["errors"]:
        lines.extend(["", "## Validation Errors", ""])
        lines.extend(f"- {error}" for error in validation["errors"])
    if validation["warnings"]:
        lines.extend(["", "## Validation Warnings", ""])
        lines.extend(f"- {warning}" for warning in validation["warnings"])
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("record", type=Path)
    parser.add_argument("--json", type=Path)
    parser.add_argument("--markdown", type=Path)
    args = parser.parse_args()

    try:
        record = json.loads(args.record.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"error: cannot read listening record: {exc}")
        return 1

    validation = validate_record(record)
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(validation, indent=2) + "\n", encoding="utf-8")
    if args.markdown:
        args.markdown.parent.mkdir(parents=True, exist_ok=True)
        args.markdown.write_text(markdown(record, validation), encoding="utf-8")
    if not args.json and not args.markdown:
        print(json.dumps(validation, indent=2))
    else:
        if args.json:
            print(args.json)
        if args.markdown:
            print(args.markdown)
    return 0 if validation["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
