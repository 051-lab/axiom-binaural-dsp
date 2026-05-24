#!/usr/bin/env python3
"""Measure a stimulus-conditioned end-to-end JDSP host-path spectral response."""

from __future__ import annotations

import argparse
import cmath
import json
import math
import struct
import wave
from dataclasses import dataclass
from pathlib import Path


DEFAULT_FREQUENCIES_HZ = (
    20.0, 31.5, 40.0, 63.0, 90.0, 120.0, 150.0, 250.0,
    500.0, 1000.0, 2000.0, 4000.0, 6000.0, 10000.0, 16000.0, 20000.0,
)
DEFAULT_INPUT_GATE_DB = -60.0
DEFAULT_MAX_CAPTURE_PEAK_DBFS = -6.0
DEFAULT_SILENCE_DBFS = -90.0
MATRIX_PATHS = (
    ("M_to_M", "mid", "mid"),
    ("M_to_S", "mid", "side"),
    ("S_to_M", "side", "mid"),
    ("S_to_S", "side", "side"),
)


@dataclass
class StereoWav:
    path: Path
    sample_rate: int
    sample_width: int
    left: list[float]
    right: list[float]
    integrity: dict
    clip_level: float


class AnalysisError(ValueError):
    pass


def db(value: float) -> float | None:
    return 20.0 * math.log10(value) if value > 0.0 else None


def db_text(value: float | None) -> str:
    return "-inf" if value is None else f"{value:.3f}"


def optional_text(value: float | None, digits: int = 3) -> str:
    return "-" if value is None else f"{value:.{digits}f}"


def decode_sample(data: bytes, offset: int, sample_width: int) -> float:
    if sample_width == 1:
        return (data[offset] - 128) / 128.0
    if sample_width == 2:
        return struct.unpack_from("<h", data, offset)[0] / 32768.0
    if sample_width == 3:
        return int.from_bytes(data[offset:offset + 3], "little", signed=True) / 8388608.0
    if sample_width == 4:
        return struct.unpack_from("<i", data, offset)[0] / 2147483648.0
    raise AnalysisError(f"unsupported PCM sample width: {sample_width} bytes")


def read_stereo_wav(path: Path) -> StereoWav:
    try:
        with wave.open(str(path), "rb") as source:
            channels = source.getnchannels()
            sample_width = source.getsampwidth()
            sample_rate = source.getframerate()
            declared_frames = source.getnframes()
            compression = source.getcomptype()
            raw = source.readframes(declared_frames)
    except (OSError, EOFError, wave.Error) as error:
        raise AnalysisError(f"cannot read WAV {path}: {error}") from error
    bytes_per_frame = channels * sample_width
    decoded_frames = len(raw) // bytes_per_frame if bytes_per_frame else 0
    valid = (
        compression == "NONE"
        and channels == 2
        and sample_width in (1, 2, 3, 4)
        and sample_rate > 0
        and len(raw) == declared_frames * bytes_per_frame
    )
    if not valid:
        raise AnalysisError(
            f"{path} must be complete uncompressed stereo PCM with 8/16/24/32-bit samples"
        )
    left = []
    right = []
    for offset in range(0, len(raw), bytes_per_frame):
        left.append(decode_sample(raw, offset, sample_width))
        right.append(decode_sample(raw, offset + sample_width, sample_width))
    integrity = {
        "path": str(path),
        "valid_stereo_pcm": True,
        "sample_rate_hz": sample_rate,
        "sample_width_bits": sample_width * 8,
        "frames": decoded_frames,
        "duration_seconds": decoded_frames / sample_rate,
    }
    clip_level = 1.0 - 1.0 / (2 ** (sample_width * 8 - 1))
    return StereoWav(path, sample_rate, sample_width, left, right, integrity, clip_level)


def level_metrics(wav: StereoWav) -> dict:
    samples = wav.left + wav.right
    peak = max((abs(value) for value in samples), default=0.0)
    rms = math.sqrt(sum(value * value for value in samples) / len(samples)) if samples else 0.0
    clipped = sum(abs(value) >= wav.clip_level for value in samples)
    return {
        "peak": peak,
        "peak_dbfs": db(peak),
        "rms": rms,
        "rms_dbfs": db(rms),
        "clipped_samples": clipped,
        "clipped": clipped > 0,
    }


def next_power_of_two(value: int) -> int:
    result = 1
    while result < value:
        result *= 2
    return result


def fft(values: list[float], size: int) -> list[complex]:
    transformed = [complex(value) for value in values]
    transformed.extend([0j] * (size - len(transformed)))
    index = 0
    for source in range(1, size):
        bit = size >> 1
        while index & bit:
            index ^= bit
            bit >>= 1
        index ^= bit
        if source < index:
            transformed[source], transformed[index] = transformed[index], transformed[source]
    length = 2
    while length <= size:
        step = cmath.exp(-2j * math.pi / length)
        half = length // 2
        for start in range(0, size, length):
            twiddle = 1.0 + 0j
            for offset in range(half):
                even = transformed[start + offset]
                odd = transformed[start + offset + half] * twiddle
                transformed[start + offset] = even + odd
                transformed[start + offset + half] = even - odd
                twiddle *= step
        length *= 2
    return transformed


def combine_spectrum(left: list[complex], right: list[complex], side: bool) -> list[complex]:
    sign = -1.0 if side else 1.0
    return [(a + sign * b) * 0.5 for a, b in zip(left, right)]


def path_spectra(
    stimulus: StereoWav, output: StereoWav, pre_roll_frames: int, fft_size: int
) -> tuple[dict[str, list[complex]], dict[str, list[complex]]]:
    prefix = [0.0] * pre_roll_frames
    stimulus_left = prefix + stimulus.left
    stimulus_right = prefix + stimulus.right
    source_left = fft(stimulus_left, fft_size)
    source_right = fft(stimulus_right, fft_size)
    output_left = fft(output.left, fft_size)
    output_right = fft(output.right, fft_size)
    source = {
        "left": source_left,
        "right": source_right,
        "mid": combine_spectrum(source_left, source_right, side=False),
        "side": combine_spectrum(source_left, source_right, side=True),
    }
    processed = {
        "left": output_left,
        "right": output_right,
        "mid": combine_spectrum(output_left, output_right, side=False),
        "side": combine_spectrum(output_left, output_right, side=True),
    }
    return source, processed


def transfer_at_bin(source: list[complex], processed: list[complex], bin_index: int) -> complex:
    return processed[bin_index] / source[bin_index]


def summarize_path(
    source: list[complex],
    processed: list[complex],
    sample_rate: int,
    fft_size: int,
    frequencies_hz: tuple[float, ...],
    input_gate_db: float,
    identifiable: bool,
    identifiability_reason: str,
) -> dict:
    half = fft_size // 2
    source_peak = max((abs(value) for value in source[1:half]), default=0.0)
    points = []
    valid_points = 0
    for requested_frequency in frequencies_hz:
        bin_index = int(round(requested_frequency * fft_size / sample_rate))
        if not 1 <= bin_index < half:
            continue
        actual_frequency = bin_index * sample_rate / fft_size
        input_magnitude = abs(source[bin_index])
        input_relative_db = db(input_magnitude / source_peak) if source_peak else None
        excited = input_relative_db is not None and input_relative_db >= input_gate_db
        valid = identifiable and excited
        neighbor_excited = False
        if excited and 1 <= bin_index - 1 and bin_index + 1 < half and source_peak:
            neighbor_levels = [
                db(abs(source[index]) / source_peak) for index in (bin_index - 1, bin_index + 1)
            ]
            neighbor_excited = all(
                level is not None and level >= input_gate_db for level in neighbor_levels
            )
        point = {
            "requested_frequency_hz": requested_frequency,
            "frequency_hz": actual_frequency,
            "fft_bin": bin_index,
            "input_magnitude": input_magnitude,
            "input_relative_to_path_peak_db": input_relative_db,
            "valid": valid,
            "confidence": (
                "valid_identifiable_excited"
                if valid
                else "non_identifiable_source_column"
                if not identifiable
                else "below_input_energy_gate"
            ),
            "magnitude_db": None,
            "phase_deg": None,
            "group_delay_ms": None,
            "group_delay_valid": False,
        }
        if valid:
            response = transfer_at_bin(source, processed, bin_index)
            point["magnitude_db"] = db(abs(response))
            point["phase_deg"] = math.degrees(cmath.phase(response))
            valid_points += 1
            if neighbor_excited:
                before = transfer_at_bin(source, processed, bin_index - 1)
                after = transfer_at_bin(source, processed, bin_index + 1)
                if abs(before) > 0.0 and abs(after) > 0.0:
                    phase_delta = cmath.phase(after / before)
                    radians_per_bin = 2.0 * math.pi / fft_size
                    point["group_delay_ms"] = (
                        -phase_delta / (2.0 * radians_per_bin) * 1000.0 / sample_rate
                    )
                    point["group_delay_valid"] = True
        points.append(point)
    return {
        "source_path_peak_magnitude": source_peak,
        "column_identifiable": identifiable,
        "column_identifiability_reason": identifiability_reason,
        "input_energy_gate_db": input_gate_db,
        "valid_bin_count": valid_points,
        "total_reported_bin_count": len(points),
        "points": points,
    }


def matrix_identifiability(source_spectra: dict[str, list[complex]], fft_size: int, input_gate_db: float) -> dict:
    half = fft_size // 2
    peaks = {
        name: max((abs(value) for value in source_spectra[name][1:half]), default=0.0)
        for name in ("mid", "side")
    }
    dominant_peak = max(peaks.values())
    active = {}
    for name, peak in peaks.items():
        relative_db = db(peak / dominant_peak) if dominant_peak else None
        active[name] = relative_db is not None and relative_db >= input_gate_db
    if active["mid"] and not active["side"]:
        reason = "identifiable: only the input mid component is energized"
        return {
            "input_component_peak_magnitude": peaks,
            "active_input_components": {"mid": True, "side": False},
            "columns": {"mid": {"identifiable": True, "reason": reason},
                        "side": {"identifiable": False, "reason": "not identifiable: input side component is not energized"}},
        }
    if active["side"] and not active["mid"]:
        reason = "identifiable: only the input side component is energized"
        return {
            "input_component_peak_magnitude": peaks,
            "active_input_components": {"mid": False, "side": True},
            "columns": {"mid": {"identifiable": False, "reason": "not identifiable: input mid component is not energized"},
                        "side": {"identifiable": True, "reason": reason}},
        }
    if active["mid"] and active["side"]:
        reason = (
            "not identifiable: a single probe energizes both input mid and side components; "
            "separate pure probes are required for a transfer-matrix column"
        )
    else:
        reason = "not identifiable: no input mid/side component clears the energy gate"
    return {
        "input_component_peak_magnitude": peaks,
        "active_input_components": active,
        "columns": {
            "mid": {"identifiable": False, "reason": reason},
            "side": {"identifiable": False, "reason": reason},
        },
    }


def qualification(output_levels: dict, maximum_peak_dbfs: float, silence_dbfs: float) -> dict:
    reasons = []
    peak_dbfs = output_levels["peak_dbfs"]
    if output_levels["clipped"]:
        reasons.append("processed output contains clipped PCM samples")
    if peak_dbfs is not None and peak_dbfs > maximum_peak_dbfs:
        reasons.append(
            f"processed output peak {peak_dbfs:.3f} dBFS exceeds {maximum_peak_dbfs:.3f} dBFS limit"
        )
    if peak_dbfs is None or peak_dbfs <= silence_dbfs:
        level = "-inf" if peak_dbfs is None else f"{peak_dbfs:.3f} dBFS"
        reasons.append(
            f"processed output peak {level} is at or below {silence_dbfs:.3f} dBFS silence threshold"
        )
    return {
        "status": "qualified" if not reasons else "unqualified",
        "qualified": not reasons,
        "maximum_processed_output_peak_dbfs": maximum_peak_dbfs,
        "processed_output_silence_threshold_dbfs": silence_dbfs,
        "requires_no_clipped_output_samples": True,
        "requires_audible_processed_output": True,
        "reasons": reasons,
    }


def create_report(
    stimulus: StereoWav,
    processed_output: StereoWav,
    *,
    label: str | None = None,
    capture_pre_roll_ms: float = 0.0,
    frequencies_hz: tuple[float, ...] = DEFAULT_FREQUENCIES_HZ,
    input_gate_db: float = DEFAULT_INPUT_GATE_DB,
    maximum_peak_dbfs: float = DEFAULT_MAX_CAPTURE_PEAK_DBFS,
    silence_dbfs: float = DEFAULT_SILENCE_DBFS,
) -> dict:
    if stimulus.sample_rate != processed_output.sample_rate:
        raise AnalysisError("stimulus and processed output sample rates differ")
    if capture_pre_roll_ms < 0.0:
        raise AnalysisError("capture pre-roll cannot be negative")
    pre_roll_frames = int(round(capture_pre_roll_ms * stimulus.sample_rate / 1000.0))
    required_frames = pre_roll_frames + len(stimulus.left)
    if len(processed_output.left) < required_frames:
        raise AnalysisError(
            "processed output is shorter than the pre-roll plus original stimulus timeline"
        )
    fft_size = next_power_of_two(max(required_frames, len(processed_output.left)))
    source_spectra, output_spectra = path_spectra(stimulus, processed_output, pre_roll_frames, fft_size)
    identifiability = matrix_identifiability(source_spectra, fft_size, input_gate_db)
    input_levels = level_metrics(stimulus)
    output_levels = level_metrics(processed_output)
    return {
        "report_type": "stimulus_conditioned_end_to_end_host_path_transfer",
        "path_under_measurement": "end_to_end_host_path",
        "interpretation": (
            "Stimulus-conditioned spectral ratio of original input WAV to post-JDSP "
            "processed output WAV; dynamic/nonlinear stages prevent treating this as "
            "a universal or Axiom-only transfer function."
        ),
        "measurement_label": label,
        "stimulus_path": str(stimulus.path),
        "processed_output_path": str(processed_output.path),
        "format": {
            "sample_rate_hz": stimulus.sample_rate,
            "capture_pre_roll_ms": capture_pre_roll_ms,
            "capture_pre_roll_frames": pre_roll_frames,
            "capture_pre_roll_semantics": (
                "caller-supplied known intentional input lead-in included in the stimulus "
                "playback timeline; it is not measured host latency"
            ),
            "phase_alignment": (
                "no data-driven or correlation alignment; timing includes any caller-supplied "
                "known playback lead-in"
            ),
            "fft_size": fft_size,
            "fft_resolution_hz": stimulus.sample_rate / fft_size,
        },
        "measurement_level": {
            "original_stimulus": {**stimulus.integrity, **input_levels},
            "post_jdsp_processed_output": {**processed_output.integrity, **output_levels},
        },
        "qualification": qualification(output_levels, maximum_peak_dbfs, silence_dbfs),
        "energy_gate": {
            "basis": "per-source-component original stimulus FFT magnitude relative to that component peak",
            "minimum_relative_db": input_gate_db,
            "invalid_bins_have_no_reported_transfer": True,
        },
        "matrix_identifiability": identifiability,
        "mid_side_transfer_matrix": {
            name: summarize_path(
                source_spectra[source_name],
                output_spectra[output_name],
                stimulus.sample_rate,
                fft_size,
                frequencies_hz,
                input_gate_db,
                identifiability["columns"][source_name]["identifiable"],
                identifiability["columns"][source_name]["reason"],
            )
            for name, source_name, output_name in MATRIX_PATHS
        },
    }


def markdown_report(report: dict) -> str:
    fmt = report["format"]
    level = report["measurement_level"]
    qualification_data = report["qualification"]
    lines = [
        "# Stimulus-Conditioned End-to-End Host Path Transfer Report",
        "",
        f"Measurement label: `{report['measurement_label'] or '-'}`",
        "",
        "This measures the `end_to_end_host_path` from the original stimulus WAV to the "
        "post-JDSP processed output WAV. It is stimulus-conditioned and is not an "
        "Axiom-only or universal transfer function.",
        "",
        "## Qualification",
        "",
        f"Status: **{qualification_data['status']}**",
        "",
        "| Signal | Peak (dBFS) | RMS (dBFS) | Clipped samples |",
        "| --- | ---: | ---: | ---: |",
        f"| Original stimulus | {db_text(level['original_stimulus']['peak_dbfs'])} | "
        f"{db_text(level['original_stimulus']['rms_dbfs'])} | {level['original_stimulus']['clipped_samples']} |",
        f"| Post-JDSP processed output | {db_text(level['post_jdsp_processed_output']['peak_dbfs'])} | "
        f"{db_text(level['post_jdsp_processed_output']['rms_dbfs'])} | "
        f"{level['post_jdsp_processed_output']['clipped_samples']} |",
        "",
        f"Qualification requires post-JDSP output peak <= "
        f"{qualification_data['maximum_processed_output_peak_dbfs']:.3f} dBFS, above "
        f"{qualification_data['processed_output_silence_threshold_dbfs']:.3f} dBFS, "
        "and no clipped samples.",
    ]
    if qualification_data["reasons"]:
        lines.extend(["", "Reasons:"])
        lines.extend(f"- {reason}" for reason in qualification_data["reasons"])
    lines.extend([
        "",
        "## Measurement Method",
        "",
        f"Sample rate: `{fmt['sample_rate_hz']} Hz`; FFT size: `{fmt['fft_size']}`; "
        f"resolution: `{fmt['fft_resolution_hz']:.6f} Hz`.",
        "",
        f"Known intentional input lead-in supplied by the caller: `{fmt['capture_pre_roll_ms']:.6f} ms` "
        f"(`{fmt['capture_pre_roll_frames']}` frames), included in the stimulus playback timeline. "
        "It is not a measured host latency. No data-driven or correlation alignment is applied; "
        "reported timing includes any supplied lead-in.",
        "",
        f"Transfer bins are reported only when the original stimulus source-component energy is at least "
        f"`{report['energy_gate']['minimum_relative_db']:.3f} dB` relative to that source-component FFT peak.",
        "",
        "## Mid/Side Matrix Identifiability",
        "",
        "A single probe identifies one transfer-matrix column only when it energizes one input "
        "component (`M` or `S`) without energizing the other. A general stereo probe cannot "
        "separate cross-coupling contributions.",
        "",
        "| Column | Identifiable | Reason |",
        "| --- | ---: | --- |",
        f"| M input column | {report['matrix_identifiability']['columns']['mid']['identifiable']} | "
        f"{report['matrix_identifiability']['columns']['mid']['reason']} |",
        f"| S input column | {report['matrix_identifiability']['columns']['side']['identifiable']} | "
        f"{report['matrix_identifiability']['columns']['side']['reason']} |",
    ])
    for path_name, _, _ in MATRIX_PATHS:
        response = report["mid_side_transfer_matrix"][path_name]
        lines.extend([
            "",
            f"## {path_name.replace('_', ' ')}",
            "",
            f"Column identifiable: `{response['column_identifiable']}`. "
            f"{response['column_identifiability_reason']}.",
            "",
            f"Valid bins: `{response['valid_bin_count']}/{response['total_reported_bin_count']}`",
            "",
            "| Frequency (Hz) | Input relative (dB) | Valid | Magnitude (dB) | Phase (deg) | Group delay (ms) |",
            "| ---: | ---: | ---: | ---: | ---: | ---: |",
        ])
        for point in response["points"]:
            lines.append(
                f"| {point['frequency_hz']:.3f} | {db_text(point['input_relative_to_path_peak_db'])} | "
                f"{point['valid']} | {db_text(point['magnitude_db'])} | "
                f"{optional_text(point['phase_deg'])} | "
                f"{optional_text(point['group_delay_ms'], 6)} |"
            )
    lines.append("")
    return "\n".join(lines)


def parse_frequencies(value: str) -> tuple[float, ...]:
    try:
        result = tuple(float(item.strip()) for item in value.split(",") if item.strip())
    except ValueError as error:
        raise argparse.ArgumentTypeError("frequencies must be comma-separated numbers") from error
    if not result or any(frequency <= 0.0 for frequency in result):
        raise argparse.ArgumentTypeError("frequencies must be positive")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stimulus", type=Path, help="original deterministic input WAV")
    parser.add_argument("processed_output", type=Path, help="post-JDSP real-host output WAV")
    parser.add_argument("--json", dest="json_path", type=Path, help="JSON report destination")
    parser.add_argument("--markdown", dest="markdown_path", type=Path, help="Markdown report destination")
    parser.add_argument("--label", help="stable script/capture label retained in reports")
    parser.add_argument(
        "--capture-pre-roll-ms",
        type=float,
        default=0.0,
        help="known intentional input lead-in in the stimulus playback timeline; not inferred latency",
    )
    parser.add_argument("--frequencies-hz", type=parse_frequencies, default=DEFAULT_FREQUENCIES_HZ)
    parser.add_argument("--input-gate-db", type=float, default=DEFAULT_INPUT_GATE_DB)
    parser.add_argument("--max-output-peak-dbfs", type=float, default=DEFAULT_MAX_CAPTURE_PEAK_DBFS)
    parser.add_argument(
        "--silence-dbfs",
        type=float,
        default=DEFAULT_SILENCE_DBFS,
        help="processed output peak at or below this threshold is unqualified",
    )
    args = parser.parse_args()
    json_path = args.json_path or args.processed_output.with_suffix(".transfer.json")
    markdown_path = args.markdown_path or args.processed_output.with_suffix(".transfer.md")
    try:
        report = create_report(
            read_stereo_wav(args.stimulus),
            read_stereo_wav(args.processed_output),
            label=args.label,
            capture_pre_roll_ms=args.capture_pre_roll_ms,
            frequencies_hz=args.frequencies_hz,
            input_gate_db=args.input_gate_db,
            maximum_peak_dbfs=args.max_output_peak_dbfs,
            silence_dbfs=args.silence_dbfs,
        )
    except AnalysisError as error:
        parser.error(str(error))
    json_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="ascii")
    markdown_path.write_text(markdown_report(report), encoding="ascii")
    print(json_path)
    print(markdown_path)
    print(f"qualification={report['qualification']['status']}")
    return 0 if report["qualification"]["qualified"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
