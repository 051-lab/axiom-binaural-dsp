#!/usr/bin/env python3
"""Characterize Axiom v4.1.4.7's nonlinear sub-harmonic injection branch."""

from __future__ import annotations

import argparse
import cmath
import json
import math
from dataclasses import dataclass
from pathlib import Path


SAMPLE_RATE = 48000
Q = 0.7071
DRIVE = 3.5
HEADROOM_DB = -1.0
DB_2_LOG = math.log(10.0) / 20.0
DEFAULT_FREQUENCIES_HZ = (30.0, 45.0, 60.0, 70.0, 90.0)
DEFAULT_SLIDER_DB = (-12.0, 0.0, 4.0, 6.0, 8.0, 12.0)
DEFAULT_INPUT_AMPLITUDES = (0.20, 0.35, 0.50, 0.65)
WARMUP_SECONDS = 0.5
MEASURE_SECONDS = 1.0


def db(value: float) -> float | None:
    return 20.0 * math.log10(value) if value > 0.0 else None


def db_text(value: float | None) -> str:
    return "-inf" if value is None else f"{value:.3f}"


@dataclass
class Biquad:
    b0: float
    b1: float
    b2: float
    a1: float
    a2: float
    x1: float = 0.0
    x2: float = 0.0
    y1: float = 0.0
    y2: float = 0.0

    def process(self, sample: float) -> float:
        output = (
            sample * self.b0
            + self.x1 * self.b1
            + self.x2 * self.b2
            + self.y1 * self.a1
            + self.y2 * self.a2
        )
        self.y2 = self.y1
        self.y1 = output
        self.x2 = self.x1
        self.x1 = sample
        return output


def biquad(kind: str, frequency: float, sample_rate: int) -> Biquad:
    safe_frequency = min(max(frequency, 5.0), sample_rate * 0.45)
    angle = safe_frequency * 2.0 * math.pi / sample_rate
    sin_angle = math.sin(angle)
    cos_angle = math.cos(angle)
    alpha = sin_angle / (Q * 2.0)
    a0 = 1.0 + alpha
    raw_a1 = -2.0 * cos_angle
    raw_a2 = 1.0 - alpha
    if kind == "lowpass":
        raw_b0 = (1.0 - cos_angle) * 0.5
        raw_b1 = 1.0 - cos_angle
        raw_b2 = (1.0 - cos_angle) * 0.5
    elif kind == "highpass":
        raw_b0 = (1.0 + cos_angle) * 0.5
        raw_b1 = -(1.0 + cos_angle)
        raw_b2 = (1.0 + cos_angle) * 0.5
    else:
        raise ValueError(kind)
    return Biquad(
        raw_b0 / a0,
        raw_b1 / a0,
        raw_b2 / a0,
        -raw_a1 / a0,
        -raw_a2 / a0,
    )


def rms(samples: list[float]) -> float:
    return math.sqrt(sum(sample * sample for sample in samples) / len(samples))


def peak(samples: list[float]) -> float:
    return max(abs(sample) for sample in samples)


def component_amplitude(samples: list[float], frequency_hz: float, sample_rate: int) -> float:
    accumulator = 0j
    length = len(samples)
    for index, sample in enumerate(samples):
        accumulator += sample * cmath.exp(-2j * math.pi * frequency_hz * index / sample_rate)
    return abs(accumulator) * 2.0 / length


def render_probe(
    frequency_hz: float,
    slider_db: float,
    input_amplitude: float = 0.35,
    sample_rate: int = SAMPLE_RATE,
    reserve_above_slider_db: float | None = None,
) -> dict:
    lowpass_1 = biquad("lowpass", 90.0, sample_rate)
    lowpass_2 = biquad("lowpass", 90.0, sample_rate)
    highpass_1 = biquad("highpass", 90.0, sample_rate)
    highpass_2 = biquad("highpass", 90.0, sample_rate)
    slider_gain = math.exp(slider_db * DB_2_LOG)
    conditional_reserve_db = (
        max(0.0, slider_db - reserve_above_slider_db)
        if reserve_above_slider_db is not None
        else 0.0
    )
    final_reserve_db = HEADROOM_DB - conditional_reserve_db
    headroom_gain = math.exp(final_reserve_db * DB_2_LOG)
    warmup_frames = round(WARMUP_SECONDS * sample_rate)
    measurement_frames = round(MEASURE_SECONDS * sample_rate)
    dry: list[float] = []
    injection: list[float] = []
    branch_output: list[float] = []
    final_output: list[float] = []
    for frame in range(warmup_frames + measurement_frames):
        sample = input_amplitude * math.sin(2.0 * math.pi * frequency_hz * frame / sample_rate)
        sub = lowpass_2.process(lowpass_1.process(sample))
        saturated = (sub * DRIVE) / (1.0 + abs(sub * DRIVE))
        harmonic = highpass_2.process(highpass_1.process(saturated))
        added = harmonic * slider_gain
        if frame >= warmup_frames:
            dry.append(sample)
            injection.append(added)
            branch_output.append(sample + added)
            final_output.append((sample + added) * headroom_gain)
    third_harmonic = component_amplitude(injection, frequency_hz * 3.0, sample_rate)
    fifth_harmonic = component_amplitude(injection, frequency_hz * 5.0, sample_rate)
    dry_rms = rms(dry)
    injection_rms = rms(injection)
    return {
        "frequency_hz": frequency_hz,
        "slider_db": slider_db,
        "input_amplitude": input_amplitude,
        "slider_linear_gain": slider_gain,
        "conditional_bass_reserve_db": conditional_reserve_db,
        "total_terminal_reserve_db": final_reserve_db,
        "dry_rms_dbfs": db(dry_rms),
        "injection_rms_dbfs": db(injection_rms),
        "injection_relative_to_dry_db": db(injection_rms / dry_rms),
        "third_harmonic_dbfs": db(third_harmonic),
        "fifth_harmonic_dbfs": db(fifth_harmonic),
        "branch_peak_dbfs_before_downstream_processing": db(peak(branch_output)),
        "terminal_headroom_applied_peak_dbfs_before_downstream_processing": db(peak(final_output)),
    }


def create_report(
    frequencies_hz: tuple[float, ...] = DEFAULT_FREQUENCIES_HZ,
    slider_db_values: tuple[float, ...] = DEFAULT_SLIDER_DB,
    input_amplitudes: tuple[float, ...] = DEFAULT_INPUT_AMPLITUDES,
    reserve_above_slider_db: float | None = None,
) -> dict:
    probes = [
        render_probe(frequency_hz, slider_db, input_amplitude, reserve_above_slider_db=reserve_above_slider_db)
        for input_amplitude in input_amplitudes
        for frequency_hz in frequencies_hz
        for slider_db in slider_db_values
    ]
    scaling_error_db = 0.0
    for input_amplitude in input_amplitudes:
        for frequency_hz in frequencies_hz:
            rows = [
                row
                for row in probes
                if row["input_amplitude"] == input_amplitude
                and row["frequency_hz"] == frequency_hz
            ]
            reference = rows[0]
            for row in rows[1:]:
                expected_delta = row["slider_db"] - reference["slider_db"]
                measured_delta = row["injection_rms_dbfs"] - reference["injection_rms_dbfs"]
                scaling_error_db = max(scaling_error_db, abs(measured_delta - expected_delta))
    maximum_row = max(
        probes,
        key=lambda row: row["terminal_headroom_applied_peak_dbfs_before_downstream_processing"],
    )
    return {
        "report_type": (
            "axiom_v4_1_4_8_bass_aware_headroom_baseline_characterization"
            if reserve_above_slider_db is not None
            else "axiom_v4_1_4_7_sub_harmonic_branch_characterization"
        ),
        "scope": (
            "Branch-local deterministic model of the LP90 x2, soft saturation, HP90 x2, "
            "slider gain, terminal -1 dB reserve, and optional bass-aware reserve; exciter, "
            "STFT, host limiter, and program-material interactions are not modeled."
        ),
        "configuration": {
            "sample_rate_hz": SAMPLE_RATE,
            "drive": DRIVE,
            "terminal_headroom_db": HEADROOM_DB,
            "reserve_above_slider_db": reserve_above_slider_db,
            "input_amplitudes": input_amplitudes,
            "frequencies_hz": frequencies_hz,
            "slider_db_values": slider_db_values,
        },
        "checks": {
            "maximum_slider_gain_law_error_db": scaling_error_db,
            "gain_law_pass": scaling_error_db <= 1.0e-9,
        },
        "maximum_branch_peak_probe": maximum_row,
        "probes": probes,
    }


def markdown_report(report: dict) -> str:
    rows = [
        "# Axiom Sub Harmonics Characterization",
        "",
        report["scope"],
        "",
        f"Input tone peak amplitudes: `{', '.join(f'{value:.2f}' for value in report['configuration']['input_amplitudes'])}`; "
        f"drive: `{report['configuration']['drive']:.3f}`; "
        f"terminal reserve represented: `{report['configuration']['terminal_headroom_db']:.1f} dB`.",
        "",
        f"Slider gain-law check: `{'PASS' if report['checks']['gain_law_pass'] else 'FAIL'}` "
        f"(maximum error `{report['checks']['maximum_slider_gain_law_error_db']:.12f} dB`).",
        "",
        "| Input peak | Tone (Hz) | Slider (dB) | Added reserve (dB) | Injection / dry (dB) | 3rd harmonic (dBFS) | 5th harmonic (dBFS) | Branch peak after reserve (dBFS) |",
        "| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for probe in report["probes"]:
        rows.append(
            f"| {probe['input_amplitude']:.2f} | {probe['frequency_hz']:.1f} | {probe['slider_db']:.1f} | "
            f"{probe['conditional_bass_reserve_db']:.1f} | "
            f"{db_text(probe['injection_relative_to_dry_db'])} | "
            f"{db_text(probe['third_harmonic_dbfs'])} | "
            f"{db_text(probe['fifth_harmonic_dbfs'])} | "
            f"{db_text(probe['terminal_headroom_applied_peak_dbfs_before_downstream_processing'])} |"
        )
    maximum = report["maximum_branch_peak_probe"]
    rows.extend(
        [
            "",
            "Highest modeled branch-local peak:",
            "",
            f"- Input peak `{maximum['input_amplitude']:.2f}`, tone `{maximum['frequency_hz']:.1f} Hz`, "
            f"slider `{maximum['slider_db']:.1f} dB`: "
            f"`{db_text(maximum['terminal_headroom_applied_peak_dbfs_before_downstream_processing'])} dBFS` "
            "after the terminal reserve and before downstream/host interactions.",
            "",
        ]
    )
    return "\n".join(rows)


def parse_csv(value: str) -> tuple[float, ...]:
    try:
        result = tuple(float(item.strip()) for item in value.split(",") if item.strip())
    except ValueError as error:
        raise argparse.ArgumentTypeError("expected comma-separated numeric values") from error
    if not result:
        raise argparse.ArgumentTypeError("at least one numeric value is required")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--frequencies-hz", type=parse_csv, default=DEFAULT_FREQUENCIES_HZ)
    parser.add_argument("--slider-db", type=parse_csv, default=DEFAULT_SLIDER_DB)
    parser.add_argument("--input-amplitudes", type=parse_csv, default=DEFAULT_INPUT_AMPLITUDES)
    parser.add_argument(
        "--reserve-above-slider-db",
        type=float,
        help="model matching output reserve for slider gain above this value",
    )
    parser.add_argument("--json", dest="json_path", type=Path)
    parser.add_argument("--markdown", dest="markdown_path", type=Path)
    args = parser.parse_args()
    if any(not 0.0 < amplitude <= 1.0 for amplitude in args.input_amplitudes):
        parser.error("--input-amplitudes must contain values greater than zero and no greater than one")
    report = create_report(
        args.frequencies_hz,
        args.slider_db,
        args.input_amplitudes,
        args.reserve_above_slider_db,
    )
    if args.json_path:
        args.json_path.parent.mkdir(parents=True, exist_ok=True)
        args.json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="ascii")
    if args.markdown_path:
        args.markdown_path.parent.mkdir(parents=True, exist_ok=True)
        args.markdown_path.write_text(markdown_report(report), encoding="ascii")
    print(markdown_report(report))
    return 0 if report["checks"]["gain_law_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
