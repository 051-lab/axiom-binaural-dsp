#!/usr/bin/env python3
"""Qualify a versioned restrained low-mid width candidate through real JDSP."""

from __future__ import annotations

import argparse
import json
import pathlib
import sys
from typing import Any

import analyze_audio_perceptual_metrics as perceptual
import analyze_jdsp_transfer as transfer
from run_jdsp_local_material import MaterialError, convert_excerpt, read_manifest
from run_jdsp_width_material_screen import band_metrics, delta, display
from run_jdsp_lowmid_width_screen import LOW_MID_BANDS_HZ
from run_jdsp_wsl_qualification import (
    DEFAULT_PULSE_SERVER,
    DEFAULT_ROUTE_HELPER,
    QualificationError,
    run,
    stop_managed_route,
    validate_route,
)


BASELINE_SLIDER = 140.0
CANDIDATE_SLIDER = 126.0
EXPECTED_MIN_DELTA_DB = -1.50
EXPECTED_MAX_DELTA_DB = -0.25


def validate_restrained_candidate(baseline: pathlib.Path, candidate: pathlib.Path) -> None:
    source = baseline.read_text(encoding="ascii")
    altered = candidate.read_text(encoding="ascii")
    for signature in ("slider5:140<", "slider5 = 140;"):
        if source.count(signature) != 1:
            raise QualificationError(f"accepted baseline is missing one expected signature: {signature}")
    expected = source.replace("slider5:140<", "slider5:126<", 1).replace("slider5 = 140;", "slider5 = 126;", 1)
    expected_lines = expected.splitlines()
    candidate_lines = altered.splitlines()
    if not candidate_lines or not candidate_lines[0].startswith("desc: Axiom Binaural DSP "):
        raise QualificationError("candidate must retain an Axiom desc header")
    if len(expected_lines) != len(candidate_lines):
        raise QualificationError("candidate contains changes outside the scoped description and slider5 defaults")
    expected_lines[0] = candidate_lines[0]
    if expected_lines != candidate_lines:
        raise QualificationError("candidate contains changes outside the scoped description and slider5 defaults")


def analyze_item(
    item: dict[str, Any],
    excerpt: pathlib.Path,
    baseline_capture: pathlib.Path,
    candidate_capture: pathlib.Path,
) -> dict[str, Any]:
    source = transfer.read_stereo_wav(excerpt)
    baseline = transfer.read_stereo_wav(baseline_capture)
    candidate = transfer.read_stereo_wav(candidate_capture)
    source_bands = band_metrics(source, LOW_MID_BANDS_HZ)
    baseline_bands = band_metrics(baseline, LOW_MID_BANDS_HZ)
    candidate_bands = band_metrics(candidate, LOW_MID_BANDS_HZ)
    result = {
        "label": item["label"],
        "name": item["name"],
        "start_seconds": item["start_seconds"],
        "duration_seconds": item["duration_seconds"],
        "levels": {
            "accepted_140": transfer.level_metrics(baseline),
            "candidate_126": transfer.level_metrics(candidate),
        },
        "perceptual_metrics": perceptual.analyze_pair(
            baseline_capture,
            candidate_capture,
            reference_label=f"{item['name']}-accepted-140",
            candidate_label=f"{item['name']}-candidate-126",
        ),
        "bands": {},
    }
    for band, _low, _high in LOW_MID_BANDS_HZ:
        result["bands"][band] = {
            "source": source_bands[band],
            "accepted_140": baseline_bands[band],
            "candidate_126": candidate_bands[band],
            "candidate_minus_accepted_side_to_mid_db": delta(
                candidate_bands[band]["side_to_mid_db"],
                baseline_bands[band]["side_to_mid_db"],
            ),
        }
    return result


def evaluate_items(items: list[dict[str, Any]], ceiling_dbfs: float) -> dict[str, Any]:
    checks: list[dict[str, str]] = []
    for item in items:
        for key in ("accepted_140", "candidate_126"):
            levels = item["levels"][key]
            if levels["clipped_samples"] > 0:
                status = "fail"
                detail = f"{levels['clipped_samples']} clipped channel samples"
            elif levels["peak_dbfs"] is None:
                status = "fail"
                detail = "silent output"
            elif key == "candidate_126" and levels["peak_dbfs"] > ceiling_dbfs:
                status = "investigate"
                detail = f"peak={levels['peak_dbfs']:.3f} dBFS exceeds observation level {ceiling_dbfs:.3f} dBFS"
            else:
                status = "pass"
                detail = f"peak={levels['peak_dbfs']:.3f} dBFS, clipping=0"
            checks.append({"name": f"{item['name']}_{key}_integrity", "status": status, "detail": detail})
        for band, _low, _high in LOW_MID_BANDS_HZ:
            measured = item["bands"][band]["candidate_minus_accepted_side_to_mid_db"]
            passed = (
                measured is not None
                and EXPECTED_MIN_DELTA_DB <= measured <= EXPECTED_MAX_DELTA_DB
            )
            checks.append(
                {
                    "name": f"{item['name']}_{band}_restrained_width_delta",
                    "status": "pass" if passed else "fail",
                    "detail": (
                        f"candidate - accepted S/M={measured:+.3f} dB; required "
                        f"{EXPECTED_MIN_DELTA_DB:+.2f} to {EXPECTED_MAX_DELTA_DB:+.2f} dB"
                        if measured is not None
                        else "candidate - accepted S/M is not measurable"
                    ),
                }
            )
    status = "fail" if any(check["status"] == "fail" for check in checks) else (
        "pass_with_investigation" if any(check["status"] == "investigate" for check in checks) else "pass"
    )
    return {"status": status, "checks": checks}


def markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Axiom Low-Mid Width Candidate Qualification",
        "",
        f"Status: **{report['evaluation']['status'].upper()}**",
        "",
        f"Baseline: `{report['baseline_eel']}`",
        "",
        f"Candidate: `{report['candidate_eel']}`",
        "",
        "The candidate is scoped to the description line and the two `slider5` default sites: "
        "`140%` to `126%`. It must produce a restrained low-mid side balance without clipping.",
        "",
        "| Material | Band | Source S/M (dB) | Accepted S/M (dB) | Candidate S/M (dB) | Candidate - accepted (dB) |",
        "| --- | --- | ---: | ---: | ---: | ---: |",
    ]
    for item in report["items"]:
        label = item["label"].replace("|", "\\|")
        for band, _low, _high in LOW_MID_BANDS_HZ:
            values = item["bands"][band]
            lines.append(
                f"| {label} | {band} | {display(values['source']['side_to_mid_db'])} | "
                f"{display(values['accepted_140']['side_to_mid_db'])} | "
                f"{display(values['candidate_126']['side_to_mid_db'])} | "
                f"{display(values['candidate_minus_accepted_side_to_mid_db'])} |"
            )
    lines.extend(["", "## Checks", "", "| Check | Status | Detail |", "| --- | --- | --- |"])
    lines.extend(
        f"| {check['name']} | {check['status'].upper()} | {check['detail']} |"
        for check in report["evaluation"]["checks"]
    )
    lines.extend(
        [
            "",
            "## Perceptual Proxy Deltas",
            "",
            "| Material | Loudness delta (dB) | True-peak proxy delta (dB) | Transient contrast delta (dB) | S/M delta (dB) |",
            "| --- | ---: | ---: | ---: | ---: |",
        ]
    )
    for item in report["items"]:
        label = item["label"].replace("|", "\\|")
        metrics = item["perceptual_metrics"]["candidate_minus_reference"]
        lines.append(
            f"| {label} | "
            f"{display(metrics['loudness']['ungated_loudness_proxy_lufs_delta'])} | "
            f"{display(metrics['combined']['true_peak_proxy_db_delta'])} | "
            f"{display(metrics['combined']['transient_contrast_db_delta'])} | "
            f"{display(metrics['stereo']['side_to_mid_db_delta'])} |"
        )
    lines.extend(
        [
            "",
            "A pass establishes scoped implementation, output integrity, and the intended measured "
            "spatial reduction. It does not accept the sound; listening remains required.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("baseline_eel", type=pathlib.Path)
    parser.add_argument("candidate_eel", type=pathlib.Path)
    parser.add_argument("manifest", type=pathlib.Path)
    parser.add_argument("output_dir", type=pathlib.Path)
    parser.add_argument("--pulse-server", default=DEFAULT_PULSE_SERVER)
    parser.add_argument("--route-helper", type=pathlib.Path, default=DEFAULT_ROUTE_HELPER)
    parser.add_argument("--master-limiter-threshold-db", type=float, default=-1.0)
    parser.add_argument("--ceiling-dbfs", type=float, default=-0.50)
    parser.add_argument("--skip-route-start", action="store_true")
    parser.add_argument("--keep-route-running", action="store_true")
    args = parser.parse_args()

    baseline = args.baseline_eel.resolve()
    candidate = args.candidate_eel.resolve()
    for eel in (baseline, candidate):
        if not eel.is_file():
            parser.error(f"EEL script not found: {eel}")
    validate_restrained_candidate(baseline, candidate)
    items = read_manifest(args.manifest.resolve())
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    route_started = False
    try:
        if not args.skip_route_start:
            if not args.route_helper.is_file():
                raise QualificationError(f"route helper not found: {args.route_helper}")
            run([str(args.route_helper)], "start managed JamesDSP WSL audio route")
            route_started = True
        validate_route(args.pulse_server)
        script_dir = pathlib.Path(__file__).resolve().parent
        reports = []
        for item in items:
            excerpt = output_dir / "excerpts" / f"{item['name']}.wav"
            convert_excerpt(item, excerpt)
            baseline_capture = output_dir / "accepted_140" / f"{item['name']}.wav"
            candidate_capture = output_dir / "candidate_126" / f"{item['name']}.wav"
            for eel, output, label in (
                (baseline, baseline_capture, "accepted"),
                (candidate, candidate_capture, "candidate"),
            ):
                run(
                    [
                        sys.executable,
                        str(script_dir / "render_jdsp_host.py"),
                        str(excerpt),
                        str(eel),
                        str(output),
                        "--pulse-server",
                        args.pulse_server,
                        "--pre-roll-ms",
                        "500",
                        "--tail-ms",
                        "2000",
                        "--master-limiter-threshold-db",
                        str(args.master_limiter_threshold_db),
                    ],
                    f"{item['label']} {label} low-mid candidate host render",
                )
            reports.append(analyze_item(item, excerpt, baseline_capture, candidate_capture))
        report = {
            "scope": "versioned restrained low-mid width candidate through real JDSP",
            "baseline_eel": str(baseline),
            "candidate_eel": str(candidate),
            "manifest": str(args.manifest.resolve()),
            "configuration": {
                "accepted_slider5_percent": BASELINE_SLIDER,
                "candidate_slider5_percent": CANDIDATE_SLIDER,
                "required_delta_db": [EXPECTED_MIN_DELTA_DB, EXPECTED_MAX_DELTA_DB],
                "master_limiter_threshold_db": args.master_limiter_threshold_db,
                "ceiling_dbfs": args.ceiling_dbfs,
            },
            "bands_hz": LOW_MID_BANDS_HZ,
            "items": reports,
        }
        report["evaluation"] = evaluate_items(reports, args.ceiling_dbfs)
        (output_dir / "lowmid_candidate_qualification.json").write_text(
            json.dumps(report, indent=2) + "\n", encoding="utf-8"
        )
        (output_dir / "lowmid_candidate_qualification.md").write_text(markdown(report), encoding="utf-8")
        print(output_dir / "lowmid_candidate_qualification.json")
        print(output_dir / "lowmid_candidate_qualification.md")
        print(f"status={report['evaluation']['status']}")
        return 1 if report["evaluation"]["status"] == "fail" else 0
    finally:
        if route_started and not args.keep_route_running:
            for error in stop_managed_route(args.pulse_server):
                print(f"warning: {error}", file=sys.stderr)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (MaterialError, QualificationError, transfer.AnalysisError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1)
