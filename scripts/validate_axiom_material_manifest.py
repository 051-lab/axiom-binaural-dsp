#!/usr/bin/env python3
"""Validate Axiom local-material manifests and coverage metadata."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


MATERIAL_CLASSES = (
    "low_level_dynamic",
    "sibilant_vocal",
    "cymbals_air",
    "dense_pop_edm",
    "hiphop_trap_sub",
    "rock_metal_guitars",
    "acoustic_bass",
    "piano",
    "orchestral_crescendo",
    "mono_narrow",
    "flawed_source",
    "speech",
    "bass_light",
    "already_wide_mix",
)
FAILURE_MODES = (
    "low_end_headroom",
    "sub_extension",
    "kick_bass_separation",
    "sibilance",
    "air_harshness",
    "center_image",
    "stereo_width",
    "mono_compatibility",
    "transient_punch",
    "fatigue",
    "distortion_artifacts",
    "speech_naturalness",
    "thin_source",
    "dense_mix_limiter_pressure",
)


def slug(label: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "_", label.strip()).strip("._-")


def is_non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def is_number(value: Any) -> bool:
    return isinstance(value, int | float) and not isinstance(value, bool)


def load_manifest(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_manifest(
    manifest: Any,
    manifest_path: Path | None = None,
    strict_metadata: bool = False,
    require_paths: bool = True,
) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    coverage = {name: 0 for name in MATERIAL_CLASSES}
    failure_mode_coverage = {name: 0 for name in FAILURE_MODES}

    if not isinstance(manifest, dict):
        return {"status": "fail", "errors": ["manifest must be a JSON object"], "warnings": [], "coverage": coverage}
    tracks = manifest.get("tracks")
    if not isinstance(tracks, list) or not tracks:
        return {"status": "fail", "errors": ["manifest.tracks must be a non-empty list"], "warnings": [], "coverage": coverage}

    seen_names: set[str] = set()
    for index, item in enumerate(tracks):
        prefix = f"tracks[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{prefix} must be an object")
            continue

        label = item.get("label")
        if not is_non_empty_string(label):
            errors.append(f"{prefix}.label must be a non-empty string")
            name = ""
        else:
            name = slug(label)
            if not name:
                errors.append(f"{prefix}.label must contain filesystem-safe characters")
            elif name in seen_names:
                errors.append(f"{prefix}.label duplicates another item after sanitization")
            seen_names.add(name)

        path_value = item.get("path")
        if not is_non_empty_string(path_value):
            errors.append(f"{prefix}.path must be a non-empty string")
        elif require_paths:
            source_path = Path(path_value).expanduser()
            if manifest_path is not None and not source_path.is_absolute():
                source_path = (manifest_path.parent / source_path).resolve()
            if not source_path.is_file():
                errors.append(f"{prefix}.path does not exist: {source_path}")

        for key in ("start_seconds", "duration_seconds"):
            if not is_number(item.get(key)):
                errors.append(f"{prefix}.{key} must be numeric")
        if is_number(item.get("start_seconds")) and item["start_seconds"] < 0.0:
            errors.append(f"{prefix}.start_seconds must be non-negative")
        if is_number(item.get("duration_seconds")):
            duration = item["duration_seconds"]
            if duration <= 0.0 or duration > 60.0:
                errors.append(f"{prefix}.duration_seconds must be in (0, 60] seconds")

        material_class = item.get("material_class")
        if material_class in MATERIAL_CLASSES:
            coverage[material_class] += 1
        elif strict_metadata:
            errors.append(f"{prefix}.material_class must be one of: {', '.join(MATERIAL_CLASSES)}")
        else:
            warnings.append(f"{prefix}.material_class is missing or outside the Axiom taxonomy")

        modes = item.get("failure_modes")
        if isinstance(modes, list) and modes:
            for mode in modes:
                if mode in FAILURE_MODES:
                    failure_mode_coverage[mode] += 1
                elif strict_metadata:
                    errors.append(f"{prefix}.failure_modes contains unknown mode: {mode}")
                else:
                    warnings.append(f"{prefix}.failure_modes contains unknown mode: {mode}")
        elif strict_metadata:
            errors.append(f"{prefix}.failure_modes must be a non-empty list")
        else:
            warnings.append(f"{prefix}.failure_modes is missing")

        for key in ("license_scope", "provenance", "role"):
            if not is_non_empty_string(item.get(key)):
                if strict_metadata:
                    errors.append(f"{prefix}.{key} must be a non-empty string")
                else:
                    warnings.append(f"{prefix}.{key} is missing")

    missing_classes = [name for name, count in coverage.items() if count == 0]
    if missing_classes:
        warnings.append(f"missing material classes: {', '.join(missing_classes)}")
    missing_failure_modes = [name for name, count in failure_mode_coverage.items() if count == 0]
    if missing_failure_modes:
        warnings.append(f"missing failure modes: {', '.join(missing_failure_modes)}")

    status = "fail" if errors else ("pass_with_warnings" if warnings else "pass")
    return {
        "status": status,
        "errors": errors,
        "warnings": warnings,
        "track_count": len(tracks),
        "coverage": coverage,
        "failure_mode_coverage": failure_mode_coverage,
    }


def markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Axiom Material Manifest Validation",
        "",
        f"Status: **{report['status'].upper()}**",
        "",
        f"Track count: `{report.get('track_count', 0)}`",
        "",
        "## Material Class Coverage",
        "",
        "| Class | Count |",
        "| --- | ---: |",
    ]
    for name in MATERIAL_CLASSES:
        lines.append(f"| {name} | {report['coverage'].get(name, 0)} |")
    lines.extend(["", "## Failure Mode Coverage", "", "| Failure mode | Count |", "| --- | ---: |"])
    for name in FAILURE_MODES:
        lines.append(f"| {name} | {report['failure_mode_coverage'].get(name, 0)} |")
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
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--strict-metadata", action="store_true")
    parser.add_argument("--allow-missing-paths", action="store_true")
    parser.add_argument("--json", type=Path)
    parser.add_argument("--markdown", type=Path)
    args = parser.parse_args()

    try:
        manifest = load_manifest(args.manifest)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"error: cannot read material manifest: {exc}")
        return 1
    report = validate_manifest(
        manifest,
        manifest_path=args.manifest.resolve(),
        strict_metadata=args.strict_metadata,
        require_paths=not args.allow_missing_paths,
    )
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
