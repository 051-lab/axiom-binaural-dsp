#!/usr/bin/env python3
"""Map accepted Axiom output across Sub Harmonics Gain settings on dense material."""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys
from typing import Any

from run_jdsp_accepted_stress import LEVEL_METRICS
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


def evaluate_map(
    slider_tracks: list[dict[str, Any]],
    threshold_db: float,
    default_slider_db: float,
    ceiling_dbfs: float,
    retreat_observation_db: float = 1.0,
) -> dict[str, Any]:
    checks: list[dict[str, str]] = []
    clipped_slider_values: set[float] = set()
    pressure_slider_values: set[float] = set()
    measurement_failure = False
    default_failure = False
    default_tracks = next(slider["tracks"] for slider in slider_tracks if slider["slider_db"] == default_slider_db)
    default_by_name = {track["name"]: track for track in default_tracks}
    retreat_findings: list[dict[str, Any]] = []
    for slider in slider_tracks:
        slider_db = slider["slider_db"]
        for track in slider["tracks"]:
            result = track["thresholds"][str(threshold_db)]
            metrics = result["metric_qualification"]
            captures = result["captures"]
            clipped = metrics["clipped_samples"]
            silent = any(capture["silent"] for capture in captures)
            flawed_source = track.get("material_class") == "flawed_source"
            qualified = [name for name, metric in metrics["metrics"].items() if metric["qualified"]]
            level_qualified = [name for name in qualified if name in LEVEL_METRICS]
            highest = max(capture["peak_dbfs"] for capture in captures if capture["peak_dbfs"] is not None)
            if silent:
                measurement_failure = True
                checks.append({
                    "name": f"slider_{slider_db:g}_{track['name']}_measurement",
                    "status": "fail",
                    "detail": "silent render observed",
                })
                continue
            if not level_qualified:
                if flawed_source and clipped:
                    checks.append({
                        "name": f"slider_{slider_db:g}_{track['name']}_measurement",
                        "status": "investigate",
                        "detail": "no repeated level metric qualified because clipping is part of the source stress case",
                    })
                else:
                    measurement_failure = True
                    checks.append({
                        "name": f"slider_{slider_db:g}_{track['name']}_measurement",
                        "status": "fail",
                        "detail": "no repeated level metric qualified within spread policy",
                    })
                    continue
            if clipped:
                checks.append({
                    "name": f"slider_{slider_db:g}_{track['name']}_clipping",
                    "status": "investigate" if flawed_source else ("fail" if slider_db == default_slider_db else "boundary"),
                    "detail": (
                        f"{clipped} clipped channel samples in flawed-source material at slider={slider_db:+.1f} dB"
                        if flawed_source else
                        f"{clipped} clipped channel samples at slider={slider_db:+.1f} dB"
                    ),
                })
                if not flawed_source:
                    clipped_slider_values.add(slider_db)
                    if slider_db == default_slider_db:
                        default_failure = True
            if highest > ceiling_dbfs:
                pressure_slider_values.add(slider_db)
                checks.append({
                    "name": f"slider_{slider_db:g}_{track['name']}_terminal_margin",
                    "status": "investigate",
                    "detail": (
                        f"highest repeated peak={highest:.3f} dBFS at slider={slider_db:+.1f} dB; "
                        f"above observation boundary {ceiling_dbfs:.3f} dBFS"
                    ),
                })
            if slider_db != default_slider_db:
                reference = default_by_name[track["name"]]["thresholds"][str(threshold_db)]
                reference_rms = reference["metric_qualification"]["metrics"]["rms_dbfs"]
                candidate_rms = metrics["metrics"]["rms_dbfs"]
                if reference_rms["qualified"] and candidate_rms["qualified"]:
                    rms_delta = candidate_rms["mean_db"] - reference_rms["mean_db"]
                    if rms_delta <= -retreat_observation_db:
                        retreat_findings.append({
                            "slider_db": slider_db,
                            "track_name": track["name"],
                            "label": track["label"],
                            "rms_delta_from_default_db": rms_delta,
                        })
                        checks.append({
                            "name": f"slider_{slider_db:g}_{track['name']}_level_retreat",
                            "status": "investigate",
                            "detail": (
                                f"mean RMS change={rms_delta:+.3f} dB versus {default_slider_db:+.1f} dB default; "
                                f"observe broadband level retreat beyond -{retreat_observation_db:.3f} dB"
                            ),
                        })
    if measurement_failure or default_failure:
        status = "fail"
    elif clipped_slider_values:
        status = "usable_range_boundary_detected"
    elif pressure_slider_values or retreat_findings:
        status = "pass_with_investigation"
    else:
        status = "pass"
    safe_slider_values = [
        slider["slider_db"] for slider in slider_tracks
        if slider["slider_db"] not in clipped_slider_values
    ]
    return {
        "status": status,
        "checks": checks,
        "clipped_slider_values_db": sorted(clipped_slider_values),
        "pressure_slider_values_db": sorted(pressure_slider_values),
        "retreat_observation_db": retreat_observation_db,
        "level_retreat_findings": retreat_findings,
        "safe_slider_values_tested_db": safe_slider_values,
        "highest_tested_unclipped_slider_db": max(safe_slider_values) if safe_slider_values else None,
    }


def markdown(report: dict[str, Any]) -> str:
    evaluation = report["evaluation"]
    lines = [
        "# Axiom Sub Harmonics Dense-Material Stress Map",
        "",
        f"Status: **{evaluation['status'].upper()}**",
        "",
        "This report maps the selected accepted EEL script through JDSP while changing only the `Sub Harmonics Gain (dB)` default in temporary external fixtures. "
        "A boundary at elevated gain is a measured usable-range limit, not a failure of the accepted default setting.",
        "",
        f"Host limiter threshold: `{report['threshold_db']:.2f} dB`; repetitions per excerpt and slider value: `{report['repetitions']}`; "
        f"terminal-pressure observation level: `{report['ceiling_dbfs']:.2f} dBFS`.",
        "",
        "| Slider (dB) | Material | Mean peak (dBFS) | Highest peak (dBFS) | Mean RMS (dBFS) | Mean P95 20 ms RMS (dBFS) | Clipped samples | Qualified scalar metrics |",
        "| ---: | --- | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for slider in report["slider_tracks"]:
        for track in slider["tracks"]:
            result = track["thresholds"][str(report["threshold_db"])]
            aggregate = result["aggregate"]
            metrics = result["metric_qualification"]
            highest = max(capture["peak_dbfs"] for capture in result["captures"] if capture["peak_dbfs"] is not None)
            qualified = [name for name, metric in metrics["metrics"].items() if metric["qualified"]]
            label = track["label"].replace("|", "\\|")
            lines.append(
                f"| {slider['slider_db']:+.1f} | {label} | {format_value(aggregate['mean_peak_dbfs'])} | "
                f"{format_value(highest)} | {format_value(aggregate['mean_rms_dbfs'])} | "
                f"{format_value(aggregate['mean_p95_rms_dbfs'])} | {metrics['clipped_samples']} | "
                f"{', '.join(qualified) or '-'} |"
            )
    lines.extend(["", "## Range Finding", ""])
    lines.append(
        f"- Highest tested slider setting without clipped samples: "
        f"`{format_value(evaluation['highest_tested_unclipped_slider_db'])} dB`."
    )
    lines.append(
        f"- Slider settings with clipped samples: "
        f"`{', '.join(f'{value:+.1f} dB' for value in evaluation['clipped_slider_values_db']) or 'none'}`."
    )
    lines.append(
        f"- Slider settings reaching the terminal-pressure observation zone: "
        f"`{', '.join(f'{value:+.1f} dB' for value in evaluation['pressure_slider_values_db']) or 'none'}`."
    )
    retreat_values = sorted({finding["slider_db"] for finding in evaluation["level_retreat_findings"]})
    lines.append(
        f"- Slider settings with repeatable RMS retreat beyond `-{evaluation['retreat_observation_db']:.3f} dB` versus default: "
        f"`{', '.join(f'{value:+.1f} dB' for value in retreat_values) or 'none'}`."
    )
    if evaluation["checks"]:
        lines.extend(["", "## Findings", "", "| Check | Status | Detail |", "| --- | --- | --- |"])
        lines.extend(
            f"| {check['name']} | {check['status'].upper()} | {check['detail']} |"
            for check in evaluation["checks"]
        )
    lines.extend(
        [
            "",
            "Use this map to decide whether a sound-changing candidate is justified and to define safe listening targets for user-adjustable bass gain.",
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
    parser.add_argument("--default-slider-db", type=float, default=4.0)
    parser.add_argument("--slider-db", type=float, action="append", dest="slider_values_db")
    parser.add_argument("--repetitions", type=int, default=3)
    parser.add_argument("--ceiling-dbfs", type=float, default=-0.50)
    parser.add_argument("--max-metric-spread-db", type=float, default=0.10)
    parser.add_argument("--retreat-observation-db", type=float, default=1.0)
    parser.add_argument("--sample-rate", type=int, default=48000)
    args = parser.parse_args()
    slider_values = args.slider_values_db or [4.0, 6.0, 8.0, 10.0, 12.0]
    if len(set(slider_values)) != len(slider_values) or args.default_slider_db not in slider_values:
        parser.error("slider values must be unique and include --default-slider-db")
    if not all(-12.0 <= value <= 12.0 for value in slider_values):
        parser.error("slider values must be in [-12, 12] dB")
    if not -30.0 <= args.threshold_db <= 0.0:
        parser.error("--threshold-db must be in [-30, 0] dB")
    if args.repetitions < 3:
        parser.error("--repetitions must be at least 3 for repeatability qualification")
    if args.max_metric_spread_db <= 0.0 or args.retreat_observation_db <= 0.0:
        parser.error("metric spread and retreat observation values must be positive")
    if args.sample_rate < 8000:
        parser.error("--sample-rate must be at least 8000")
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
    fixtures = output_dir / "fixtures"
    route_started = False
    try:
        if not args.skip_route_start:
            if not args.route_helper.is_file():
                raise QualificationError(f"route helper not found: {args.route_helper}")
            run([str(args.route_helper)], "start managed JamesDSP WSL audio route")
            route_started = True
        validate_route(args.pulse_server)
        script_dir = pathlib.Path(__file__).resolve().parent
        slider_tracks: list[dict[str, Any]] = []
        for slider_db in slider_values:
            fixture = eel
            if slider_db != args.default_slider_db:
                fixture = fixtures / f"{eel.stem}_sub_{slider_db:g}db.eel"
                slider_fixture(eel, fixture, slider_db)
            tracks = [
                render_track(
                    script_dir, fixture, item, output_dir / f"slider_{slider_db:g}db" / item["name"],
                    args.pulse_server, [args.threshold_db], args.repetitions, args.max_metric_spread_db,
                    sample_rate=args.sample_rate,
                )
                for item in items
            ]
            slider_tracks.append({"slider_db": slider_db, "eel_fixture": str(fixture), "tracks": tracks})
        report = {
            "scope": "accepted EEL script rendered through JDSP with temporary Sub Harmonics Gain fixtures",
            "eel_script": str(eel),
            "manifest": str(args.manifest.resolve()),
            "threshold_db": args.threshold_db,
            "default_slider_db": args.default_slider_db,
            "slider_values_db": slider_values,
            "repetitions": args.repetitions,
            "ceiling_dbfs": args.ceiling_dbfs,
            "max_metric_spread_db": args.max_metric_spread_db,
            "retreat_observation_db": args.retreat_observation_db,
            "sample_rate_hz": args.sample_rate,
            "slider_tracks": slider_tracks,
        }
        report["evaluation"] = evaluate_map(
            slider_tracks, args.threshold_db, args.default_slider_db, args.ceiling_dbfs,
            args.retreat_observation_db,
        )
        (output_dir / "sub_slider_map.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        (output_dir / "sub_slider_map.md").write_text(markdown(report), encoding="utf-8")
        print(output_dir / "sub_slider_map.json")
        print(output_dir / "sub_slider_map.md")
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
