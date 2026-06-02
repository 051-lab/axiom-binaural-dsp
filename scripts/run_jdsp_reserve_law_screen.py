#!/usr/bin/env python3
"""Screen temporary elevated-bass reserve laws against accepted Axiom output."""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys
from typing import Any

from run_jdsp_limiter_sweep import format_value, render_track
from run_jdsp_local_material import MaterialError, read_manifest
from run_jdsp_wsl_qualification import (
    DEFAULT_PULSE_SERVER,
    DEFAULT_ROUTE_HELPER,
    QualificationError,
    run,
    slider_fixture,
    stop_managed_route,
    validate_route,
)


CURRENT_RESERVE_LINE = (
    "outputGain = (slider1 > 4.0) ? "
    "(headroomGain * exp(-((slider1 - 4.0) * 0.75) * DB_2_LOG)) : headroomGain;"
)
RESERVE_OUTPUT_GAIN_PATTERN = re.compile(
    r"outputGain = \(slider1 > 4\.0\) \? "
    r"\(headroomGain \* exp\(-\(\(slider1 - 4\.0\) \* [0-9.]+\) \* DB_2_LOG\)\) : headroomGain;"
)


def reserve_fixture(source: pathlib.Path, destination: pathlib.Path, slider_db: float, slope: float) -> None:
    slider_fixture(source, destination, slider_db)
    text = destination.read_text(encoding="ascii")
    matches = RESERVE_OUTPUT_GAIN_PATTERN.findall(text)
    if len(matches) != 1:
        raise QualificationError(f"cannot create reserve-law fixture from {source}: reserve expression missing")
    replacement = (
        "outputGain = (slider1 > 4.0) ? "
        f"(headroomGain * exp(-((slider1 - 4.0) * {slope:g}) * DB_2_LOG)) : headroomGain;"
    )
    destination.write_text(RESERVE_OUTPUT_GAIN_PATTERN.sub(replacement, text, count=1), encoding="ascii")


def evaluate_screen(
    slope_runs: list[dict[str, Any]],
    threshold_db: float,
    reference_slope: float,
    ceiling_dbfs: float,
    minimum_recovery_db: float,
) -> dict[str, Any]:
    checks: list[dict[str, str]] = []
    reference = next(run for run in slope_runs if run["reserve_slope"] == reference_slope)
    reference_by_name = {track["name"]: track for track in reference["tracks"]}
    rejected_slopes: set[float] = set()
    failed = False
    candidates: dict[float, list[dict[str, Any]]] = {
        run["reserve_slope"]: [] for run in slope_runs if run["reserve_slope"] != reference_slope
    }
    for slope_run in slope_runs:
        slope = slope_run["reserve_slope"]
        for track in slope_run["tracks"]:
            result = track["thresholds"][str(threshold_db)]
            metrics = result["metric_qualification"]
            captures = result["captures"]
            clipped = metrics["clipped_samples"]
            silent = any(capture["silent"] for capture in captures)
            rms_qualified = metrics["metrics"]["rms_dbfs"]["qualified"]
            highest = max(capture["peak_dbfs"] for capture in captures if capture["peak_dbfs"] is not None)
            if silent or not rms_qualified:
                failed = True
                checks.append({
                    "name": f"slope_{slope:g}_{track['name']}_measurement",
                    "status": "fail",
                    "detail": "silent render observed" if silent else "repeated RMS level did not qualify within spread policy",
                })
                continue
            if slope == reference_slope:
                if clipped or highest > ceiling_dbfs:
                    failed = True
                    checks.append({
                        "name": f"slope_{slope:g}_{track['name']}_reference_safety",
                        "status": "fail",
                        "detail": (
                            f"accepted law is not a safe comparison reference: clipping={clipped}, "
                            f"highest peak={highest:.3f} dBFS"
                        ),
                    })
                continue
            reference_result = reference_by_name[track["name"]]["thresholds"][str(threshold_db)]
            reference_rms = reference_result["metric_qualification"]["metrics"]["rms_dbfs"]
            candidate_rms = metrics["metrics"]["rms_dbfs"]
            recovery = None
            if reference_rms["qualified"] and candidate_rms["qualified"]:
                recovery = candidate_rms["mean_db"] - reference_rms["mean_db"]
            unsafe = clipped > 0 or highest > ceiling_dbfs
            if unsafe:
                rejected_slopes.add(slope)
                checks.append({
                    "name": f"slope_{slope:g}_{track['name']}_headroom",
                    "status": "reject",
                    "detail": (
                        f"clipping={clipped}, highest peak={highest:.3f} dBFS; "
                        f"required <= {ceiling_dbfs:.3f} dBFS"
                    ),
                })
            elif recovery is not None and recovery >= minimum_recovery_db:
                candidates[slope].append({
                    "reserve_slope": slope,
                    "track_name": track["name"],
                    "label": track["label"],
                    "rms_recovery_db": recovery,
                    "highest_peak_dbfs": highest,
                })
    expected_tracks = len(reference["tracks"])
    viable = sorted(
        slope for slope, findings in candidates.items()
        if slope not in rejected_slopes and len(findings) == expected_tracks
    )
    if failed:
        status = "fail"
    elif viable:
        status = "viable_reduced_reserve_identified"
    else:
        status = "full_reserve_retained"
    return {
        "status": status,
        "checks": checks,
        "minimum_recovery_db": minimum_recovery_db,
        "viable_reserve_slopes": viable,
        "rejected_reserve_slopes": sorted(rejected_slopes),
        "findings": [
            finding for slope in viable for finding in candidates[slope]
        ],
    }


def markdown(report: dict[str, Any]) -> str:
    evaluation = report["evaluation"]
    lines = [
        "# Axiom Elevated-Bass Reserve-Law Screen",
        "",
        f"Status: **{evaluation['status'].upper()}**",
        "",
        "This is an experimental fixture screen. It changes only the elevated-bass global reserve law outside the tracked EEL source; no DSP candidate is created.",
        "",
        f"Sub Harmonics setting: `{report['slider_db']:+.1f} dB`; host limiter threshold: `{report['threshold_db']:.2f} dB`; "
        f"measured repetitions per fixture and excerpt: `{report['repetitions']}`; excluded conditioning renders per set: "
        f"`{report['conditioning_renders']}`; peak observation limit: `{report['ceiling_dbfs']:.2f} dBFS`.",
        "",
        "| Reserve slope | Material | Mean peak (dBFS) | Highest peak (dBFS) | Mean RMS (dBFS) | RMS recovery vs reference reserve (dB) | Clipped samples |",
        "| ---: | --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    reference = next(run for run in report["slope_runs"] if run["reserve_slope"] == report["reference_slope"])
    reference_by_name = {track["name"]: track for track in reference["tracks"]}
    for slope_run in report["slope_runs"]:
        for track in slope_run["tracks"]:
            result = track["thresholds"][str(report["threshold_db"])]
            aggregate = result["aggregate"]
            metrics = result["metric_qualification"]
            highest = max(capture["peak_dbfs"] for capture in result["captures"] if capture["peak_dbfs"] is not None)
            ref_metric = reference_by_name[track["name"]]["thresholds"][str(report["threshold_db"])]["metric_qualification"]["metrics"]["rms_dbfs"]
            metric = metrics["metrics"]["rms_dbfs"]
            recovery = metric["mean_db"] - ref_metric["mean_db"] if metric["qualified"] and ref_metric["qualified"] else None
            label = track["label"].replace("|", "\\|")
            lines.append(
                f"| {slope_run['reserve_slope']:.3f} | {label} | "
                f"{format_value(aggregate['mean_peak_dbfs'])} | {format_value(highest)} | "
                f"{format_value(aggregate['mean_rms_dbfs'])} | {format_value(recovery)} | "
                f"{metrics['clipped_samples']} |"
            )
    lines.extend(["", "## Decision", ""])
    lines.append(
        f"- Viable reduced reserve slopes in this focused screen: "
        f"`{', '.join(f'{value:.3f}' for value in evaluation['viable_reserve_slopes']) or 'none'}`."
    )
    lines.append(
        f"- Rejected reserve slopes in this focused screen: "
        f"`{', '.join(f'{value:.3f}' for value in evaluation['rejected_reserve_slopes']) or 'none'}`."
    )
    if evaluation["findings"]:
        lines.extend(["", "## Qualified Recovery", ""])
        for finding in evaluation["findings"]:
            lines.append(
                f"- Slope `{finding['reserve_slope']:.3f}` on `{finding['label']}` recovered "
                f"`{finding['rms_recovery_db']:+.3f} dB` RMS while highest peak remained "
                f"`{finding['highest_peak_dbfs']:.3f} dBFS`."
            )
    if evaluation["checks"]:
        lines.extend(["", "## Rejections Or Failures", "", "| Check | Status | Detail |", "| --- | --- | --- |"])
        lines.extend(f"| {item['name']} | {item['status'].upper()} | {item['detail']} |" for item in evaluation["checks"])
    lines.extend(
        [
            "",
            "A viable focused-screen result justifies broader boundary qualification before creating a versioned DSP candidate.",
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
    parser.add_argument("--label-regex", default="electronic|hip hop")
    parser.add_argument("--threshold-db", type=float, default=-1.0)
    parser.add_argument("--slider-db", type=float, default=8.0)
    parser.add_argument("--reserve-slope", type=float, action="append", dest="reserve_slopes")
    parser.add_argument("--reference-slope", type=float, default=0.75)
    parser.add_argument("--repetitions", type=int, default=3)
    parser.add_argument("--conditioning-renders", type=int, default=2)
    parser.add_argument("--ceiling-dbfs", type=float, default=-0.50)
    parser.add_argument("--max-metric-spread-db", type=float, default=0.10)
    parser.add_argument("--minimum-recovery-db", type=float, default=0.50)
    args = parser.parse_args()
    slopes = args.reserve_slopes or [0.75, 0.7, 0.625, 0.5]
    if len(set(slopes)) != len(slopes) or args.reference_slope not in slopes:
        parser.error("reserve slopes must be unique and include --reference-slope")
    if not all(0.0 <= value <= 1.0 for value in slopes):
        parser.error("reserve slopes must be in [0, 1]")
    if not -12.0 <= args.slider_db <= 12.0 or args.slider_db <= 4.0:
        parser.error("--slider-db must be elevated above +4 dB and within the slider range")
    if not -30.0 <= args.threshold_db <= 0.0:
        parser.error("--threshold-db must be in [-30, 0] dB")
    if args.repetitions < 2:
        parser.error("--repetitions must be at least 2")
    if args.conditioning_renders < 0:
        parser.error("--conditioning-renders must not be negative")
    if args.max_metric_spread_db <= 0.0 or args.minimum_recovery_db <= 0.0:
        parser.error("metric spread and recovery values must be positive")
    eel = args.eel_script.resolve()
    if not eel.is_file():
        parser.error(f"EEL script not found: {eel}")
    pattern = re.compile(args.label_regex, re.IGNORECASE)
    items = [item for item in read_manifest(args.manifest.resolve()) if pattern.search(item["label"])]
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
            fixture = output_dir / "fixtures" / f"{eel.stem}_sub_{args.slider_db:g}db_reserve_{slope:g}.eel"
            reserve_fixture(eel, fixture, args.slider_db, slope)
            tracks = [
                render_track(
                    script_dir, fixture, item, output_dir / f"slope_{slope:g}" / item["name"],
                    args.pulse_server, [args.threshold_db], args.repetitions, args.max_metric_spread_db,
                    conditioning_renders=args.conditioning_renders,
                )
                for item in items
            ]
            slope_runs.append({"reserve_slope": slope, "fixture": str(fixture), "tracks": tracks})
        report = {
            "scope": "temporary reduced-reserve fixtures screened on dense material before candidate creation",
            "eel_script": str(eel),
            "manifest": str(args.manifest.resolve()),
            "label_regex": args.label_regex,
            "slider_db": args.slider_db,
            "threshold_db": args.threshold_db,
            "reference_slope": args.reference_slope,
            "reserve_slopes": slopes,
            "repetitions": args.repetitions,
            "conditioning_renders": args.conditioning_renders,
            "ceiling_dbfs": args.ceiling_dbfs,
            "max_metric_spread_db": args.max_metric_spread_db,
            "minimum_recovery_db": args.minimum_recovery_db,
            "slope_runs": slope_runs,
        }
        report["evaluation"] = evaluate_screen(
            slope_runs, args.threshold_db, args.reference_slope, args.ceiling_dbfs, args.minimum_recovery_db
        )
        (output_dir / "reserve_law_screen.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        (output_dir / "reserve_law_screen.md").write_text(markdown(report), encoding="utf-8")
        print(output_dir / "reserve_law_screen.json")
        print(output_dir / "reserve_law_screen.md")
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
