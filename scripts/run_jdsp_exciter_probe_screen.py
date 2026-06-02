#!/usr/bin/env python3
"""Screen accepted exciter behavior with generated low-level probes through real JDSP."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import pathlib
import struct
import sys
import wave
from collections.abc import Callable
from typing import Any

import run_jdsp_exciter_sensitivity_screen as exciter
from run_jdsp_wsl_qualification import (
    DEFAULT_PULSE_SERVER,
    DEFAULT_ROUTE_HELPER,
    QualificationError,
    run,
    stop_managed_route,
    validate_route,
)


ACCEPTED_BASELINE_SHA256 = "ad7dd7b33f2e62ff03ae08d7101c7ac333d707baef26b952806990ad979b0b0e"
PEAK_SAMPLE = 32767
DEFAULT_SAMPLE_RATE = 48000
DEFAULT_DURATION_SECONDS = 4.0
DEFAULT_MIN_AIR_LIFT_DB = 0.10
DEFAULT_MAX_DULL_AIR_LIFT_DB = 0.20
DEFAULT_MAX_HIGH_LEVEL_AIR_LIFT_DB = 0.20
DEFAULT_MAX_SIBILANCE_PRESENCE_LIFT_DB = 0.60
DEFAULT_DECISION_FLOOR_DBFS = -90.0
DEFAULT_DEPTH_ORDER_TOLERANCE_DB = 0.20
ProbeSignal = Callable[[int, int, int], tuple[float, float]]


def sha256_file(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def clamp(value: float) -> float:
    return max(-1.0, min(1.0, value))


def pcm16(value: float) -> int:
    return int(round(clamp(value) * PEAK_SAMPLE))


def fade(frame: int, total_frames: int, sample_rate: int, fade_ms: float = 30.0) -> float:
    fade_frames = max(1, int(round(sample_rate * fade_ms / 1000.0)))
    if frame < fade_frames:
        return frame / fade_frames
    if frame >= total_frames - fade_frames:
        return max(0.0, (total_frames - frame - 1) / fade_frames)
    return 1.0


def burst(time_s: float, start_s: float, duration_s: float, attack_s: float = 0.015, release_s: float = 0.060) -> float:
    if not start_s <= time_s < start_s + duration_s:
        return 0.0
    elapsed = time_s - start_s
    remaining = start_s + duration_s - time_s
    return min(1.0, elapsed / attack_s, remaining / release_s)


def low_level_air_activation(frame: int, sample_rate: int, total_frames: int) -> tuple[float, float]:
    time_s = frame / sample_rate
    env = fade(frame, total_frames, sample_rate)
    body_l = (
        0.010 * math.sin(2.0 * math.pi * 220.0 * time_s)
        + 0.007 * math.sin(2.0 * math.pi * 660.0 * time_s + 0.17)
        + 0.005 * math.sin(2.0 * math.pi * 1400.0 * time_s + 0.41)
    )
    body_r = (
        0.010 * math.sin(2.0 * math.pi * 220.0 * time_s + 0.03)
        + 0.007 * math.sin(2.0 * math.pi * 660.0 * time_s + 0.29)
        + 0.005 * math.sin(2.0 * math.pi * 1400.0 * time_s + 0.61)
    )
    air_l = (
        0.0045 * math.sin(2.0 * math.pi * 12000.0 * time_s + 0.11)
        + 0.0035 * math.sin(2.0 * math.pi * 15500.0 * time_s + 0.73)
    )
    air_r = (
        0.0045 * math.sin(2.0 * math.pi * 12000.0 * time_s + 0.47)
        + 0.0035 * math.sin(2.0 * math.pi * 15500.0 * time_s + 1.13)
    )
    return env * (body_l + air_l), env * (body_r + air_r)


def low_level_dull_control(frame: int, sample_rate: int, total_frames: int) -> tuple[float, float]:
    time_s = frame / sample_rate
    env = fade(frame, total_frames, sample_rate)
    left = (
        0.012 * math.sin(2.0 * math.pi * 180.0 * time_s)
        + 0.009 * math.sin(2.0 * math.pi * 420.0 * time_s + 0.31)
        + 0.006 * math.sin(2.0 * math.pi * 1100.0 * time_s + 0.77)
    )
    right = (
        0.012 * math.sin(2.0 * math.pi * 180.0 * time_s + 0.05)
        + 0.009 * math.sin(2.0 * math.pi * 420.0 * time_s + 0.43)
        + 0.006 * math.sin(2.0 * math.pi * 1100.0 * time_s + 0.91)
    )
    return env * left, env * right


def low_level_sibilance_texture(frame: int, sample_rate: int, total_frames: int) -> tuple[float, float]:
    time_s = frame / sample_rate
    env = fade(frame, total_frames, sample_rate)
    burst_env = sum(burst(time_s, start, 0.22) for start in (0.45, 1.15, 1.85, 2.55, 3.20))
    body = 0.006 * math.sin(2.0 * math.pi * 300.0 * time_s)
    left = body + burst_env * (
        0.0060 * math.sin(2.0 * math.pi * 6500.0 * time_s + 0.13)
        + 0.0045 * math.sin(2.0 * math.pi * 8800.0 * time_s + 0.37)
        + 0.0035 * math.sin(2.0 * math.pi * 12400.0 * time_s + 0.71)
    )
    right = body + burst_env * (
        0.0060 * math.sin(2.0 * math.pi * 6500.0 * time_s + 0.43)
        + 0.0045 * math.sin(2.0 * math.pi * 8800.0 * time_s + 0.89)
        + 0.0035 * math.sin(2.0 * math.pi * 12400.0 * time_s + 1.19)
    )
    return env * left, env * right


def high_level_air_control(frame: int, sample_rate: int, total_frames: int) -> tuple[float, float]:
    left, right = low_level_air_activation(frame, sample_rate, total_frames)
    return left * 8.0, right * 8.0


PROBES: dict[str, tuple[str, str, ProbeSignal]] = {
    "low_level_air_activation": (
        "Low-level air activation",
        "Quiet harmonic material with existing 12-16 kHz air content; should exercise the level-dependent exciter.",
        low_level_air_activation,
    ),
    "low_level_dull_control": (
        "Low-level dull control",
        "Quiet harmonic material with little air-band content; should not manufacture air from nothing.",
        low_level_dull_control,
    ),
    "low_level_sibilance_texture": (
        "Low-level sibilance texture",
        "Quiet burst material spanning presence, brilliance, and lower air bands; exposes edge or harshness risk.",
        low_level_sibilance_texture,
    ),
    "high_level_air_control": (
        "High-level air control",
        "Louder version of the air-bearing probe; should show much less level-contingent exciter action.",
        high_level_air_control,
    ),
}


def write_probe(path: pathlib.Path, signal: ProbeSignal, sample_rate: int, duration_seconds: float) -> None:
    total_frames = int(round(sample_rate * duration_seconds))
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as output:
        output.setnchannels(2)
        output.setsampwidth(2)
        output.setframerate(sample_rate)
        chunk = bytearray()
        for frame in range(total_frames):
            left, right = signal(frame, sample_rate, total_frames)
            chunk.extend(struct.pack("<hh", pcm16(left), pcm16(right)))
            if len(chunk) >= 16384:
                output.writeframesraw(chunk)
                chunk.clear()
        if chunk:
            output.writeframesraw(chunk)


def generate_probes(
    output_dir: pathlib.Path,
    selected: tuple[str, ...],
    sample_rate: int,
    duration_seconds: float,
) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for name in selected:
        label, description, signal = PROBES[name]
        path = output_dir / f"{name}.wav"
        write_probe(path, signal, sample_rate, duration_seconds)
        items.append(
            {
                "name": name,
                "label": label,
                "description": description,
                "source_path": str(path),
                "start_seconds": 0.0,
                "duration_seconds": duration_seconds,
                "provenance": "generated_deterministic_probe",
            }
        )
    return items


def accepted_minus(value: float | None) -> float | None:
    return -value if value is not None else None


def activation_summary(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    summary: list[dict[str, Any]] = []
    for item in items:
        bands: dict[str, Any] = {}
        for band, _low, _high in exciter.EXCITER_BANDS_HZ:
            values = item["bands"][band]
            bands[band] = {
                "source_band_rms_dbfs": values.get("source", {}).get("band_rms_dbfs"),
                "accepted_band_rms_dbfs": values.get("accepted_50", {}).get("band_rms_dbfs"),
                "reduced_band_rms_dbfs": values.get("reduced_35", {}).get("band_rms_dbfs"),
                "bypass_band_rms_dbfs": values.get("bypass_0", {}).get("band_rms_dbfs"),
                "accepted_minus_bypass_rms_db": accepted_minus(values["bypass_minus_accepted_band_rms_db"]),
                "accepted_minus_reduced_rms_db": accepted_minus(values["reduced_minus_accepted_band_rms_db"]),
                "accepted_minus_bypass_side_to_mid_db": accepted_minus(values["bypass_minus_accepted_side_to_mid_db"]),
            }
        summary.append({"name": item["name"], "label": item["label"], "bands": bands})
    return summary


def band_value(
    summary_by_name: dict[str, dict[str, Any]],
    item_name: str,
    band: str,
    metric: str,
) -> float | None:
    item = summary_by_name.get(item_name)
    if item is None:
        return None
    return item["bands"][band].get(metric)


def status_check(name: str, passed: bool, detail: str) -> dict[str, str]:
    return {"name": name, "status": "pass" if passed else "investigate", "detail": detail}


def band_is_below_floor(
    summary_by_name: dict[str, dict[str, Any]],
    item_name: str,
    band: str,
    decision_floor_dbfs: float,
) -> bool:
    accepted = band_value(summary_by_name, item_name, band, "accepted_band_rms_dbfs")
    bypass = band_value(summary_by_name, item_name, band, "bypass_band_rms_dbfs")
    if accepted is None or bypass is None:
        return False
    return max(accepted, bypass) < decision_floor_dbfs


def evaluate_activation(
    summary: list[dict[str, Any]],
    min_air_lift_db: float = DEFAULT_MIN_AIR_LIFT_DB,
    max_dull_air_lift_db: float = DEFAULT_MAX_DULL_AIR_LIFT_DB,
    max_high_level_air_lift_db: float = DEFAULT_MAX_HIGH_LEVEL_AIR_LIFT_DB,
    max_sibilance_presence_lift_db: float = DEFAULT_MAX_SIBILANCE_PRESENCE_LIFT_DB,
    decision_floor_dbfs: float = DEFAULT_DECISION_FLOOR_DBFS,
    depth_order_tolerance_db: float = DEFAULT_DEPTH_ORDER_TOLERANCE_DB,
) -> dict[str, Any]:
    summary_by_name = {item["name"]: item for item in summary}
    checks: list[dict[str, str]] = []

    low_air = band_value(
        summary_by_name,
        "low_level_air_activation",
        "air",
        "accepted_minus_bypass_rms_db",
    )
    low_air_reduced = band_value(
        summary_by_name,
        "low_level_air_activation",
        "air",
        "accepted_minus_reduced_rms_db",
    )
    if low_air is None:
        checks.append(status_check("low_level_air_activation_present", False, "probe result missing"))
    else:
        checks.append(
            status_check(
                "low_level_air_activation_lift",
                low_air >= min_air_lift_db,
                f"accepted-bypass air lift={low_air:.3f} dB; expected >= {min_air_lift_db:.3f} dB",
            )
        )
        if low_air_reduced is None:
            checks.append(status_check("low_level_air_activation_depth_order", False, "reduced fixture result missing"))
        else:
            checks.append(
                status_check(
                    "low_level_air_activation_depth_order",
                    low_air + depth_order_tolerance_db >= low_air_reduced >= -0.05,
                    (
                        f"accepted-bypass air lift={low_air:.3f} dB; "
                        f"accepted-reduced air lift={low_air_reduced:.3f} dB; "
                        f"tolerance={depth_order_tolerance_db:.3f} dB"
                    ),
                )
            )

    dull_air = band_value(
        summary_by_name,
        "low_level_dull_control",
        "air",
        "accepted_minus_bypass_rms_db",
    )
    if dull_air is None:
        checks.append(status_check("low_level_dull_control_present", False, "probe result missing"))
    else:
        dull_floor_only = band_is_below_floor(
            summary_by_name,
            "low_level_dull_control",
            "air",
            decision_floor_dbfs,
        )
        accepted_dull = band_value(summary_by_name, "low_level_dull_control", "air", "accepted_band_rms_dbfs")
        bypass_dull = band_value(summary_by_name, "low_level_dull_control", "air", "bypass_band_rms_dbfs")
        if dull_floor_only:
            checks.append(
                status_check(
                    "low_level_dull_control_restraint",
                    True,
                    (
                        f"accepted-bypass air lift={dull_air:.3f} dB, but accepted={accepted_dull:.3f} dBFS "
                        f"and bypass={bypass_dull:.3f} dBFS are below decision floor {decision_floor_dbfs:.3f} dBFS"
                    ),
                )
            )
        else:
            checks.append(
                status_check(
                    "low_level_dull_control_restraint",
                    abs(dull_air) <= max_dull_air_lift_db,
                    (
                        f"accepted-bypass air lift={dull_air:.3f} dB; expected magnitude <= "
                        f"{max_dull_air_lift_db:.3f} dB above floor {decision_floor_dbfs:.3f} dBFS"
                    ),
                )
            )

    high_air = band_value(
        summary_by_name,
        "high_level_air_control",
        "air",
        "accepted_minus_bypass_rms_db",
    )
    if high_air is None:
        checks.append(status_check("high_level_air_control_present", False, "probe result missing"))
    else:
        checks.append(
            status_check(
                "high_level_air_control_restraint",
                abs(high_air) <= max_high_level_air_lift_db,
                (
                    f"accepted-bypass air lift={high_air:.3f} dB; "
                    f"expected magnitude <= {max_high_level_air_lift_db:.3f} dB"
                ),
            )
        )

    sibilance_presence = band_value(
        summary_by_name,
        "low_level_sibilance_texture",
        "presence_edge",
        "accepted_minus_bypass_rms_db",
    )
    if sibilance_presence is None:
        checks.append(status_check("low_level_sibilance_texture_present", False, "probe result missing"))
    else:
        checks.append(
            status_check(
                "low_level_sibilance_texture_restraint",
                sibilance_presence <= max_sibilance_presence_lift_db,
                (
                    f"accepted-bypass presence-edge lift={sibilance_presence:.3f} dB; "
                    f"expected <= {max_sibilance_presence_lift_db:.3f} dB"
                ),
            )
        )

    status = (
        "measurement_complete_with_investigation"
        if any(check["status"] == "investigate" for check in checks)
        else "measurement_complete"
    )
    return {"status": status, "checks": checks}


def combine_evaluations(integrity: dict[str, Any], activation: dict[str, Any]) -> dict[str, Any]:
    checks = [
        {"category": "integrity", **check}
        for check in integrity["checks"]
    ] + [
        {"category": "activation", **check}
        for check in activation["checks"]
    ]
    status = "fail" if integrity["status"] == "fail" else (
        "measurement_complete_with_investigation"
        if (
            integrity["status"] == "measurement_complete_with_investigation"
            or activation["status"] == "measurement_complete_with_investigation"
        )
        else "measurement_complete"
    )
    return {
        "status": status,
        "integrity_status": integrity["status"],
        "activation_status": activation["status"],
        "checks": checks,
    }


def checks_for_category(report: dict[str, Any], category: str) -> list[dict[str, str]]:
    return [
        check
        for check in report["evaluation"]["checks"]
        if check.get("category") == category
    ]


def markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Axiom Low-Level Exciter Probe Screen",
        "",
        f"Status: **{report['evaluation']['status'].upper()}**",
        "",
        "This generated-probe screen measures the accepted level-dependent air/exciter stage on material designed to exercise it. Only temporary `slider3` fixtures are created; the accepted script is unchanged.",
        "",
        f"Host limiter threshold: `{report['master_limiter_threshold_db']:.2f} dB`; terminal observation ceiling: `{report['ceiling_dbfs']:.2f} dBFS`.",
        "",
        "| Probe | Band | Accepted - bypass RMS (dB) | Accepted - reduced RMS (dB) | Accepted - bypass S/M (dB) |",
        "| --- | --- | ---: | ---: | ---: |",
    ]
    for item in report["activation_summary"]:
        label = item["label"].replace("|", "\\|")
        for band, _low, _high in exciter.EXCITER_BANDS_HZ:
            values = item["bands"][band]
            lines.append(
                f"| {label} | {band} | "
                f"{exciter.display(values['accepted_minus_bypass_rms_db'])} | "
                f"{exciter.display(values['accepted_minus_reduced_rms_db'])} | "
                f"{exciter.display(values['accepted_minus_bypass_side_to_mid_db'])} |"
            )
    lines.extend(
        [
            "",
            "Absolute band RMS context is included so near-silence dB deltas are not overinterpreted.",
            "",
            "| Probe | Band | Source RMS (dBFS) | Accepted RMS (dBFS) | Bypass RMS (dBFS) |",
            "| --- | --- | ---: | ---: | ---: |",
        ]
    )
    for item in report["activation_summary"]:
        label = item["label"].replace("|", "\\|")
        for band, _low, _high in exciter.EXCITER_BANDS_HZ:
            values = item["bands"][band]
            lines.append(
                f"| {label} | {band} | "
                f"{exciter.display(values['source_band_rms_dbfs'])} | "
                f"{exciter.display(values['accepted_band_rms_dbfs'])} | "
                f"{exciter.display(values['bypass_band_rms_dbfs'])} |"
            )
    lines.extend(["", "## Probe Intent", "", "| Probe | Intent |", "| --- | --- |"])
    for item in report["probes"]:
        lines.append(f"| {item['label']} | {item['description']} |")
    lines.extend(["", "## Activation Checks", "", "| Check | Status | Detail |", "| --- | --- | --- |"])
    lines.extend(
        f"| {check['name']} | {check['status'].upper()} | {check['detail']} |"
        for check in checks_for_category(report, "activation")
    )
    lines.extend(["", "## Integrity Checks", "", "| Check | Status | Detail |", "| --- | --- | --- |"])
    lines.extend(
        f"| {check['name']} | {check['status'].upper()} | {check['detail']} |"
        for check in checks_for_category(report, "integrity")
    )
    lines.extend(
        [
            "",
            "Interpretation boundary: this is not a listening candidate. Useful evidence would show the accepted baseline adding measurable air to low-level air-bearing material, little change on dull material, and reduced action on the louder control probe.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("accepted_eel", type=pathlib.Path)
    parser.add_argument("output_dir", type=pathlib.Path)
    parser.add_argument("--pulse-server", default=DEFAULT_PULSE_SERVER)
    parser.add_argument("--route-helper", type=pathlib.Path, default=DEFAULT_ROUTE_HELPER)
    parser.add_argument("--master-limiter-threshold-db", type=float, default=-1.0)
    parser.add_argument("--ceiling-dbfs", type=float, default=-6.0)
    parser.add_argument("--sample-rate", type=int, default=DEFAULT_SAMPLE_RATE)
    parser.add_argument("--duration", type=float, default=DEFAULT_DURATION_SECONDS)
    parser.add_argument("--min-air-lift-db", type=float, default=DEFAULT_MIN_AIR_LIFT_DB)
    parser.add_argument("--max-dull-air-lift-db", type=float, default=DEFAULT_MAX_DULL_AIR_LIFT_DB)
    parser.add_argument("--max-high-level-air-lift-db", type=float, default=DEFAULT_MAX_HIGH_LEVEL_AIR_LIFT_DB)
    parser.add_argument("--decision-floor-dbfs", type=float, default=DEFAULT_DECISION_FLOOR_DBFS)
    parser.add_argument("--depth-order-tolerance-db", type=float, default=DEFAULT_DEPTH_ORDER_TOLERANCE_DB)
    parser.add_argument(
        "--max-sibilance-presence-lift-db",
        type=float,
        default=DEFAULT_MAX_SIBILANCE_PRESENCE_LIFT_DB,
    )
    parser.add_argument("--probe", choices=sorted(PROBES), action="append", dest="probes")
    parser.add_argument("--skip-route-start", action="store_true")
    parser.add_argument("--keep-route-running", action="store_true")
    parser.add_argument("--allow-non-accepted-hash", action="store_true")
    args = parser.parse_args()

    accepted = args.accepted_eel.resolve()
    if not accepted.is_file():
        parser.error(f"EEL script not found: {accepted}")
    accepted_sha256 = sha256_file(accepted)
    if accepted_sha256 != ACCEPTED_BASELINE_SHA256 and not args.allow_non_accepted_hash:
        parser.error(
            f"{accepted} is not the accepted v4.1.4.11 baseline; "
            "pass --allow-non-accepted-hash only for tool development"
        )
    if not -30.0 <= args.master_limiter_threshold_db <= 0.0:
        parser.error("--master-limiter-threshold-db must be in [-30, 0] dB")
    if args.sample_rate < 8000:
        parser.error("--sample-rate must be at least 8000")
    if args.duration < 1.0:
        parser.error("--duration must be at least 1 second")
    selected_probes = tuple(args.probes or PROBES.keys())
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    script_dir = pathlib.Path(__file__).resolve().parent
    probes = generate_probes(output_dir / "probes", selected_probes, args.sample_rate, args.duration)
    fixtures = {"accepted_50": accepted}
    for key, percent, _label in exciter.SETTINGS[1:]:
        fixture = output_dir / "fixtures" / f"{accepted.stem}_exciter_probe_{percent:g}.eel"
        exciter.exciter_fixture(accepted, fixture, percent)
        run([str(script_dir / "validate_axiom_static.sh"), str(fixture)], f"{key} exciter probe fixture static validation")
        fixtures[key] = fixture

    route_started = False
    try:
        if not args.skip_route_start:
            if not args.route_helper.is_file():
                raise QualificationError(f"route helper not found: {args.route_helper}")
            run([str(args.route_helper)], "start managed JamesDSP WSL audio route")
            route_started = True
        validate_route(args.pulse_server)
        reports = []
        for item in probes:
            captures = {}
            for key, _percent, label in exciter.SETTINGS:
                output = output_dir / key / f"{item['name']}.wav"
                run(
                    [
                        sys.executable,
                        str(script_dir / "render_jdsp_host.py"),
                        item["source_path"],
                        str(fixtures[key]),
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
                    f"{item['label']} {label} exciter probe host render",
                )
                captures[key] = output
            reports.append(exciter.analyze_item(item, pathlib.Path(item["source_path"]), captures))
        report = {
            "scope": "generated low-level exciter probes rendered through real JDSP",
            "accepted_eel": str(accepted),
            "accepted_sha256": accepted_sha256,
            "fixtures": {name: str(path) for name, path in fixtures.items()},
            "settings": [exciter.setting_descriptor(*setting) for setting in exciter.SETTINGS],
            "master_limiter_threshold_db": args.master_limiter_threshold_db,
            "ceiling_dbfs": args.ceiling_dbfs,
            "sample_rate_hz": args.sample_rate,
            "duration_seconds": args.duration,
            "bands_hz": exciter.EXCITER_BANDS_HZ,
            "probes": probes,
            "items": reports,
        }
        report["activation_summary"] = activation_summary(reports)
        integrity_evaluation = exciter.evaluate_items(reports, args.ceiling_dbfs)
        activation_evaluation = evaluate_activation(
            report["activation_summary"],
            min_air_lift_db=args.min_air_lift_db,
            max_dull_air_lift_db=args.max_dull_air_lift_db,
            max_high_level_air_lift_db=args.max_high_level_air_lift_db,
            max_sibilance_presence_lift_db=args.max_sibilance_presence_lift_db,
            decision_floor_dbfs=args.decision_floor_dbfs,
            depth_order_tolerance_db=args.depth_order_tolerance_db,
        )
        report["activation_thresholds_db"] = {
            "min_air_lift_db": args.min_air_lift_db,
            "max_dull_air_lift_db": args.max_dull_air_lift_db,
            "max_high_level_air_lift_db": args.max_high_level_air_lift_db,
            "max_sibilance_presence_lift_db": args.max_sibilance_presence_lift_db,
            "decision_floor_dbfs": args.decision_floor_dbfs,
            "depth_order_tolerance_db": args.depth_order_tolerance_db,
        }
        report["evaluation"] = combine_evaluations(integrity_evaluation, activation_evaluation)
        (output_dir / "exciter_probe_screen.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        (output_dir / "exciter_probe_screen.md").write_text(markdown(report), encoding="utf-8")
        print(output_dir / "exciter_probe_screen.json")
        print(output_dir / "exciter_probe_screen.md")
        print(f"status={report['evaluation']['status']}")
        return 1 if report["evaluation"]["status"] == "fail" else 0
    finally:
        if route_started and not args.keep_route_running:
            for error in stop_managed_route(args.pulse_server):
                print(f"warning: {error}", file=sys.stderr)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (exciter.MaterialError, QualificationError, exciter.transfer.AnalysisError) as err:
        print(f"error: {err}", file=sys.stderr)
        raise SystemExit(1)
