#!/usr/bin/env python3
"""Qualify reduced elevated-bass reserve slopes across the user control range."""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys
from typing import Any

from run_jdsp_limiter_sweep import format_value, render_track
from run_jdsp_local_material import MaterialError, read_manifest
from run_jdsp_reserve_law_screen import reserve_fixture
from run_jdsp_wsl_qualification import (
    DEFAULT_PULSE_SERVER,
    DEFAULT_ROUTE_HELPER,
    QualificationError,
    run,
    stop_managed_route,
    validate_route,
)


def track_problem(track: dict[str, Any], threshold_db: float, ceiling_dbfs: float) -> tuple[str, str] | None:
    result = track["thresholds"][str(threshold_db)]
    metrics = result["metric_qualification"]
    captures = result["captures"]
    if any(capture["silent"] for capture in captures):
        return "fail", "silent render observed"
    if not metrics["metrics"]["rms_dbfs"]["qualified"]:
        return "fail", "repeated RMS level did not qualify within spread policy"
    highest = max(capture["peak_dbfs"] for capture in captures if capture["peak_dbfs"] is not None)
    if metrics["clipped_samples"] or highest > ceiling_dbfs:
        return (
            "reject",
            f"clipping={metrics['clipped_samples']}, highest peak={highest:.3f} dBFS; "
            f"required <= {ceiling_dbfs:.3f} dBFS",
        )
    return None


def evaluate_range(
    slope_runs: list[dict[str, Any]],
    threshold_db: float,
    ceiling_dbfs: float,
    slider_values_db: list[float],
) -> dict[str, Any]:
    checks: list[dict[str, str]] = []
    viable: list[float] = []
    rejected: list[float] = []
    failed = False
    for slope_run in slope_runs:
        slope = slope_run["reserve_slope"]
        rejected_slope = False
        measured_sliders = [entry["slider_db"] for entry in slope_run["slider_runs"]]
        for slider_run in slope_run["slider_runs"]:
            slider_db = slider_run["slider_db"]
            for track in slider_run["tracks"]:
                problem = track_problem(track, threshold_db, ceiling_dbfs)
                if not problem:
                    continue
                status, detail = problem
                checks.append({
                    "name": f"slope_{slope:g}_slider_{slider_db:g}_{track['name']}",
                    "status": status,
                    "detail": detail,
                })
                if status == "fail":
                    failed = True
                else:
                    rejected_slope = True
        if rejected_slope:
            rejected.append(slope)
        elif set(measured_sliders) != set(slider_values_db):
            failed = True
            checks.append({
                "name": f"slope_{slope:g}_coverage",
                "status": "fail",
                "detail": "slope ended without either full slider coverage or a verified rejection",
            })
        elif not failed:
            viable.append(slope)
    if failed:
        status = "fail"
    elif viable:
        status = "viable_reduced_reserve_range_identified"
    else:
        status = "no_reduced_reserve_range_qualifies"
    return {
        "status": status,
        "checks": checks,
        "viable_reserve_slopes": sorted(viable),
        "rejected_reserve_slopes": sorted(rejected),
    }


def markdown(report: dict[str, Any]) -> str:
    evaluation = report["evaluation"]
    lines = [
        "# Axiom Reduced-Reserve Range Qualification",
        "",
        f"Status: **{evaluation['status'].upper()}**",
        "",
        "This is a pre-candidate range qualification using temporary EEL fixtures. It does not edit or accept an Axiom DSP script.",
        "",
        f"Host limiter threshold: `{report['threshold_db']:.2f} dB`; measured repetitions per fixture and excerpt: "
        f"`{report['repetitions']}`; excluded conditioning renders per set: `{report['conditioning_renders']}`; "
        f"maximum conditioned attempts for unstable measurement: `{report['max_measurement_attempts']}`; "
        f"peak observation limit: `{report['ceiling_dbfs']:.2f} dBFS`.",
        "",
        "| Reserve slope | Slider | Material | Attempt used | Mean peak (dBFS) | Highest peak (dBFS) | Mean RMS (dBFS) | Clipped samples |",
        "| ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for slope_run in report["slope_runs"]:
        for slider_run in slope_run["slider_runs"]:
            for track in slider_run["tracks"]:
                result = track["thresholds"][str(report["threshold_db"])]
                aggregate = result["aggregate"]
                metrics = result["metric_qualification"]
                highest = max(capture["peak_dbfs"] for capture in result["captures"] if capture["peak_dbfs"] is not None)
                label = track["label"].replace("|", "\\|")
                lines.append(
                    f"| {slope_run['reserve_slope']:.3f} | {slider_run['slider_db']:+.1f} dB | {label} | "
                    f"{track.get('measurement_attempt', 1)} | {format_value(aggregate['mean_peak_dbfs'])} | {format_value(highest)} | "
                    f"{format_value(aggregate['mean_rms_dbfs'])} | {metrics['clipped_samples']} |"
                )
    lines.extend(["", "## Decision", ""])
    lines.append(
        "- Slopes retaining full tested-range eligibility: "
        f"`{', '.join(f'{value:.3f}' for value in evaluation['viable_reserve_slopes']) or 'none'}`."
    )
    lines.append(
        "- Slopes rejected after a measured unsafe operating point: "
        f"`{', '.join(f'{value:.3f}' for value in evaluation['rejected_reserve_slopes']) or 'none'}`."
    )
    if evaluation["checks"]:
        lines.extend(["", "## Findings", "", "| Check | Status | Detail |", "| --- | --- | --- |"])
        lines.extend(f"| {item['name']} | {item['status'].upper()} | {item['detail']} |" for item in evaluation["checks"])
    lines.extend(
        [
            "",
            "A rejected slope is not rendered further once a verified unsafe setting makes full-range qualification impossible.",
            "",
        ]
    )
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
    parser.add_argument("--label-regex", default="", help="case-insensitive manifest label filter; empty selects all")
    parser.add_argument("--threshold-db", type=float, default=-1.0)
    parser.add_argument("--reserve-slope", type=float, action="append", dest="reserve_slopes")
    parser.add_argument("--slider-db", type=float, action="append", dest="slider_values_db")
    parser.add_argument("--repetitions", type=int, default=3)
    parser.add_argument("--conditioning-renders", type=int, default=1)
    parser.add_argument("--max-measurement-attempts", type=int, default=2)
    parser.add_argument("--ceiling-dbfs", type=float, default=-0.50)
    parser.add_argument("--max-metric-spread-db", type=float, default=0.10)
    args = parser.parse_args()
    slopes = args.reserve_slopes or [0.75, 0.5]
    sliders = args.slider_values_db or [12.0, 10.0, 8.0, 6.0]
    if len(set(slopes)) != len(slopes) or not all(0.0 <= value < 1.0 for value in slopes):
        parser.error("reserve slopes must be unique reduced-law values in [0, 1)")
    if len(set(sliders)) != len(sliders) or not all(4.0 < value <= 12.0 for value in sliders):
        parser.error("slider values must be unique elevated values in (4, 12]")
    if not -30.0 <= args.threshold_db <= 0.0:
        parser.error("--threshold-db must be in [-30, 0] dB")
    if args.repetitions < 2 or args.conditioning_renders < 0 or args.max_measurement_attempts < 1 or args.max_metric_spread_db <= 0.0:
        parser.error("invalid repetitions, conditioning renders, measurement attempts, or metric spread")
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
        slope_runs: list[dict[str, Any]] = []
        for slope in slopes:
            slider_runs: list[dict[str, Any]] = []
            stop_slope = False
            for slider_db in sliders:
                fixture = output_dir / "fixtures" / f"{eel.stem}_sub_{slider_db:g}db_reserve_{slope:g}.eel"
                reserve_fixture(eel, fixture, slider_db, slope)
                tracks: list[dict[str, Any]] = []
                for item in items:
                    problem: tuple[str, str] | None = None
                    for attempt in range(1, args.max_measurement_attempts + 1):
                        track = render_track(
                            script_dir, fixture, item,
                            output_dir / f"slope_{slope:g}" / f"slider_{slider_db:g}db" / item["name"] / f"attempt_{attempt}",
                            args.pulse_server, [args.threshold_db], args.repetitions, args.max_metric_spread_db,
                            conditioning_renders=args.conditioning_renders,
                        )
                        track["measurement_attempt"] = attempt
                        problem = track_problem(track, args.threshold_db, args.ceiling_dbfs)
                        if not problem or problem[0] != "fail":
                            break
                    tracks.append(track)
                    if problem:
                        stop_slope = True
                        break
                slider_runs.append({"slider_db": slider_db, "fixture": str(fixture), "tracks": tracks})
                if stop_slope:
                    break
            slope_runs.append({"reserve_slope": slope, "slider_runs": slider_runs})
        report = {
            "scope": "temporary reduced-reserve fixtures range-qualified before candidate creation",
            "eel_script": str(eel),
            "manifest": str(args.manifest.resolve()),
            "label_regex": args.label_regex,
            "threshold_db": args.threshold_db,
            "reserve_slopes": slopes,
            "slider_values_db": sliders,
            "repetitions": args.repetitions,
            "conditioning_renders": args.conditioning_renders,
            "max_measurement_attempts": args.max_measurement_attempts,
            "ceiling_dbfs": args.ceiling_dbfs,
            "max_metric_spread_db": args.max_metric_spread_db,
            "slope_runs": slope_runs,
        }
        report["evaluation"] = evaluate_range(slope_runs, args.threshold_db, args.ceiling_dbfs, sliders)
        (output_dir / "reserve_range_qualification.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        (output_dir / "reserve_range_qualification.md").write_text(markdown(report), encoding="utf-8")
        print(output_dir / "reserve_range_qualification.json")
        print(output_dir / "reserve_range_qualification.md")
        print(f"status={report['evaluation']['status']}")
        return 1 if report["evaluation"]["status"] == "fail" else 0
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
