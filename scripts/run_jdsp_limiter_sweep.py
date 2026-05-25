#!/usr/bin/env python3
"""Measure default-control Axiom output across JDSP terminal-limiter thresholds."""

from __future__ import annotations

import argparse
import json
import math
import pathlib
import re
import statistics
import subprocess
import sys
from typing import Any

from compare_jdsp_captures import analyze_capture, read_capture
from run_jdsp_local_material import MaterialError, convert_excerpt, read_manifest
from run_jdsp_wsl_qualification import (
    DEFAULT_PULSE_SERVER,
    DEFAULT_ROUTE_HELPER,
    QualificationError,
    run,
    stop_managed_route,
    validate_route,
)


def percentile(values: list[float], quantile: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    position = (len(ordered) - 1) * quantile
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    weight = position - lower
    return ordered[lower] * (1.0 - weight) + ordered[upper] * weight


def dbfs(value: float | None) -> float | None:
    return 20.0 * math.log10(value) if value and value > 0.0 else None


def window_metrics(capture: Any, window_ms: float = 20.0) -> dict[str, float | None]:
    frames = len(capture.left)
    window_frames = max(1, round(capture.sample_rate * window_ms / 1000.0))
    levels: list[float] = []
    for start in range(0, frames, window_frames):
        stop = min(frames, start + window_frames)
        if stop <= start:
            continue
        power = sum(
            (capture.left[index] * capture.left[index] + capture.right[index] * capture.right[index]) * 0.5
            for index in range(start, stop)
        ) / (stop - start)
        levels.append(math.sqrt(power))
    p95 = percentile(levels, 0.95)
    p99 = percentile(levels, 0.99)
    return {
        "window_ms": window_ms,
        "p95_rms_dbfs": dbfs(p95),
        "p99_rms_dbfs": dbfs(p99),
    }


def mean(values: list[float | None]) -> float | None:
    finite = [value for value in values if value is not None]
    return statistics.fmean(finite) if len(finite) == len(values) and finite else None


def aggregate_capture_metrics(captures: list[dict[str, Any]]) -> dict[str, float | None]:
    fields = ("peak_dbfs", "rms_dbfs", "crest_db", "p95_rms_dbfs", "p99_rms_dbfs")
    return {f"mean_{field}": mean([capture[field] for capture in captures]) for field in fields}


def delta(lower: float | None, reference: float | None) -> float | None:
    return lower - reference if lower is not None and reference is not None else None


def classify(
    tracks: list[dict[str, Any]],
    reference_threshold_db: float,
    accepted_threshold_db: float,
    min_effect_db: float,
) -> dict[str, Any]:
    affected: list[dict[str, Any]] = []
    failures: list[str] = []
    for track in tracks:
        thresholds = track["thresholds"]
        reference = thresholds[str(reference_threshold_db)]
        accepted = thresholds[str(accepted_threshold_db)]
        if reference["repeatability"]["status"] != "pass" or accepted["repeatability"]["status"] != "pass":
            failures.append(f"{track['label']}: repeatability failed at the reference or accepted threshold")
            continue
        changes = {
            "peak_db": delta(accepted["aggregate"]["mean_peak_dbfs"], reference["aggregate"]["mean_peak_dbfs"]),
            "rms_db": delta(accepted["aggregate"]["mean_rms_dbfs"], reference["aggregate"]["mean_rms_dbfs"]),
            "crest_db": delta(accepted["aggregate"]["mean_crest_db"], reference["aggregate"]["mean_crest_db"]),
            "p95_rms_db": delta(accepted["aggregate"]["mean_p95_rms_dbfs"], reference["aggregate"]["mean_p95_rms_dbfs"]),
            "p99_rms_db": delta(accepted["aggregate"]["mean_p99_rms_dbfs"], reference["aggregate"]["mean_p99_rms_dbfs"]),
        }
        if any(value is not None and abs(value) >= min_effect_db for value in changes.values()):
            affected.append({"label": track["label"], "accepted_minus_reference": changes})
    if failures:
        return {"status": "unqualified", "failures": failures, "affected_tracks": affected}
    return {
        "status": "limiter_participation_detected" if affected else "no_reliable_limiter_participation_detected",
        "failures": [],
        "affected_tracks": affected,
    }


def render_track(
    script_dir: pathlib.Path,
    eel: pathlib.Path,
    item: dict[str, Any],
    output_dir: pathlib.Path,
    pulse_server: str,
    thresholds_db: list[float],
    repetitions: int,
) -> dict[str, Any]:
    excerpt = output_dir / "excerpt.wav"
    convert_excerpt(item, excerpt)
    thresholds: dict[str, Any] = {}
    for threshold in thresholds_db:
        key = str(threshold)
        captures: list[dict[str, Any]] = []
        wavs: list[pathlib.Path] = []
        threshold_dir = output_dir / f"threshold_{threshold:g}db"
        for number in range(1, repetitions + 1):
            output = threshold_dir / f"render_{number}.wav"
            run(
                [
                    sys.executable,
                    str(script_dir / "render_jdsp_host.py"),
                    str(excerpt),
                    str(eel),
                    str(output),
                    "--pulse-server",
                    pulse_server,
                    "--pre-roll-ms",
                    "500",
                    "--tail-ms",
                    "2000",
                    "--master-limiter-threshold-db",
                    str(threshold),
                ],
                f"{item['label']} threshold {threshold:g} dB render {number}",
            )
            capture, integrity = read_capture(output)
            if not capture:
                raise QualificationError(f"invalid host capture for {item['label']} at {threshold:g} dB: {integrity}")
            combined = analyze_capture(capture, -90.0)["channels"]["combined"]
            captures.append({**combined, **window_metrics(capture)})
            wavs.append(output)
        repeat_json = threshold_dir / "repeatability.json"
        repeat_md = threshold_dir / "repeatability.md"
        result = subprocess.run(
            [
                sys.executable,
                str(script_dir / "qualify_jdsp_repeatability.py"),
                *[str(wav) for wav in wavs],
                "--max-peak-spread-db",
                "0.10",
                "--max-rms-spread-db",
                "0.10",
                "--min-correlation",
                "0.999",
                "--json",
                str(repeat_json),
                "--markdown",
                str(repeat_md),
            ],
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode not in (0, 1):
            raise QualificationError(result.stderr.strip() or "repeatability runner failed")
        thresholds[key] = {
            "threshold_db": threshold,
            "captures": captures,
            "aggregate": aggregate_capture_metrics(captures),
            "repeatability": json.loads(repeat_json.read_text(encoding="ascii")),
            "report": str(repeat_md),
        }
    return {
        "label": item["label"],
        "name": item["name"],
        "start_seconds": item["start_seconds"],
        "duration_seconds": item["duration_seconds"],
        "thresholds": thresholds,
    }


def format_value(value: float | None) -> str:
    return "-" if value is None else f"{value:.3f}"


def markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Axiom JDSP Limiter-Threshold Sweep",
        "",
        f"Status: **{report['classification']['status'].upper()}**",
        "",
        "This is a same-script host-path measurement. A threshold-correlated difference identifies JDSP limiter participation, not an EEL defect by itself.",
        "",
        f"Reference threshold: `{report['reference_threshold_db']:.2f} dB`; accepted threshold: `{report['accepted_threshold_db']:.2f} dB`; reliable-effect floor: `{report['min_effect_db']:.3f} dB`.",
        "",
    ]
    for track in report["tracks"]:
        lines.extend(
            [
                f"## {track['label']}",
                "",
                "| Limiter threshold (dB) | Repeatability | Mean peak (dBFS) | Mean RMS (dBFS) | Mean crest (dB) | Mean P95 20 ms RMS (dBFS) | Mean P99 20 ms RMS (dBFS) |",
                "| ---: | --- | ---: | ---: | ---: | ---: | ---: |",
            ]
        )
        for threshold in report["thresholds_db"]:
            result = track["thresholds"][str(threshold)]
            aggregate = result["aggregate"]
            lines.append(
                f"| {threshold:.2f} | {result['repeatability']['status'].upper()} | "
                f"{format_value(aggregate['mean_peak_dbfs'])} | {format_value(aggregate['mean_rms_dbfs'])} | "
                f"{format_value(aggregate['mean_crest_db'])} | {format_value(aggregate['mean_p95_rms_dbfs'])} | "
                f"{format_value(aggregate['mean_p99_rms_dbfs'])} |"
            )
        lines.append("")
    if report["classification"]["affected_tracks"]:
        lines.extend(["## Accepted Versus Reference Threshold", ""])
        for affected in report["classification"]["affected_tracks"]:
            values = affected["accepted_minus_reference"]
            lines.append(
                f"- `{affected['label']}`: peak `{format_value(values['peak_db'])} dB`, "
                f"RMS `{format_value(values['rms_db'])} dB`, crest `{format_value(values['crest_db'])} dB`, "
                f"P95 window RMS `{format_value(values['p95_rms_db'])} dB`, "
                f"P99 window RMS `{format_value(values['p99_rms_db'])} dB`."
            )
    if report["classification"]["failures"]:
        lines.extend(["", "## Qualification Failures", ""])
        lines.extend(f"- {failure}" for failure in report["classification"]["failures"])
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("eel_script", type=pathlib.Path)
    parser.add_argument("manifest", type=pathlib.Path)
    parser.add_argument("output_dir", type=pathlib.Path)
    parser.add_argument("--pulse-server", default=DEFAULT_PULSE_SERVER)
    parser.add_argument("--route-helper", type=pathlib.Path, default=DEFAULT_ROUTE_HELPER)
    parser.add_argument("--skip-route-start", action="store_true")
    parser.add_argument("--keep-route-running", action="store_true")
    parser.add_argument("--label-regex", default="electronic", help="case-insensitive manifest label filter; empty selects all")
    parser.add_argument("--threshold-db", type=float, action="append", dest="thresholds_db")
    parser.add_argument("--accepted-threshold-db", type=float, default=-1.0)
    parser.add_argument("--repetitions", type=int, default=5)
    parser.add_argument("--min-effect-db", type=float, default=0.15)
    args = parser.parse_args()
    thresholds = args.thresholds_db or [0.0, -1.0, -3.0]
    if len(set(thresholds)) != len(thresholds) or not all(-30.0 <= value <= 0.0 for value in thresholds):
        parser.error("thresholds must be unique values in [-30, 0] dB")
    if args.accepted_threshold_db not in thresholds:
        parser.error("--accepted-threshold-db must be included in --threshold-db values")
    if args.repetitions < 2:
        parser.error("--repetitions must be at least 2")
    eel = args.eel_script.resolve()
    if not eel.is_file():
        parser.error(f"EEL script not found: {eel}")
    items = read_manifest(args.manifest.resolve())
    if args.label_regex:
        pattern = re.compile(args.label_regex, re.IGNORECASE)
        items = [item for item in items if pattern.search(item["label"])]
    if not items:
        parser.error("no manifest items match --label-regex")
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
        tracks = [
            render_track(script_dir, eel, item, output_dir / item["name"], args.pulse_server, thresholds, args.repetitions)
            for item in items
        ]
        report = {
            "scope": "same accepted EEL script rendered through JDSP at controlled terminal-limiter thresholds",
            "eel_script": str(eel),
            "manifest": str(args.manifest.resolve()),
            "thresholds_db": thresholds,
            "reference_threshold_db": max(thresholds),
            "accepted_threshold_db": args.accepted_threshold_db,
            "repetitions": args.repetitions,
            "min_effect_db": args.min_effect_db,
            "tracks": tracks,
        }
        report["classification"] = classify(
            tracks, report["reference_threshold_db"], args.accepted_threshold_db, args.min_effect_db
        )
        (output_dir / "limiter_sweep.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        (output_dir / "limiter_sweep.md").write_text(markdown(report), encoding="utf-8")
        print(output_dir / "limiter_sweep.json")
        print(output_dir / "limiter_sweep.md")
        print(f"status={report['classification']['status']}")
        return 1 if report["classification"]["status"] == "unqualified" else 0
    finally:
        if route_started and not args.keep_route_running:
            for error in stop_managed_route(args.pulse_server):
                print(f"warning: {error}", file=sys.stderr)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (MaterialError, QualificationError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1)
