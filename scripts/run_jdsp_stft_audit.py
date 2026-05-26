#!/usr/bin/env python3
"""Measure accepted Axiom STFT behavior with same-render diagnostic channel pairing."""

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

from run_jdsp_wsl_qualification import (
    DEFAULT_PULSE_SERVER,
    DEFAULT_ROUTE_HELPER,
    QualificationError,
    read_jdsp_setting,
    run,
    set_jdsp_setting,
    stop_managed_route,
    validate_route,
)


STFT_STAGE_HEADER = """// ==========================================
// LAYER 4: STFT DYNAMIC RESONANCE SUPPRESSOR
// ==========================================
"""
FINAL_STAGE_HEADER = """// ==========================================
// FINAL OUTPUT ASSIGNMENT
// ==========================================
"""
MONO_STIMULUS_NAMES = ("impulse", "bass_burst", "sweep", "correlated_mono")


def stft_fixture(source: pathlib.Path, destination: pathlib.Path, suppression_percent: float) -> None:
    text = source.read_text(encoding="ascii")
    if text.count(STFT_STAGE_HEADER) != 1 or text.count(FINAL_STAGE_HEADER) != 1:
        raise QualificationError(f"cannot make STFT diagnostic fixture from {source}: stage markers are missing")
    if text.count("slider7:50<") != 1 or text.count("slider7 = 50;") != 1:
        raise QualificationError(f"cannot make STFT diagnostic fixture from {source}: control signature is missing")
    value = f"{suppression_percent:g}"
    altered = text.replace("slider7:50<", f"slider7:{value}<", 1).replace("slider7 = 50;", f"slider7 = {value};", 1)
    altered = altered.replace("outputGain = headroomGain;", "outputGain = headroomGain;\nstftDiagnosticDry = 0.0;", 1)
    altered = altered.replace(STFT_STAGE_HEADER, STFT_STAGE_HEADER + "stftDiagnosticDry = out_L;\n", 1)
    altered = altered.replace(
        FINAL_STAGE_HEADER,
        "// Diagnostic fixture only: output pre-STFT mono path on left and STFT path on right.\n"
        "out_L = stftDiagnosticDry;\n\n"
        + FINAL_STAGE_HEADER,
        1,
    )
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(altered, encoding="ascii")


def split_capture_channels(source: pathlib.Path, dry_output: pathlib.Path, processed_output: pathlib.Path) -> None:
    with wave.open(str(source), "rb") as input_wav:
        if input_wav.getnchannels() != 2 or input_wav.getsampwidth() != 2:
            raise QualificationError(f"STFT diagnostic capture must be stereo 16-bit PCM: {source}")
        sample_rate = input_wav.getframerate()
        frames = input_wav.getnframes()
        raw = input_wav.readframes(frames)
    dry = bytearray()
    processed = bytearray()
    for left, right in struct.iter_unpack("<hh", raw):
        dry.extend(struct.pack("<hh", left, left))
        processed.extend(struct.pack("<hh", right, right))
    for destination, payload in ((dry_output, dry), (processed_output, processed)):
        destination.parent.mkdir(parents=True, exist_ok=True)
        with wave.open(str(destination), "wb") as output_wav:
            output_wav.setnchannels(2)
            output_wav.setsampwidth(2)
            output_wav.setframerate(sample_rate)
            output_wav.writeframes(payload)


def read_mono_samples(source: pathlib.Path) -> tuple[int, list[float]]:
    with wave.open(str(source), "rb") as input_wav:
        if input_wav.getnchannels() != 2 or input_wav.getsampwidth() != 2:
            raise QualificationError(f"STFT diagnostic split must be stereo 16-bit PCM: {source}")
        sample_rate = input_wav.getframerate()
        raw = input_wav.readframes(input_wav.getnframes())
    return sample_rate, [left / 32768.0 for left, _right in struct.iter_unpack("<hh", raw)]


def db_ratio(numerator: float, denominator: float) -> float | None:
    return 20.0 * math.log10(numerator / denominator) if numerator > 0.0 and denominator > 0.0 else None


def energy_span_ms(samples: list[float], sample_rate: int, low_fraction: float = 0.05, high_fraction: float = 0.95) -> float | None:
    energies = [value * value for value in samples]
    total = sum(energies)
    if total <= 0.0:
        return None
    low_target = total * low_fraction
    high_target = total * high_fraction
    cumulative = 0.0
    low_index = 0
    high_index = len(samples) - 1
    for index, energy in enumerate(energies):
        cumulative += energy
        if cumulative >= low_target:
            low_index = index
            break
    cumulative = 0.0
    for index, energy in enumerate(energies):
        cumulative += energy
        if cumulative >= high_target:
            high_index = index
            break
    return (high_index - low_index) * 1000.0 / sample_rate


def centered_energy_fraction(samples: list[float], peak_index: int, sample_rate: int, radius_ms: float) -> float | None:
    energies = [value * value for value in samples]
    total = sum(energies)
    if total <= 0.0:
        return None
    radius = int(round(radius_ms * sample_rate / 1000.0))
    start = max(0, peak_index - radius)
    end = min(len(samples), peak_index + radius + 1)
    return sum(energies[start:end]) / total


def transient_metrics(dry_path: pathlib.Path, processed_path: pathlib.Path) -> dict[str, Any]:
    sample_rate, dry = read_mono_samples(dry_path)
    processed_rate, processed = read_mono_samples(processed_path)
    if processed_rate != sample_rate or len(processed) != len(dry):
        raise QualificationError("STFT diagnostic transient paths must share sample rate and frame count")
    dry_peak_index = max(range(len(dry)), key=lambda index: abs(dry[index]))
    processed_peak_index = max(range(len(processed)), key=lambda index: abs(processed[index]))
    dry_peak = abs(dry[dry_peak_index])
    processed_peak = abs(processed[processed_peak_index])
    dry_span = energy_span_ms(dry, sample_rate)
    processed_span = energy_span_ms(processed, sample_rate)
    return {
        "sample_rate_hz": sample_rate,
        "dry_peak_frame": dry_peak_index,
        "processed_peak_frame": processed_peak_index,
        "peak_arrival_delta_frames": processed_peak_index - dry_peak_index,
        "peak_arrival_delta_ms": (processed_peak_index - dry_peak_index) * 1000.0 / sample_rate,
        "processed_peak_relative_to_dry_db": db_ratio(processed_peak, dry_peak),
        "dry_energy_span_5_to_95_ms": dry_span,
        "processed_energy_span_5_to_95_ms": processed_span,
        "energy_span_delta_ms": None if dry_span is None or processed_span is None else processed_span - dry_span,
        "dry_energy_within_1ms_of_peak": centered_energy_fraction(dry, dry_peak_index, sample_rate, 1.0),
        "processed_energy_within_1ms_of_peak": centered_energy_fraction(processed, processed_peak_index, sample_rate, 1.0),
        "dry_energy_within_5ms_of_peak": centered_energy_fraction(dry, dry_peak_index, sample_rate, 5.0),
        "processed_energy_within_5ms_of_peak": centered_energy_fraction(processed, processed_peak_index, sample_rate, 5.0),
    }


def load_json(path: pathlib.Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="ascii"))


def run_mode(
    script_dir: pathlib.Path,
    fixture: pathlib.Path,
    stimuli_dir: pathlib.Path,
    destination: pathlib.Path,
    pulse_server: str,
    limiter_threshold_db: float,
    transient_repetitions: int,
) -> dict[str, Any]:
    reports: dict[str, dict[str, Any]] = {}
    for stimulus in MONO_STIMULUS_NAMES:
        capture = destination / "capture" / f"{stimulus}.wav"
        dry = destination / "split" / f"{stimulus}_pre_stft.wav"
        processed = destination / "split" / f"{stimulus}_stft.wav"
        compare_json = destination / "comparison" / f"{stimulus}.json"
        compare_md = destination / "comparison" / f"{stimulus}.md"
        run(
            [
                sys.executable,
                str(script_dir / "render_jdsp_host.py"),
                str(stimuli_dir / f"{stimulus}.wav"),
                str(fixture),
                str(capture),
                "--pulse-server",
                pulse_server,
                "--pre-roll-ms",
                "500",
                "--tail-ms",
                "2000",
                "--master-limiter-threshold-db",
                str(limiter_threshold_db),
            ],
            f"STFT {destination.name} {stimulus} host render",
        )
        split_capture_channels(capture, dry, processed)
        run(
            [
                sys.executable,
                str(script_dir / "compare_jdsp_captures.py"),
                str(dry),
                str(processed),
                "--json",
                str(compare_json),
                "--markdown",
                str(compare_md),
                "--max-lag-ms",
                "100",
            ],
            f"STFT {destination.name} {stimulus} same-render comparison",
        )
        reports[stimulus] = load_json(compare_json)
        if stimulus == "impulse":
            reports[stimulus]["transient_metrics"] = transient_metrics(dry, processed)
    impulse_repetitions = [reports["impulse"]["transient_metrics"]]
    for repetition in range(2, transient_repetitions + 1):
        capture = destination / "impulse_repetitions" / f"repeat_{repetition}" / "capture.wav"
        dry = destination / "impulse_repetitions" / f"repeat_{repetition}" / "pre_stft.wav"
        processed = destination / "impulse_repetitions" / f"repeat_{repetition}" / "stft.wav"
        run(
            [
                sys.executable,
                str(script_dir / "render_jdsp_host.py"),
                str(stimuli_dir / "impulse.wav"),
                str(fixture),
                str(capture),
                "--pulse-server",
                pulse_server,
                "--pre-roll-ms",
                "500",
                "--tail-ms",
                "2000",
                "--master-limiter-threshold-db",
                str(limiter_threshold_db),
            ],
            f"STFT {destination.name} impulse repetition {repetition} host render",
        )
        split_capture_channels(capture, dry, processed)
        impulse_repetitions.append(transient_metrics(dry, processed))
    reports["impulse"]["transient_repetitions"] = impulse_repetitions
    return reports


def evaluate_modes(modes: dict[str, dict[str, Any]]) -> list[dict[str, str]]:
    checks: list[dict[str, str]] = []
    for mode_name, reports in modes.items():
        for stimulus in MONO_STIMULUS_NAMES:
            captures = reports[stimulus]["captures"]
            failed = any(
                captures[label]["channels"]["combined"]["silent"]
                or captures[label]["channels"]["combined"]["clipped_samples"] > 0
                for label in ("reference", "candidate")
            )
            checks.append(
                {
                    "name": f"{mode_name}_{stimulus}_integrity",
                    "status": "fail" if failed else "pass",
                    "detail": (
                        f"dry silent={captures['reference']['channels']['combined']['silent']}, "
                        f"STFT silent={captures['candidate']['channels']['combined']['silent']}, "
                        f"dry clipping={captures['reference']['channels']['combined']['clipped_samples']}, "
                        f"STFT clipping={captures['candidate']['channels']['combined']['clipped_samples']}"
                    ),
                }
            )
    return checks


def report_status(checks: list[dict[str, str]]) -> str:
    return "fail" if any(check["status"] == "fail" for check in checks) else "measurement_complete"


def metric(value: float | None, places: int = 3) -> str:
    return "-inf" if value is None else f"{value:.{places}f}"


def markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Axiom STFT Stage Audit",
        "",
        f"Status: **{report['status'].upper()}**",
        "",
        "This is diagnostic host-path evidence. Each temporary EEL fixture sends its pre-STFT mono path to the left output channel and its STFT result to the right output channel in the same render. The accepted source script is unchanged.",
        "",
        "- `unity_round_trip`: STFT analysis/resynthesis with suppression fixed at `0%`.",
        "- `accepted_suppression`: STFT analysis/resynthesis with accepted suppression fixed at `50%`.",
        "",
    ]
    for mode, label in (
        ("unity_round_trip", "Same-render pre-STFT -> STFT unity round trip"),
        ("accepted_suppression", "Same-render pre-STFT -> accepted STFT suppression"),
    ):
        lines.extend(
            [
                f"## {label}",
                "",
                "| Stimulus | STFT delay (ms) | Correlation | RMS residual (dBFS) | Signal / residual (dB) | STFT peak (dBFS) | STFT clipped |",
                "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
            ]
        )
        for stimulus in MONO_STIMULUS_NAMES:
            item = report["modes"][mode][stimulus]
            comparison = item["comparison"]
            candidate = item["captures"]["candidate"]["channels"]["combined"]
            lines.append(
                f"| {stimulus} | {comparison['alignment']['candidate_delay_ms']:.6f} | "
                f"{comparison['alignment']['normalized_correlation']:.9f} | "
                f"{metric(comparison['difference']['rms_difference_dbfs'])} | "
                f"{metric(comparison['difference']['signal_to_difference_db'])} | "
                f"{metric(candidate['peak_dbfs'])} | {candidate['clipped_samples']} |"
            )
        lines.append("")
        transient = report["modes"][mode]["impulse"]["transient_metrics"]
        lines.extend(
            [
                "Impulse temporal-energy metrics:",
                "",
                "| Metric | Value |",
                "| --- | ---: |",
                f"| Peak arrival delta (ms) | {transient['peak_arrival_delta_ms']:.6f} |",
                f"| Processed peak relative to pre-STFT peak (dB) | {metric(transient['processed_peak_relative_to_dry_db'])} |",
                f"| Pre-STFT energy span, 5-95% (ms) | {metric(transient['dry_energy_span_5_to_95_ms'], 6)} |",
                f"| STFT energy span, 5-95% (ms) | {metric(transient['processed_energy_span_5_to_95_ms'], 6)} |",
                f"| Energy span delta (ms) | {metric(transient['energy_span_delta_ms'], 6)} |",
                f"| Pre-STFT energy within +/-1 ms of peak | {transient['dry_energy_within_1ms_of_peak']:.6f} |",
                f"| STFT energy within +/-1 ms of peak | {transient['processed_energy_within_1ms_of_peak']:.6f} |",
                f"| Pre-STFT energy within +/-5 ms of peak | {transient['dry_energy_within_5ms_of_peak']:.6f} |",
                f"| STFT energy within +/-5 ms of peak | {transient['processed_energy_within_5ms_of_peak']:.6f} |",
                "",
            ]
        )
        lines.extend(
            [
                "Repeated impulse temporal metrics:",
                "",
                "| Repetition | Peak arrival delta (ms) | Processed peak vs pre-STFT (dB) | Energy span delta (ms) | STFT energy within +/-1 ms | STFT energy within +/-5 ms |",
                "| ---: | ---: | ---: | ---: | ---: | ---: |",
            ]
        )
        for repetition, result in enumerate(report["modes"][mode]["impulse"]["transient_repetitions"], start=1):
            lines.append(
                f"| {repetition} | {result['peak_arrival_delta_ms']:.6f} | "
                f"{metric(result['processed_peak_relative_to_dry_db'])} | "
                f"{metric(result['energy_span_delta_ms'], 6)} | "
                f"{result['processed_energy_within_1ms_of_peak']:.6f} | "
                f"{result['processed_energy_within_5ms_of_peak']:.6f} |"
            )
        lines.append("")
    lines.extend(["## Integrity Checks", "", "| Check | Status | Detail |", "| --- | --- | --- |"])
    lines.extend(f"| {check['name']} | {check['status'].upper()} | {check['detail']} |" for check in report["checks"])
    lines.extend(
        [
            "",
            "Interpretation boundary: this diagnostic uses mono probes because the two output channels carry different audit paths. It characterizes the JDSP-hosted stage behavior under each fixture; it does not by itself justify a production change.",
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
    parser.add_argument("--transient-repetitions", type=int, default=3)
    parser.add_argument("--skip-route-start", action="store_true")
    parser.add_argument("--keep-route-running", action="store_true")
    args = parser.parse_args()

    accepted = args.accepted_eel.resolve()
    output_dir = args.output_dir.resolve()
    script_dir = pathlib.Path(__file__).resolve().parent
    if not accepted.is_file():
        parser.error(f"EEL script not found: {accepted}")
    if args.transient_repetitions < 1:
        parser.error("--transient-repetitions must be at least 1")
    output_dir.mkdir(parents=True, exist_ok=True)
    unity = output_dir / "fixtures" / f"{accepted.stem}_stft_unity_same_render.eel"
    active = output_dir / "fixtures" / f"{accepted.stem}_stft_accepted_same_render.eel"
    stft_fixture(accepted, unity, 0.0)
    stft_fixture(accepted, active, 50.0)
    run(
        [sys.executable, str(script_dir / "generate_jdsp_stimuli.py"), str(output_dir / "stimuli")],
        "STFT audit stimulus generation",
    )

    route_started = False
    restored_master_threshold: str | None = None
    try:
        if not args.skip_route_start:
            if not args.route_helper.is_file():
                raise QualificationError(f"route helper not found: {args.route_helper}")
            run([str(args.route_helper)], "start managed JamesDSP WSL audio route")
            route_started = True
        validate_route(args.pulse_server)
        restored_master_threshold = read_jdsp_setting("master_limthreshold")
        set_jdsp_setting("master_limthreshold", f"{args.master_limiter_threshold_db:g}")
        modes = {
            "unity_round_trip": run_mode(
                script_dir, unity, output_dir / "stimuli", output_dir / "unity_round_trip",
                args.pulse_server, args.master_limiter_threshold_db, args.transient_repetitions,
            ),
            "accepted_suppression": run_mode(
                script_dir, active, output_dir / "stimuli", output_dir / "accepted_suppression",
                args.pulse_server, args.master_limiter_threshold_db, args.transient_repetitions,
            ),
        }
        checks = evaluate_modes(modes)
        report = {
            "generated_at": dt.datetime.now(tz=dt.timezone.utc).isoformat(),
            "status": report_status(checks),
            "scope": "same-render pre-STFT versus post-STFT diagnostic channel pairing through JDSP",
            "accepted_eel": str(accepted),
            "fixtures": {"stft_unity": str(unity), "accepted_suppression": str(active)},
            "master_limiter_threshold_db": args.master_limiter_threshold_db,
            "transient_repetitions": args.transient_repetitions,
            "modes": modes,
            "checks": checks,
        }
        (output_dir / "stft_audit.json").write_text(json.dumps(report, indent=2) + "\n", encoding="ascii")
        (output_dir / "stft_audit.md").write_text(markdown(report), encoding="ascii")
        print(output_dir / "stft_audit.json")
        print(output_dir / "stft_audit.md")
        return 1 if report["status"] == "fail" else 0
    finally:
        if restored_master_threshold is not None:
            try:
                set_jdsp_setting("master_limthreshold", restored_master_threshold)
            except QualificationError as exc:
                print(f"warning: {exc}", file=sys.stderr)
        if route_started and not args.keep_route_running:
            for error in stop_managed_route(args.pulse_server):
                print(f"warning: {error}", file=sys.stderr)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except QualificationError as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1)
