#!/usr/bin/env python3
"""Establish a repeated dense-material host baseline at Axiom's accepted limiter setting."""

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
    stop_managed_route,
    validate_route,
)


LEVEL_METRICS = ("rms_dbfs", "p95_rms_dbfs", "p99_rms_dbfs")


def evaluate_tracks(tracks: list[dict[str, Any]], threshold_db: float, ceiling_dbfs: float) -> dict[str, Any]:
    checks: list[dict[str, str]] = []
    for track in tracks:
        result = track["thresholds"][str(threshold_db)]
        captures = result["captures"]
        metrics = result["metric_qualification"]
        clipped = metrics["clipped_samples"]
        silent = any(capture["silent"] for capture in captures)
        qualified = [
            name for name, metric in metrics["metrics"].items()
            if metric["qualified"]
        ]
        level_qualified = [name for name in qualified if name in LEVEL_METRICS]
        maximum_peak = max(capture["peak_dbfs"] for capture in captures if capture["peak_dbfs"] is not None)
        failures: list[str] = []
        if silent:
            failures.append("one or more renders were silent")
        if clipped:
            failures.append(f"{clipped} clipped channel samples were observed")
        if not level_qualified:
            failures.append("no repeated level metric qualified within spread policy")
        terminal_pressure = maximum_peak > ceiling_dbfs
        checks.append(
            {
                "name": f"stress_{track['name']}_integrity",
                "status": "fail" if failures else "pass",
                "detail": "; ".join(failures) if failures else
                    f"non-clipping repeated metrics: {', '.join(qualified)}",
            }
        )
        checks.append(
            {
                "name": f"stress_{track['name']}_terminal_margin",
                "status": "investigate" if terminal_pressure else "pass",
                "detail": (
                    f"highest repeated peak={maximum_peak:.3f} dBFS; "
                    + (
                        f"retain accepted host-limiter pressure above {ceiling_dbfs:.3f} dBFS"
                        if terminal_pressure else
                        f"within observation boundary <= {ceiling_dbfs:.3f} dBFS"
                    )
                ),
            }
        )
    status = "fail" if any(check["status"] == "fail" for check in checks) else (
        "pass_with_investigation" if any(check["status"] == "investigate" for check in checks) else "pass"
    )
    return {"status": status, "checks": checks}


def markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Axiom Accepted-Setting Dense-Material Stress Baseline",
        "",
        f"Status: **{report['evaluation']['status'].upper()}**",
        "",
        "This report characterizes the accepted EEL script through JDSP at the accepted terminal-limiter setting. "
        "Near-ceiling output is recorded as baseline host-limiter pressure; clipping or unrepeatable level metrics fail the gate.",
        "",
        f"Host limiter threshold: `{report['threshold_db']:.2f} dB`; repetitions per excerpt: `{report['repetitions']}`; "
        f"terminal-pressure observation level: `{report['ceiling_dbfs']:.2f} dBFS`.",
        "",
        "| Material | Qualified scalar metrics | Mean peak (dBFS) | Highest peak (dBFS) | Mean RMS (dBFS) | Mean P95 20 ms RMS (dBFS) | Clipped samples |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for track in report["tracks"]:
        result = track["thresholds"][str(report["threshold_db"])]
        aggregate = result["aggregate"]
        metrics = result["metric_qualification"]
        qualified = [name for name, metric in metrics["metrics"].items() if metric["qualified"]]
        highest = max(capture["peak_dbfs"] for capture in result["captures"] if capture["peak_dbfs"] is not None)
        label = track["label"].replace("|", "\\|")
        lines.append(
            f"| {label} | {', '.join(qualified) or '-'} | "
            f"{format_value(aggregate['mean_peak_dbfs'])} | {format_value(highest)} | "
            f"{format_value(aggregate['mean_rms_dbfs'])} | {format_value(aggregate['mean_p95_rms_dbfs'])} | "
            f"{metrics['clipped_samples']} |"
        )
    lines.extend(["", "## Checks", "", "| Check | Status | Detail |", "| --- | --- | --- |"])
    lines.extend(
        f"| {check['name']} | {check['status'].upper()} | {check['detail']} |"
        for check in report["evaluation"]["checks"]
    )
    lines.extend(
        [
            "",
            "Use this artifact as the accepted `.8` reference for future dense-material candidate investigations. "
            "It is host-path evidence and does not establish a defect in the EEL script.",
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
    parser.add_argument("--repetitions", type=int, default=3)
    parser.add_argument("--ceiling-dbfs", type=float, default=-0.50)
    parser.add_argument("--max-metric-spread-db", type=float, default=0.10)
    args = parser.parse_args()
    if not -30.0 <= args.threshold_db <= 0.0:
        parser.error("--threshold-db must be in [-30, 0] dB")
    if args.repetitions < 2:
        parser.error("--repetitions must be at least 2")
    if args.max_metric_spread_db <= 0.0:
        parser.error("--max-metric-spread-db must be positive")
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
            render_track(
                script_dir, eel, item, output_dir / item["name"], args.pulse_server,
                [args.threshold_db], args.repetitions, args.max_metric_spread_db
            )
            for item in items
        ]
        report = {
            "scope": "accepted EEL script rendered repeatedly through JDSP on registered dense material",
            "eel_script": str(eel),
            "manifest": str(args.manifest.resolve()),
            "threshold_db": args.threshold_db,
            "repetitions": args.repetitions,
            "ceiling_dbfs": args.ceiling_dbfs,
            "max_metric_spread_db": args.max_metric_spread_db,
            "tracks": tracks,
        }
        report["evaluation"] = evaluate_tracks(tracks, args.threshold_db, args.ceiling_dbfs)
        (output_dir / "accepted_stress.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        (output_dir / "accepted_stress.md").write_text(markdown(report), encoding="utf-8")
        print(output_dir / "accepted_stress.json")
        print(output_dir / "accepted_stress.md")
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
