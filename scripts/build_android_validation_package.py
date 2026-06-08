#!/usr/bin/env python3
"""Build a local RootlessJamesDSP validation package for Axiom scripts."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import shutil
from pathlib import Path
from typing import Any


DEFAULT_HOST_SETTINGS = {
    "jdsp_limiter_threshold_db": -1.0,
    "jdsp_limiter_release_ms": 60.0,
    "jdsp_postgain_db": 0.0,
    "crossfeed_enabled_for_qualification": False,
}


class PackageError(RuntimeError):
    pass


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def script_entry(path: Path, role: str, destination: Path) -> dict[str, Any]:
    if not path.is_file():
        raise PackageError(f"{role} script not found: {path}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, destination)
    return {
        "role": role,
        "source_path": str(path),
        "package_path": str(destination),
        "filename": destination.name,
        "sha256": sha256(destination),
    }


def listening_template(package_name: str, accepted_version: str, comparison_version: str) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "recorded_at": dt.datetime.now(tz=dt.timezone.utc).isoformat(),
        "listener": "",
        "axiom_version": accepted_version,
        "comparison_version": comparison_version,
        "decision": "no_decision",
        "acceptance_rationale": "",
        "rejection_rationale": "",
        "device": "Android / RootlessJamesDSP",
        "route": "",
        "host_settings": {
            "jdsp_limiter_threshold_db": DEFAULT_HOST_SETTINGS["jdsp_limiter_threshold_db"],
            "jdsp_limiter_release_ms": DEFAULT_HOST_SETTINGS["jdsp_limiter_release_ms"],
            "jdsp_postgain_db": DEFAULT_HOST_SETTINGS["jdsp_postgain_db"],
            "crossfeed_enabled": DEFAULT_HOST_SETTINGS["crossfeed_enabled_for_qualification"],
        },
        "slider_settings": {
            "sub_harmonics_gain_db": 4.0,
            "global_side_width_percent": 135.0,
            "fletcher_munson_sensitivity_percent": 50.0,
            "low_mid_width_percent": 126.0,
            "high_width_percent": 110.0,
            "stft_resonance_suppression_percent": 50.0,
        },
        "material": [],
        "observations": {
            "bass": "",
            "punch": "",
            "center_image": "",
            "lateral_spread": "",
            "localization_blur": "",
            "depth_impression": "",
            "bass_image_coupling": "",
            "width": "",
            "air": "",
            "harshness": "",
            "loudness": "",
            "fatigue": "",
            "route_context": "",
            "artifacts": "",
            "overall": f"{package_name} Android validation notes",
        },
    }


def checklist(manifest: dict[str, Any]) -> str:
    rows = [
        "# Axiom Android Validation Checklist",
        "",
        f"Package: `{manifest['package_name']}`",
        "",
        "## Scripts",
        "",
        "| Role | Filename | SHA-256 |",
        "| --- | --- | --- |",
    ]
    for item in manifest["scripts"]:
        rows.append(f"| {item['role']} | `{item['filename']}` | `{item['sha256']}` |")
    rows.extend(
        [
            "",
            "## RootlessJamesDSP Setup",
            "",
            "- Copy the selected `.eel` file from `scripts/` into the RootlessJamesDSP Liveprog location.",
            "- Confirm the active Liveprog filename and SHA-256 against `manifest.json` before listening.",
            "- Qualification baseline: JDSP limiter threshold `-1.00 dB`, release `60 ms`, postgain `0 dB`.",
            "- Keep host crossfeed disabled during qualification. Enable it only for separate compatibility listening.",
            "- Reopen RootlessJamesDSP after loading if the app does not clearly reload the script.",
            "- After a reboot, repeat the filename/hash check before trusting a listening result.",
            "",
            "## Listening Pass",
            "",
            "- Use the same material order for accepted and candidate scripts.",
            "- Avoid changing Axiom sliders mid-pass unless the test explicitly says so.",
            "- Record bass, punch, center image, lateral spread, localization blur, depth, bass-image coupling, route context, fatigue, and artifacts.",
            "- Validate the completed local record with `scripts/validate_axiom_listening_record.py`.",
            "",
            "Full listening records may contain private material names and should stay local unless sanitized.",
            "",
        ]
    )
    return "\n".join(rows)


def build_package(
    accepted: Path,
    output_dir: Path,
    candidate: Path | None = None,
    package_name: str = "axiom-android-validation",
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    scripts_dir = output_dir / "scripts"
    accepted = accepted.resolve()
    scripts = [script_entry(accepted, "accepted", scripts_dir / accepted.name)]
    comparison_version = accepted.stem
    if candidate is not None:
        candidate = candidate.resolve()
        scripts.append(script_entry(candidate, "candidate", scripts_dir / candidate.name))
        comparison_version = accepted.stem
        accepted_version = candidate.stem
    else:
        accepted_version = accepted.stem
    manifest = {
        "package_name": package_name,
        "generated_at": dt.datetime.now(tz=dt.timezone.utc).isoformat(),
        "scope": "RootlessJamesDSP manual validation package",
        "host_settings": DEFAULT_HOST_SETTINGS,
        "scripts": scripts,
        "artifacts": {
            "checklist": "android-validation-checklist.md",
            "listening_record_template": "listening-record-template.json",
        },
    }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    (output_dir / "android-validation-checklist.md").write_text(checklist(manifest), encoding="utf-8")
    (output_dir / "listening-record-template.json").write_text(
        json.dumps(listening_template(package_name, accepted_version, comparison_version), indent=2) + "\n",
        encoding="utf-8",
    )
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("accepted_eel", type=Path)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--candidate-eel", type=Path)
    parser.add_argument("--package-name", default="axiom-android-validation")
    args = parser.parse_args()
    try:
        manifest = build_package(
            args.accepted_eel,
            args.output_dir.resolve(),
            candidate=args.candidate_eel,
            package_name=args.package_name,
        )
    except PackageError as exc:
        print(f"error: {exc}")
        return 1
    print(args.output_dir.resolve() / "manifest.json")
    for item in manifest["scripts"]:
        print(f"{item['role']}: {item['filename']} {item['sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
