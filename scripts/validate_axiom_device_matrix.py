#!/usr/bin/env python3
"""Validate Axiom device and route validation matrices."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


DEVICE_CLASSES = (
    "primary_android",
    "speaker_path",
    "wired_or_usb",
    "bluetooth",
    "wsl_jdsp_lab",
)
QUALIFICATION_CROSSFEED_POLICIES = {"off_for_qualification", "not_applicable"}
CROSSFEED_POLICIES = QUALIFICATION_CROSSFEED_POLICIES | {"manual_compatibility_only"}
REQUIRED_CHECKS = (
    "active_script_hash_verified",
    "host_settings_verified",
    "route_stability_checked",
    "reboot_persistence_checked",
)


def is_non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate_matrix(data: Any, strict_coverage: bool = False) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    coverage = {name: 0 for name in DEVICE_CLASSES}

    if not isinstance(data, dict):
        return {"status": "fail", "errors": ["device matrix must be a JSON object"], "warnings": [], "coverage": coverage}
    if data.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    devices = data.get("devices")
    if not isinstance(devices, list) or not devices:
        errors.append("devices must be a non-empty list")
        return {"status": "fail", "errors": errors, "warnings": warnings, "coverage": coverage}

    labels: set[str] = set()
    for index, device in enumerate(devices):
        prefix = f"devices[{index}]"
        if not isinstance(device, dict):
            errors.append(f"{prefix} must be an object")
            continue

        label = device.get("label")
        if not is_non_empty_string(label):
            errors.append(f"{prefix}.label must be a non-empty string")
        elif label in labels:
            errors.append(f"{prefix}.label duplicates another device")
        else:
            labels.add(label)

        device_class = device.get("device_class")
        if device_class not in DEVICE_CLASSES:
            errors.append(f"{prefix}.device_class must be one of: {', '.join(DEVICE_CLASSES)}")
        elif device.get("available") is True:
            coverage[device_class] += 1

        for key in ("platform", "route", "output_device", "validation_role"):
            if not is_non_empty_string(device.get(key)):
                errors.append(f"{prefix}.{key} must be a non-empty string")

        for key in ("available", "qualification_allowed"):
            if not isinstance(device.get(key), bool):
                errors.append(f"{prefix}.{key} must be boolean")

        crossfeed_policy = device.get("crossfeed_policy")
        if crossfeed_policy not in CROSSFEED_POLICIES:
            errors.append(f"{prefix}.crossfeed_policy must be one of: {', '.join(sorted(CROSSFEED_POLICIES))}")
        elif device.get("qualification_allowed") is True and crossfeed_policy not in QUALIFICATION_CROSSFEED_POLICIES:
            errors.append(f"{prefix}.crossfeed_policy must keep crossfeed off for qualification")

        checks = device.get("checks")
        if not isinstance(checks, dict):
            errors.append(f"{prefix}.checks must be an object")
        else:
            for key in REQUIRED_CHECKS:
                if not isinstance(checks.get(key), bool):
                    errors.append(f"{prefix}.checks.{key} must be boolean")
            if device_class == "primary_android" and device.get("available") is True:
                if checks.get("reboot_persistence_checked") is not True:
                    warnings.append(f"{prefix} is primary Android but reboot persistence has not been checked")
            if device.get("qualification_allowed") is True:
                incomplete = [key for key in REQUIRED_CHECKS if checks.get(key) is not True]
                if incomplete:
                    warnings.append(f"{prefix} is qualification-allowed but has incomplete checks: {', '.join(incomplete)}")

    missing = [name for name, count in coverage.items() if count == 0]
    if missing:
        message = f"missing available device classes: {', '.join(missing)}"
        if strict_coverage:
            errors.append(message)
        else:
            warnings.append(message)

    status = "fail" if errors else ("pass_with_warnings" if warnings else "pass")
    return {
        "status": status,
        "errors": errors,
        "warnings": warnings,
        "coverage": coverage,
        "device_count": len(devices),
    }


def markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Axiom Device Matrix Validation",
        "",
        f"Status: **{report['status'].upper()}**",
        "",
        f"Device count: `{report.get('device_count', 0)}`",
        "",
        "## Coverage",
        "",
        "| Device class | Available entries |",
        "| --- | ---: |",
    ]
    for name in DEVICE_CLASSES:
        lines.append(f"| {name} | {report['coverage'].get(name, 0)} |")
    if report["errors"]:
        lines.extend(["", "## Errors", ""])
        lines.extend(f"- {error}" for error in report["errors"])
    if report["warnings"]:
        lines.extend(["", "## Warnings", ""])
        lines.extend(f"- {warning}" for warning in report["warnings"])
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("matrix", type=Path)
    parser.add_argument("--strict-coverage", action="store_true")
    parser.add_argument("--json", type=Path)
    parser.add_argument("--markdown", type=Path)
    args = parser.parse_args()

    try:
        data = json.loads(args.matrix.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"error: cannot read device matrix: {exc}")
        return 1
    report = validate_matrix(data, strict_coverage=args.strict_coverage)
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    if args.markdown:
        args.markdown.parent.mkdir(parents=True, exist_ok=True)
        args.markdown.write_text(markdown(report), encoding="utf-8")
    if not args.json and not args.markdown:
        print(json.dumps(report, indent=2))
    else:
        if args.json:
            print(args.json)
        if args.markdown:
            print(args.markdown)
    return 1 if report["status"] == "fail" else 0


if __name__ == "__main__":
    raise SystemExit(main())
