#!/usr/bin/env python3
"""Measure accepted Axiom width behavior and mono compatibility through real JDSP."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import pathlib
import struct
import sys
import wave
from typing import Any

import analyze_jdsp_transfer as transfer
from run_jdsp_wsl_qualification import (
    DEFAULT_PULSE_SERVER,
    DEFAULT_ROUTE_HELPER,
    QualificationError,
    run,
    stop_managed_route,
    validate_route,
)


FREQUENCIES_HZ = (63.0, 90.0, 250.0, 1000.0, 2400.0, 6000.0, 10000.0, 16000.0)
WIDTH_DEFAULTS = (
    ("slider2:135<", "slider2:100<", "slider2 = 135;", "slider2 = 100;"),
    ("slider5:140<", "slider5:100<", "slider5 = 140;", "slider5 = 100;"),
    ("slider6:110<", "slider6:100<", "slider6 = 110;", "slider6 = 100;"),
)
PROBES = ("pure_mid", "pure_side")
SAMPLE_RATE = 48000
DURATION_SECONDS = 2.0
PRE_ROLL_MS = 500
TAIL_MS = 2000
TONE_AMPLITUDE = 0.025
LEAKAGE_OBSERVATION_DB = -70.0
LINEAR_REFERENCE_GAIN_DB = -1.0


def unity_width_fixture(source: pathlib.Path, destination: pathlib.Path) -> None:
    text = source.read_text(encoding="ascii")
    for slider, replacement, initializer, init_replacement in WIDTH_DEFAULTS:
        if text.count(slider) != 1 or text.count(initializer) != 1:
            raise QualificationError(
                f"cannot make width diagnostic fixture from {source}: missing control signature {slider}"
            )
        text = text.replace(slider, replacement, 1).replace(initializer, init_replacement, 1)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="ascii")


def pcm16(value: float) -> int:
    return int(round(max(-1.0, min(1.0, value)) * 32767))


def write_probe(destination: pathlib.Path, component: str) -> None:
    if component not in PROBES:
        raise QualificationError(f"unknown width audit component: {component}")
    frames = int(round(SAMPLE_RATE * DURATION_SECONDS))
    fade_frames = int(round(SAMPLE_RATE * 0.05))
    phases = (0.0, 0.63, 1.31, 2.02, 2.87, 3.52, 4.34, 5.18)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(destination), "wb") as output:
        output.setnchannels(2)
        output.setsampwidth(2)
        output.setframerate(SAMPLE_RATE)
        payload = bytearray()
        for frame in range(frames):
            time_s = frame / SAMPLE_RATE
            fade = min(1.0, frame / fade_frames, (frames - frame - 1) / fade_frames)
            value = fade * TONE_AMPLITUDE * sum(
                math.sin(2.0 * math.pi * frequency * time_s + phase)
                for frequency, phase in zip(FREQUENCIES_HZ, phases)
            )
            left, right = (value, value) if component == "pure_mid" else (value, -value)
            payload.extend(struct.pack("<hh", pcm16(left), pcm16(right)))
        output.writeframes(payload)


def output_levels(report: dict[str, Any]) -> dict[str, Any]:
    return report["measurement_level"]["post_jdsp_processed_output"]


def path_points(report: dict[str, Any], path_name: str) -> dict[float, dict[str, Any]]:
    return {
        round(point["requested_frequency_hz"], 6): point
        for point in report["mid_side_transfer_matrix"][path_name]["points"]
        if point["valid"]
    }


def magnitude(report: dict[str, Any], path_name: str, frequency: float) -> float | None:
    point = path_points(report, path_name).get(round(frequency, 6))
    return None if point is None else point["magnitude_db"]


def level_text(value: float | None, places: int = 3) -> str:
    return "-inf" if value is None else f"{value:.{places}f}"


def leakage_status(value: float | None, threshold_db: float) -> str:
    return "pass" if value is None or value <= threshold_db else "investigate"


def evaluate_modes(modes: dict[str, dict[str, dict[str, Any]]], leakage_db: float) -> dict[str, Any]:
    checks: list[dict[str, str]] = []
    for mode_name, reports in modes.items():
        for probe_name, report in reports.items():
            levels = output_levels(report)
            if levels["clipped_samples"] > 0:
                status = "fail"
                detail = f"{levels['clipped_samples']} clipped channel samples"
            elif levels["peak_dbfs"] is None:
                status = "fail"
                detail = "processed output is silent"
            elif not report["qualification"]["qualified"]:
                status = "investigate"
                detail = "; ".join(report["qualification"]["reasons"])
            else:
                status = "pass"
                detail = f"output peak={levels['peak_dbfs']:.3f} dBFS with no clipped samples"
            checks.append({"name": f"{mode_name}_{probe_name}_integrity", "status": status, "detail": detail})

        for frequency in FREQUENCIES_HZ:
            mono_to_side = magnitude(reports["pure_mid"], "M_to_S", frequency)
            side_to_mono = magnitude(reports["pure_side"], "S_to_M", frequency)
            for name, value in (("mid_to_side", mono_to_side), ("side_to_mid", side_to_mono)):
                checks.append(
                    {
                        "name": f"{mode_name}_{name}_{frequency:g}hz",
                        "status": leakage_status(value, leakage_db),
                        "detail": (
                            f"{name.replace('_', ' ')} transfer={level_text(value)} dB; "
                            f"observation boundary <= {leakage_db:.1f} dB"
                        ),
                    }
                )

    status = "fail" if any(check["status"] == "fail" for check in checks) else (
        "measurement_complete_with_investigation"
        if any(check["status"] == "investigate" for check in checks)
        else "measurement_complete"
    )
    return {"status": status, "checks": checks}


def width_map(modes: dict[str, dict[str, dict[str, Any]]]) -> list[dict[str, Any]]:
    mapped = []
    for frequency in FREQUENCIES_HZ:
        accepted = magnitude(modes["accepted_width"]["pure_side"], "S_to_S", frequency)
        unity = magnitude(modes["unity_width"]["pure_side"], "S_to_S", frequency)
        mapped.append(
            {
                "frequency_hz": frequency,
                "accepted_side_to_side_db": accepted,
                "unity_side_to_side_db": unity,
                "accepted_minus_unity_db": None if accepted is None or unity is None else accepted - unity,
            }
        )
    return mapped


def mono_map(modes: dict[str, dict[str, dict[str, Any]]]) -> list[dict[str, Any]]:
    mapped = []
    for frequency in FREQUENCIES_HZ:
        accepted = magnitude(modes["accepted_width"]["pure_mid"], "M_to_M", frequency)
        unity = magnitude(modes["unity_width"]["pure_mid"], "M_to_M", frequency)
        mapped.append(
            {
                "frequency_hz": frequency,
                "accepted_mid_to_mid_db": accepted,
                "unity_mid_to_mid_db": unity,
                "accepted_minus_unity_db": None if accepted is None or unity is None else accepted - unity,
            }
        )
    return mapped


def render_mode(
    script_dir: pathlib.Path,
    eel: pathlib.Path,
    stimuli: pathlib.Path,
    destination: pathlib.Path,
    pulse_server: str,
    threshold_db: float,
) -> dict[str, dict[str, Any]]:
    reports: dict[str, dict[str, Any]] = {}
    for probe in PROBES:
        output = destination / "capture" / f"{probe}.wav"
        json_path = destination / "transfer" / f"{probe}.json"
        markdown_path = destination / "transfer" / f"{probe}.md"
        run(
            [
                sys.executable,
                str(script_dir / "render_jdsp_host.py"),
                str(stimuli / f"{probe}.wav"),
                str(eel),
                str(output),
                "--pulse-server",
                pulse_server,
                "--pre-roll-ms",
                str(PRE_ROLL_MS),
                "--tail-ms",
                str(TAIL_MS),
                "--master-limiter-threshold-db",
                str(threshold_db),
            ],
            f"width/mono {destination.name} {probe} host render",
        )
        report = transfer.create_report(
            transfer.read_stereo_wav(stimuli / f"{probe}.wav"),
            transfer.read_stereo_wav(output),
            label=f"{destination.name}-{probe}",
            capture_pre_roll_ms=PRE_ROLL_MS,
            frequencies_hz=FREQUENCIES_HZ,
        )
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="ascii")
        markdown_path.write_text(transfer.markdown_report(report), encoding="ascii")
        reports[probe] = report
    return reports


def markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Axiom Width and Mono Compatibility Audit",
        "",
        f"Status: **{report['evaluation']['status'].upper()}**",
        "",
        "This measurement renders low-level pure-mid and pure-side multitone probes through real JDSP. "
        "The accepted source EEL is unchanged; `unity_width` is a temporary diagnostic fixture whose "
        "three width controls are fixed to `100%`.",
        "",
        "## Width Control Map",
        "",
        "| Frequency (Hz) | Unity S->S (dB) | Accepted S->S (dB) | Accepted - unity (dB) |",
        "| ---: | ---: | ---: | ---: |",
    ]
    for point in report["width_map"]:
        lines.append(
            f"| {point['frequency_hz']:.0f} | {level_text(point['unity_side_to_side_db'])} | "
            f"{level_text(point['accepted_side_to_side_db'])} | "
            f"{level_text(point['accepted_minus_unity_db'])} |"
        )
    lines.extend(
        [
            "",
            "The low-frequency rows measure crossover-transition behavior, not a brick-wall bass fold. "
            "Residual side energy from the high-pass branches can still be widened below the nominal "
            "`150 Hz` split.",
            "",
            "## Pure-Mid Render Control",
            "",
            "| Frequency (Hz) | Unity M->M (dB) | Accepted M->M (dB) | Accepted - unity (dB) |",
            "| ---: | ---: | ---: | ---: |",
        ]
    )
    for point in report["mono_map"]:
        lines.append(
            f"| {point['frequency_hz']:.0f} | {level_text(point['unity_mid_to_mid_db'])} | "
            f"{level_text(point['accepted_mid_to_mid_db'])} | "
            f"{level_text(point['accepted_minus_unity_db'])} |"
        )
    lines.extend(
        [
            "",
            "Width controls have no mathematical effect on a pure-mid input. Any non-zero difference in "
            "the table above is separate-render host/dynamic-stage variance and is not attributed to "
            "width processing; center preservation is assessed through the `M->S` leakage checks below.",
            "",
            "## Integrity and Leakage Checks",
            "",
            f"Leakage observation boundary: `{report['leakage_observation_db']:.1f} dB`. "
            "A leakage observation requests engineering review; only silence or clipping fails this diagnostic.",
            "",
            "| Check | Status | Detail |",
            "| --- | --- | --- |",
        ]
    )
    lines.extend(
        f"| {check['name']} | {check['status'].upper()} | {check['detail']} |"
        for check in report["evaluation"]["checks"]
    )
    lines.extend(
        [
            "",
            "Interpretation boundary: pure-side material is designed to cancel under mono summation. "
            "The S->M measurement tests unintended center leakage; it does not treat intentional side-only "
            "collapse as a defect. Transfer values are stimulus-conditioned host-path measurements.",
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
    parser.add_argument("--leakage-observation-db", type=float, default=LEAKAGE_OBSERVATION_DB)
    parser.add_argument("--skip-route-start", action="store_true")
    parser.add_argument("--keep-route-running", action="store_true")
    args = parser.parse_args()

    accepted = args.accepted_eel.resolve()
    output_dir = args.output_dir.resolve()
    if not accepted.is_file():
        parser.error(f"EEL script not found: {accepted}")
    if args.leakage_observation_db >= 0.0:
        parser.error("--leakage-observation-db must be negative")
    output_dir.mkdir(parents=True, exist_ok=True)
    fixture = output_dir / "fixtures" / f"{accepted.stem}_unity_width.eel"
    unity_width_fixture(accepted, fixture)
    stimuli = output_dir / "stimuli"
    for probe in PROBES:
        write_probe(stimuli / f"{probe}.wav", probe)

    route_started = False
    try:
        if not args.skip_route_start:
            if not args.route_helper.is_file():
                raise QualificationError(f"route helper not found: {args.route_helper}")
            run([str(args.route_helper)], "start managed JamesDSP WSL audio route")
            route_started = True
        validate_route(args.pulse_server)
        script_dir = pathlib.Path(__file__).resolve().parent
        modes = {
            "unity_width": render_mode(
                script_dir, fixture, stimuli, output_dir / "unity_width",
                args.pulse_server, args.master_limiter_threshold_db,
            ),
            "accepted_width": render_mode(
                script_dir, accepted, stimuli, output_dir / "accepted_width",
                args.pulse_server, args.master_limiter_threshold_db,
            ),
        }
        report = {
            "generated_at": dt.datetime.now(tz=dt.timezone.utc).isoformat(),
            "scope": "accepted width controls and mono compatibility through real JDSP",
            "accepted_eel": str(accepted),
            "fixtures": {"unity_width": str(fixture)},
            "master_limiter_threshold_db": args.master_limiter_threshold_db,
            "frequencies_hz": FREQUENCIES_HZ,
            "leakage_observation_db": args.leakage_observation_db,
            "modes": modes,
        }
        report["width_map"] = width_map(modes)
        report["mono_map"] = mono_map(modes)
        report["evaluation"] = evaluate_modes(modes, args.leakage_observation_db)
        (output_dir / "width_mono_audit.json").write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="ascii"
        )
        (output_dir / "width_mono_audit.md").write_text(markdown(report), encoding="ascii")
        print(output_dir / "width_mono_audit.json")
        print(output_dir / "width_mono_audit.md")
        print(f"status={report['evaluation']['status']}")
        return 1 if report["evaluation"]["status"] == "fail" else 0
    finally:
        if route_started and not args.keep_route_running:
            for error in stop_managed_route(args.pulse_server):
                print(f"warning: {error}", file=sys.stderr)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (QualificationError, transfer.AnalysisError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1)
