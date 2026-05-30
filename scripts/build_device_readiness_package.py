#!/usr/bin/env python3
"""Build a local device-readiness checklist package for Axiom route validation."""

from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
from typing import Any

import build_android_validation_package as android_package
import validate_axiom_device_matrix as device_matrix


DEFAULT_MATRIX = Path.home() / ".local" / "state" / "axiom-engineering" / "device-matrix.json"


class ReadinessPackageError(RuntimeError):
    pass


def load_matrix(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ReadinessPackageError(f"cannot read device matrix {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ReadinessPackageError("device matrix must be a JSON object")
    return data


def route_actions(device: dict[str, Any]) -> list[str]:
    actions: list[str] = []
    label = str(device.get("label", "unnamed route"))
    device_class = str(device.get("device_class", "unknown"))
    available = device.get("available") is True
    checks = device.get("checks") if isinstance(device.get("checks"), dict) else {}
    missing_checks = False

    if not available:
        actions.append(
            "Decide whether this route is actually available; set `available: true` only after playback is verified."
        )
    for key, text in (
        ("active_script_hash_verified", "Confirm active script filename and SHA-256 match accepted policy."),
        ("host_settings_verified", "Confirm limiter threshold, release, postgain, and crossfeed policy."),
        ("route_stability_checked", "Play known material and confirm the route is stable without mute/dropout."),
        ("reboot_persistence_checked", "Reboot or reconnect and repeat route/script/settings confirmation."),
    ):
        if checks.get(key) is not True:
            missing_checks = True
            actions.append(text)
    if device_class == "primary_android" and (not available or missing_checks):
        actions.append("Use the Android validation package before accepting phone-side evidence.")
    if device_class == "wired_or_usb" and (not available or missing_checks):
        actions.append("Verify the OS reports the wired/USB endpoint as connected and healthy.")
    if not actions:
        actions.append(f"No setup actions remain for `{label}`.")
    return actions


def route_summaries(matrix: dict[str, Any]) -> list[dict[str, Any]]:
    summaries = []
    for item in matrix.get("devices", []):
        if not isinstance(item, dict):
            continue
        checks = item.get("checks") if isinstance(item.get("checks"), dict) else {}
        summaries.append(
            {
                "label": item.get("label", ""),
                "device_class": item.get("device_class", ""),
                "platform": item.get("platform", ""),
                "route": item.get("route", ""),
                "output_device": item.get("output_device", ""),
                "available": item.get("available"),
                "qualification_allowed": item.get("qualification_allowed"),
                "crossfeed_policy": item.get("crossfeed_policy", ""),
                "checks": {key: checks.get(key) for key in device_matrix.REQUIRED_CHECKS},
                "actions": route_actions(item),
            }
        )
    return summaries


def markdown(manifest: dict[str, Any]) -> str:
    strict = manifest["strict_validation"]
    lines = [
        "# Axiom Device Readiness Package",
        "",
        f"Status: **{strict['status'].upper()}**",
        "",
        "This package is local evidence-prep only. It does not certify a route and does not change DSP.",
        "",
        "## Accepted Script",
        "",
        f"- Path: `{manifest['accepted_script']['path']}`",
        f"- SHA-256: `{manifest['accepted_script']['sha256']}`",
        "",
        "## Strict Coverage",
        "",
        "| Device class | Available entries |",
        "| --- | ---: |",
    ]
    for name in device_matrix.DEVICE_CLASSES:
        lines.append(f"| {name} | {strict['coverage'].get(name, 0)} |")

    if strict["errors"]:
        lines.extend(["", "## Blocking Errors", ""])
        lines.extend(f"- {error}" for error in strict["errors"])
    if strict["warnings"]:
        lines.extend(["", "## Warnings", ""])
        lines.extend(f"- {warning}" for warning in strict["warnings"])

    lines.extend(["", "## Route Checklist", ""])
    for route in manifest["routes"]:
        lines.extend(
            [
                f"### {route['label'] or 'Unnamed route'}",
                "",
                f"- Class: `{route['device_class']}`",
                f"- Platform: `{route['platform']}`",
                f"- Output: `{route['output_device']}`",
                f"- Available: `{route['available']}`",
                f"- Qualification allowed: `{route['qualification_allowed']}`",
                f"- Crossfeed policy: `{route['crossfeed_policy']}`",
                "",
                "| Check | Value |",
                "| --- | --- |",
            ]
        )
        for key, value in route["checks"].items():
            lines.append(f"| {key} | `{value}` |")
        lines.extend(["", "Actions:"])
        lines.extend(f"- [ ] {action}" for action in route["actions"])
        lines.append("")

    lines.extend(
        [
            "## Validation Commands",
            "",
            "```bash",
            "scripts/validate_axiom_device_matrix.py \\",
            f"  {manifest['device_matrix_path']} \\",
            "  --strict-coverage \\",
            "  --strict-setup \\",
            "  --json /tmp/axiom-device-matrix-strict.json \\",
            "  --markdown /tmp/axiom-device-matrix-strict.md",
            "",
            "scripts/evaluate_axiom_candidate_readiness.py \\",
            "  --json /tmp/axiom-candidate-readiness.json \\",
            "  --markdown /tmp/axiom-candidate-readiness.md",
            "```",
            "",
        ]
    )
    return "\n".join(lines)


def build_package(
    accepted_eel: Path,
    matrix_path: Path,
    output_dir: Path,
    package_name: str = "axiom-device-readiness",
) -> dict[str, Any]:
    if not accepted_eel.is_file():
        raise ReadinessPackageError(f"accepted EEL script not found: {accepted_eel}")
    if accepted_eel.suffix.lower() != ".eel":
        raise ReadinessPackageError(f"accepted script must be an .eel file: {accepted_eel}")
    matrix = load_matrix(matrix_path)
    strict = device_matrix.validate_matrix(
        matrix,
        strict_coverage=True,
        strict_setup=True,
    )
    loose = device_matrix.validate_matrix(matrix)
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "package_name": package_name,
        "generated_at": dt.datetime.now(tz=dt.timezone.utc).isoformat(),
        "scope": "local device-readiness checklist package",
        "accepted_script": {
            "path": str(accepted_eel.resolve()),
            "filename": accepted_eel.name,
            "sha256": android_package.sha256(accepted_eel),
        },
        "device_matrix_path": str(matrix_path.expanduser()),
        "loose_validation": loose,
        "strict_validation": strict,
        "routes": route_summaries(matrix),
        "artifacts": {
            "manifest": "manifest.json",
            "checklist": "device-readiness-checklist.md",
        },
    }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    (output_dir / "device-readiness-checklist.md").write_text(markdown(manifest), encoding="utf-8")
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("accepted_eel", type=Path)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--device-matrix", type=Path, default=DEFAULT_MATRIX)
    parser.add_argument("--package-name", default="axiom-device-readiness")
    args = parser.parse_args()
    try:
        manifest = build_package(
            args.accepted_eel.expanduser(),
            args.device_matrix.expanduser(),
            args.output_dir.expanduser().resolve(),
            package_name=args.package_name,
        )
    except ReadinessPackageError as exc:
        print(f"error: {exc}")
        return 1
    print(args.output_dir.expanduser().resolve() / "manifest.json")
    print(f"strict_status={manifest['strict_validation']['status']}")
    return 0 if manifest["strict_validation"]["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
