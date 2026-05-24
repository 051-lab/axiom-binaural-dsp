#!/usr/bin/env python3
"""Compare two stereo PCM WAV captures and emit JSON and Markdown reports."""

import argparse
import json
import math
import struct
import wave
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Capture:
    path: Path
    sample_rate: int
    sample_width: int
    declared_frames: int
    left: list
    right: list
    integrity: dict
    clip_level: float


def dbfs(value):
    if value <= 0.0:
        return None
    return 20.0 * math.log10(value)


def format_db(value):
    return "-inf" if value is None else f"{value:.3f}"


def format_ratio(value, infinite=False):
    return "+inf" if infinite else format_db(value)


def decode_sample(data, offset, sample_width):
    if sample_width == 1:
        return (data[offset] - 128) / 128.0
    if sample_width == 2:
        return struct.unpack_from("<h", data, offset)[0] / 32768.0
    if sample_width == 3:
        return int.from_bytes(data[offset:offset + 3], "little", signed=True) / 8388608.0
    if sample_width == 4:
        return struct.unpack_from("<i", data, offset)[0] / 2147483648.0
    raise ValueError(f"unsupported PCM sample width: {sample_width} bytes")


def read_capture(path):
    integrity = {"path": str(path), "readable": False, "valid_stereo_pcm": False}
    try:
        with wave.open(str(path), "rb") as source:
            channels = source.getnchannels()
            sample_width = source.getsampwidth()
            sample_rate = source.getframerate()
            declared_frames = source.getnframes()
            compression = source.getcomptype()
            raw = source.readframes(declared_frames)
    except (OSError, EOFError, wave.Error) as error:
        integrity["error"] = str(error)
        return None, integrity

    bytes_per_frame = channels * sample_width
    decoded_frames = len(raw) // bytes_per_frame if bytes_per_frame else 0
    integrity.update({
        "readable": True,
        "channels": channels,
        "sample_rate_hz": sample_rate,
        "sample_width_bits": sample_width * 8,
        "declared_frames": declared_frames,
        "decoded_frames": decoded_frames,
        "duration_seconds": decoded_frames / sample_rate if sample_rate else 0.0,
        "compression": compression,
        "complete_frame_data": len(raw) == declared_frames * bytes_per_frame,
    })
    try:
        supported_width = sample_width in (1, 2, 3, 4)
        valid = (
            compression == "NONE"
            and channels == 2
            and sample_rate > 0
            and supported_width
            and integrity["complete_frame_data"]
        )
        integrity["valid_stereo_pcm"] = valid
        if not valid:
            integrity["error"] = "capture must be complete, uncompressed stereo PCM with 8/16/24/32-bit samples"
            return None, integrity

        left = []
        right = []
        for offset in range(0, len(raw), bytes_per_frame):
            left.append(decode_sample(raw, offset, sample_width))
            right.append(decode_sample(raw, offset + sample_width, sample_width))
    except ValueError as error:
        integrity["error"] = str(error)
        integrity["valid_stereo_pcm"] = False
        return None, integrity

    clip_level = 1.0 - (1.0 / (2 ** (sample_width * 8 - 1)))
    return Capture(path, sample_rate, sample_width, declared_frames, left, right, integrity, clip_level), integrity


def signal_metrics(values, clip_level, silence_level):
    count = len(values)
    if not count:
        return {
            "samples": 0, "silent": True, "peak": 0.0, "peak_dbfs": None,
            "rms": 0.0, "rms_dbfs": None, "crest_db": None,
            "dc_offset": 0.0, "dc_offset_dbfs": None,
            "clipped_samples": 0, "clipped_percent": 0.0,
        }
    peak = max(abs(value) for value in values)
    rms = math.sqrt(sum(value * value for value in values) / count)
    dc = sum(values) / count
    clipped = sum(1 for value in values if abs(value) >= clip_level)
    return {
        "samples": count,
        "silent": peak <= silence_level,
        "peak": peak,
        "peak_dbfs": dbfs(peak),
        "rms": rms,
        "rms_dbfs": dbfs(rms),
        "crest_db": dbfs(peak / rms) if rms else None,
        "dc_offset": dc,
        "dc_offset_dbfs": dbfs(abs(dc)),
        "clipped_samples": clipped,
        "clipped_percent": clipped * 100.0 / count,
    }


def correlation(left, right):
    if not left:
        return None
    left_mean = sum(left) / len(left)
    right_mean = sum(right) / len(right)
    numerator = 0.0
    left_power = 0.0
    right_power = 0.0
    for left_value, right_value in zip(left, right):
        a = left_value - left_mean
        b = right_value - right_mean
        numerator += a * b
        left_power += a * a
        right_power += b * b
    denominator = math.sqrt(left_power * right_power)
    return numerator / denominator if denominator else None


def analyze_capture(capture, silence_dbfs):
    silence_level = 10.0 ** (silence_dbfs / 20.0)
    left = capture.left
    right = capture.right
    combined = left + right
    mid = [(a + b) * 0.5 for a, b in zip(left, right)]
    side = [(a - b) * 0.5 for a, b in zip(left, right)]
    channels = {
        "left": signal_metrics(left, capture.clip_level, silence_level),
        "right": signal_metrics(right, capture.clip_level, silence_level),
        "combined": signal_metrics(combined, capture.clip_level, silence_level),
    }
    mono = signal_metrics(mid, capture.clip_level, silence_level)
    side_metrics = signal_metrics(side, capture.clip_level, silence_level)
    combined_rms = channels["combined"]["rms"]
    mid_rms = mono["rms"]
    side_rms = side_metrics["rms"]
    return {
        "format_integrity": capture.integrity,
        "silence_threshold_dbfs": silence_dbfs,
        "channels": channels,
        "mono": {
            **mono,
            "rms_relative_to_stereo_db": dbfs(mid_rms / combined_rms) if combined_rms else None,
            "rms_relative_to_stereo_infinite": combined_rms == 0.0 and mid_rms > 0.0,
        },
        "mid_side": {
            "mid": mono,
            "side": side_metrics,
            "side_to_mid_db": dbfs(side_rms / mid_rms) if mid_rms else None,
            "side_to_mid_infinite": mid_rms == 0.0 and side_rms > 0.0,
            "left_right_correlation": correlation(left, right),
        },
    }


def alignment_score(reference, candidate, lag, stride=1):
    ref_start = max(0, -lag)
    candidate_start = max(0, lag)
    length = min(len(reference.left) - ref_start, len(candidate.left) - candidate_start)
    if length <= 0:
        return -1.0
    dot = 0.0
    ref_power = 0.0
    candidate_power = 0.0
    end = ref_start + length
    candidate_index = candidate_start
    for ref_index in range(ref_start, end, stride):
        ref_left = reference.left[ref_index]
        ref_right = reference.right[ref_index]
        cand_left = candidate.left[candidate_index]
        cand_right = candidate.right[candidate_index]
        dot += ref_left * cand_left + ref_right * cand_right
        ref_power += ref_left * ref_left + ref_right * ref_right
        candidate_power += cand_left * cand_left + cand_right * cand_right
        candidate_index += stride
    denominator = math.sqrt(ref_power * candidate_power)
    return dot / denominator if denominator else -1.0


def find_alignment(reference, candidate, max_lag_frames):
    if reference.left == candidate.left and reference.right == candidate.right:
        return 0
    total_power = sum(value * value for value in reference.left + reference.right + candidate.left + candidate.right)
    if total_power == 0.0:
        return 0
    length = min(len(reference.left), len(candidate.left))
    stride = max(1, length // 12000)
    coarse_lags = range(-max_lag_frames, max_lag_frames + 1, stride)
    best_lag = max(coarse_lags, key=lambda lag: alignment_score(reference, candidate, lag, stride))
    lower = max(-max_lag_frames, best_lag - stride + 1)
    upper = min(max_lag_frames, best_lag + stride - 1)
    refined_lags = range(lower, upper + 1)
    return max(refined_lags, key=lambda lag: alignment_score(reference, candidate, lag))


def compare_aligned(reference, candidate, max_lag_ms):
    max_lag_frames = int(round(reference.sample_rate * max_lag_ms / 1000.0))
    lag = find_alignment(reference, candidate, max_lag_frames)
    ref_start = max(0, -lag)
    candidate_start = max(0, lag)
    frames = min(len(reference.left) - ref_start, len(candidate.left) - candidate_start)
    reference_samples = []
    differences = []
    changed_frames = 0
    for index in range(frames):
        ref_left = reference.left[ref_start + index]
        ref_right = reference.right[ref_start + index]
        cand_left = candidate.left[candidate_start + index]
        cand_right = candidate.right[candidate_start + index]
        delta_left = cand_left - ref_left
        delta_right = cand_right - ref_right
        reference_samples.extend((ref_left, ref_right))
        differences.extend((delta_left, delta_right))
        if delta_left != 0.0 or delta_right != 0.0:
            changed_frames += 1
    diff_peak = max((abs(value) for value in differences), default=0.0)
    diff_rms = math.sqrt(sum(value * value for value in differences) / len(differences)) if differences else 0.0
    ref_rms = math.sqrt(sum(value * value for value in reference_samples) / len(reference_samples)) if reference_samples else 0.0
    changed_samples = sum(1 for value in differences if value != 0.0)
    return {
        "alignment": {
            "candidate_delay_frames": lag,
            "candidate_delay_ms": lag * 1000.0 / reference.sample_rate,
            "max_lag_searched_ms": max_lag_ms,
            "normalized_correlation": alignment_score(reference, candidate, lag),
            "overlap_frames": frames,
        },
        "difference": {
            "exact_match_after_alignment": changed_samples == 0 and len(reference.left) == len(candidate.left) and lag == 0,
            "changed_frames": changed_frames,
            "changed_samples": changed_samples,
            "max_absolute_difference": diff_peak,
            "max_absolute_difference_dbfs": dbfs(diff_peak),
            "rms_difference": diff_rms,
            "rms_difference_dbfs": dbfs(diff_rms),
            "signal_to_difference_db": dbfs(ref_rms / diff_rms) if diff_rms else None,
            "signal_to_difference_infinite": diff_rms == 0.0 and ref_rms > 0.0,
        },
    }


def markdown_report(report):
    lines = [
        "# JDSP Capture Comparison",
        "",
        f"Status: **{report['status']}**",
        "",
        "## Format and Integrity",
        "",
        "| Capture | Valid PCM stereo | Rate (Hz) | Bits | Frames | Duration (s) |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for label in ("reference", "candidate"):
        item = report["captures"][label]["format_integrity"]
        lines.append(
            f"| {label} | {item.get('valid_stereo_pcm', False)} | {item.get('sample_rate_hz', '-')} | "
            f"{item.get('sample_width_bits', '-')} | {item.get('decoded_frames', '-')} | "
            f"{item.get('duration_seconds', 0.0):.6f} |"
        )
    if not report["comparison"].get("compatible", False):
        lines.extend(["", f"Comparison unavailable: {report['comparison'].get('reason', 'invalid input')}.", ""])
        return "\n".join(lines)

    lines.extend([
        "",
        "## Signal Metrics",
        "",
        "| Capture / signal | Silent | Peak (dBFS) | RMS (dBFS) | Crest (dB) | DC (dBFS) | Clipped samples |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ])
    for capture_label in ("reference", "candidate"):
        capture = report["captures"][capture_label]
        for signal_label, metrics in (
            ("left", capture["channels"]["left"]),
            ("right", capture["channels"]["right"]),
            ("mono", capture["mono"]),
            ("mid", capture["mid_side"]["mid"]),
            ("side", capture["mid_side"]["side"]),
        ):
            lines.append(
                f"| {capture_label} / {signal_label} | {metrics['silent']} | {format_db(metrics['peak_dbfs'])} | "
                f"{format_db(metrics['rms_dbfs'])} | {format_db(metrics['crest_db'])} | "
                f"{format_db(metrics['dc_offset_dbfs'])} | {metrics['clipped_samples']} |"
            )
    lines.extend([
        "",
        "## Mono and Mid-Side",
        "",
        "| Capture | Mono RMS relative to stereo (dB) | Side / Mid (dB) | L/R correlation |",
        "| --- | ---: | ---: | ---: |",
    ])
    for label in ("reference", "candidate"):
        capture = report["captures"][label]
        lines.append(
            f"| {label} | {format_ratio(capture['mono']['rms_relative_to_stereo_db'], capture['mono']['rms_relative_to_stereo_infinite'])} | "
            f"{format_ratio(capture['mid_side']['side_to_mid_db'], capture['mid_side']['side_to_mid_infinite'])} | "
            f"{capture['mid_side']['left_right_correlation'] if capture['mid_side']['left_right_correlation'] is not None else '-'} |"
        )
    alignment = report["comparison"]["alignment"]
    difference = report["comparison"]["difference"]
    lines.extend([
        "",
        "## Alignment and Difference",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
        f"| Candidate delay (frames) | {alignment['candidate_delay_frames']} |",
        f"| Candidate delay (ms) | {alignment['candidate_delay_ms']:.6f} |",
        f"| Aligned correlation | {alignment['normalized_correlation']:.9f} |",
        f"| Compared frames | {alignment['overlap_frames']} |",
        f"| Exact match after alignment | {difference['exact_match_after_alignment']} |",
        f"| Changed samples | {difference['changed_samples']} |",
        f"| Peak difference (dBFS) | {format_db(difference['max_absolute_difference_dbfs'])} |",
        f"| RMS difference (dBFS) | {format_db(difference['rms_difference_dbfs'])} |",
        f"| Signal / difference (dB) | {format_ratio(difference['signal_to_difference_db'], difference['signal_to_difference_infinite'])} |",
        "",
    ])
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("reference", type=Path)
    parser.add_argument("candidate", type=Path)
    parser.add_argument("--json", dest="json_path", type=Path, help="JSON report destination")
    parser.add_argument("--markdown", dest="markdown_path", type=Path, help="Markdown report destination")
    parser.add_argument("--silence-dbfs", type=float, default=-90.0)
    parser.add_argument("--max-lag-ms", type=float, default=20.0)
    args = parser.parse_args()
    if args.max_lag_ms < 0.0:
        parser.error("--max-lag-ms cannot be negative")

    json_path = args.json_path or args.candidate.with_suffix(".comparison.json")
    markdown_path = args.markdown_path or args.candidate.with_suffix(".comparison.md")
    reference, reference_integrity = read_capture(args.reference)
    candidate, candidate_integrity = read_capture(args.candidate)
    report = {
        "reference_path": str(args.reference),
        "candidate_path": str(args.candidate),
        "captures": {
            "reference": analyze_capture(reference, args.silence_dbfs) if reference else {"format_integrity": reference_integrity},
            "candidate": analyze_capture(candidate, args.silence_dbfs) if candidate else {"format_integrity": candidate_integrity},
        },
        "comparison": {"compatible": False},
    }

    exit_code = 0
    if not reference or not candidate:
        report["status"] = "invalid"
        report["comparison"]["reason"] = "one or both WAV files failed stereo PCM integrity validation"
        exit_code = 2
    elif reference.sample_rate != candidate.sample_rate:
        report["status"] = "incompatible"
        report["comparison"]["reason"] = "sample rates differ; alignment requires equal-rate captures"
        exit_code = 2
    else:
        report["comparison"]["compatible"] = True
        report["comparison"].update(compare_aligned(reference, candidate, args.max_lag_ms))
        is_match = report["comparison"]["difference"]["exact_match_after_alignment"]
        report["status"] = "identical" if is_match else "different"

    json_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="ascii")
    markdown_path.write_text(markdown_report(report), encoding="ascii")
    print(json_path)
    print(markdown_path)
    print(f"status={report['status']}")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
