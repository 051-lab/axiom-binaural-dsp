#!/usr/bin/env python3
"""Report perceptual-proxy metrics for a stereo PCM WAV file."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import analyze_jdsp_transfer as transfer
from compare_jdsp_captures import correlation
from run_jdsp_width_material_screen import cascaded, coefficients, ratio_db, rms


ERB_LIKE_BANDS_HZ = (
    ("sub_bass", 20.0, 60.0),
    ("bass", 60.0, 150.0),
    ("low_mid", 150.0, 400.0),
    ("mid", 400.0, 1000.0),
    ("upper_mid", 1000.0, 2500.0),
    ("presence", 2500.0, 5000.0),
    ("brilliance", 5000.0, 10000.0),
    ("air", 10000.0, 20000.0),
)
DEFAULT_WINDOW_MS = 20.0


def dbfs(value: float) -> float | None:
    return 20.0 * math.log10(value) if value > 0.0 else None


def db_power(value: float) -> float | None:
    return 10.0 * math.log10(value) if value > 0.0 else None


def text(value: float | None, digits: int = 3) -> str:
    return "-" if value is None else f"{value:.{digits}f}"


def percentile(sorted_values: list[float], percent: float) -> float | None:
    if not sorted_values:
        return None
    if len(sorted_values) == 1:
        return sorted_values[0]
    position = (len(sorted_values) - 1) * percent / 100.0
    lower = int(math.floor(position))
    upper = int(math.ceil(position))
    if lower == upper:
        return sorted_values[lower]
    weight = position - lower
    return sorted_values[lower] * (1.0 - weight) + sorted_values[upper] * weight


def cubic_value(p0: float, p1: float, p2: float, p3: float, phase: float) -> float:
    phase2 = phase * phase
    phase3 = phase2 * phase
    return 0.5 * (
        (2.0 * p1)
        + (-p0 + p2) * phase
        + (2.0 * p0 - 5.0 * p1 + 4.0 * p2 - p3) * phase2
        + (-p0 + 3.0 * p1 - 3.0 * p2 + p3) * phase3
    )


def true_peak_proxy(samples: list[float], oversample: int = 4) -> float:
    peak = max((abs(sample) for sample in samples), default=0.0)
    if len(samples) < 4 or oversample <= 1:
        return peak
    for index in range(1, len(samples) - 2):
        p0 = samples[index - 1]
        p1 = samples[index]
        p2 = samples[index + 1]
        p3 = samples[index + 2]
        for step in range(1, oversample):
            peak = max(peak, abs(cubic_value(p0, p1, p2, p3, step / oversample)))
    return peak


def window_rms_values(samples: list[float], sample_rate: int, window_ms: float) -> list[float]:
    window = max(1, int(round(sample_rate * window_ms / 1000.0)))
    values = []
    for start in range(0, len(samples), window):
        chunk = samples[start:start + window]
        if chunk:
            values.append(rms(chunk))
    return values


def signal_metrics(samples: list[float], sample_rate: int, clip_level: float, window_ms: float) -> dict[str, Any]:
    sample_count = len(samples)
    peak = max((abs(sample) for sample in samples), default=0.0)
    sample_rms = rms(samples)
    true_peak = true_peak_proxy(samples)
    clipped = sum(1 for sample in samples if abs(sample) >= clip_level)
    windows = sorted(window_rms_values(samples, sample_rate, window_ms))
    p50 = percentile(windows, 50.0)
    p95 = percentile(windows, 95.0)
    p99 = percentile(windows, 99.0)
    peak_window = max(windows) if windows else None
    return {
        "samples": sample_count,
        "peak": peak,
        "peak_dbfs": dbfs(peak),
        "true_peak_proxy": true_peak,
        "true_peak_proxy_dbfs": dbfs(true_peak),
        "true_peak_proxy_overshoot_db": dbfs(true_peak / peak) if peak > 0.0 else None,
        "rms": sample_rms,
        "rms_dbfs": dbfs(sample_rms),
        "crest_db": dbfs(peak / sample_rms) if sample_rms > 0.0 else None,
        "dc_offset": sum(samples) / sample_count if sample_count else 0.0,
        "clipped_samples": clipped,
        "clipped_percent": clipped * 100.0 / sample_count if sample_count else 0.0,
        "window_ms": window_ms,
        "window_peak_rms_dbfs": dbfs(peak_window) if peak_window is not None else None,
        "window_p50_rms_dbfs": dbfs(p50) if p50 is not None else None,
        "window_p95_rms_dbfs": dbfs(p95) if p95 is not None else None,
        "window_p99_rms_dbfs": dbfs(p99) if p99 is not None else None,
        "transient_contrast_db": (
            dbfs(p99 / p50) if p50 is not None and p99 is not None and p50 > 0.0 else None
        ),
    }


def stereo_vectors(wav: transfer.StereoWav) -> dict[str, list[float]]:
    mid = [(left + right) * 0.5 for left, right in zip(wav.left, wav.right)]
    side = [(left - right) * 0.5 for left, right in zip(wav.left, wav.right)]
    return {
        "left": wav.left,
        "right": wav.right,
        "combined": wav.left + wav.right,
        "mid": mid,
        "side": side,
    }


def loudness_proxy_lufs(left: list[float], right: list[float]) -> float | None:
    if not left:
        return None
    mean_square = sum((l * l) + (r * r) for l, r in zip(left, right)) / len(left)
    value = db_power(mean_square)
    return None if value is None else -0.691 + value


def bandpass(samples: list[float], sample_rate: int, low_hz: float, high_hz: float) -> list[float]:
    high = min(high_hz, sample_rate * 0.45)
    hp = coefficients("highpass", low_hz, sample_rate)
    lp = coefficients("lowpass", high, sample_rate)
    return cascaded(cascaded(samples, hp), lp)


def band_metrics(wav: transfer.StereoWav) -> dict[str, Any]:
    vectors = stereo_vectors(wav)
    result: dict[str, Any] = {}
    for name, low_hz, high_hz in ERB_LIKE_BANDS_HZ:
        left = bandpass(vectors["left"], wav.sample_rate, low_hz, high_hz)
        right = bandpass(vectors["right"], wav.sample_rate, low_hz, high_hz)
        mid = bandpass(vectors["mid"], wav.sample_rate, low_hz, high_hz)
        side = bandpass(vectors["side"], wav.sample_rate, low_hz, high_hz)
        combined_rms = math.sqrt(
            sum((left_value * left_value) + (right_value * right_value) for left_value, right_value in zip(left, right))
            / (2.0 * len(left))
        ) if left else 0.0
        mid_rms = rms(mid)
        side_rms = rms(side)
        result[name] = {
            "low_hz": low_hz,
            "high_hz": high_hz,
            "combined_rms_dbfs": dbfs(combined_rms),
            "mid_rms_dbfs": dbfs(mid_rms),
            "side_rms_dbfs": dbfs(side_rms),
            "side_to_mid_db": ratio_db(side_rms, mid_rms),
            "left_right_correlation": correlation(left, right),
        }
    return result


def analyze(path: Path, label: str | None = None, window_ms: float = DEFAULT_WINDOW_MS) -> dict[str, Any]:
    wav = transfer.read_stereo_wav(path)
    vectors = stereo_vectors(wav)
    left_metrics = signal_metrics(vectors["left"], wav.sample_rate, wav.clip_level, window_ms)
    right_metrics = signal_metrics(vectors["right"], wav.sample_rate, wav.clip_level, window_ms)
    combined_metrics = signal_metrics(vectors["combined"], wav.sample_rate, wav.clip_level, window_ms)
    combined_true_peak = max(left_metrics["true_peak_proxy"], right_metrics["true_peak_proxy"])
    combined_metrics["true_peak_proxy"] = combined_true_peak
    combined_metrics["true_peak_proxy_dbfs"] = dbfs(combined_true_peak)
    combined_metrics["true_peak_proxy_overshoot_db"] = (
        dbfs(combined_true_peak / combined_metrics["peak"]) if combined_metrics["peak"] > 0.0 else None
    )
    mid_metrics = signal_metrics(vectors["mid"], wav.sample_rate, wav.clip_level, window_ms)
    side_metrics = signal_metrics(vectors["side"], wav.sample_rate, wav.clip_level, window_ms)
    side_to_mid = ratio_db(side_metrics["rms"], mid_metrics["rms"])
    return {
        "label": label or path.stem,
        "path": str(path),
        "format": wav.integrity,
        "metric_scope": "offline perceptual proxies; not official BS.1770 true-peak or gated LUFS",
        "loudness": {
            "ungated_loudness_proxy_lufs": loudness_proxy_lufs(wav.left, wav.right),
            "combined_rms_dbfs": combined_metrics["rms_dbfs"],
        },
        "channels": {
            "left": left_metrics,
            "right": right_metrics,
            "combined": combined_metrics,
        },
        "stereo": {
            "mid": mid_metrics,
            "side": side_metrics,
            "side_to_mid_db": side_to_mid,
            "side_to_mid_infinite": mid_metrics["rms"] == 0.0 and side_metrics["rms"] > 0.0,
            "left_right_correlation": correlation(wav.left, wav.right),
        },
        "erb_like_bands": band_metrics(wav),
    }


def delta(candidate: float | None, reference: float | None) -> float | None:
    return None if candidate is None or reference is None else candidate - reference


def compare_reports(reference: dict[str, Any], candidate: dict[str, Any]) -> dict[str, Any]:
    bands: dict[str, Any] = {}
    for name, candidate_band in candidate["erb_like_bands"].items():
        reference_band = reference["erb_like_bands"][name]
        bands[name] = {
            "combined_rms_db_delta": delta(candidate_band["combined_rms_dbfs"], reference_band["combined_rms_dbfs"]),
            "mid_rms_db_delta": delta(candidate_band["mid_rms_dbfs"], reference_band["mid_rms_dbfs"]),
            "side_rms_db_delta": delta(candidate_band["side_rms_dbfs"], reference_band["side_rms_dbfs"]),
            "side_to_mid_db_delta": delta(candidate_band["side_to_mid_db"], reference_band["side_to_mid_db"]),
            "left_right_correlation_delta": delta(
                candidate_band["left_right_correlation"], reference_band["left_right_correlation"]
            ),
        }
    return {
        "loudness": {
            "ungated_loudness_proxy_lufs_delta": delta(
                candidate["loudness"]["ungated_loudness_proxy_lufs"],
                reference["loudness"]["ungated_loudness_proxy_lufs"],
            ),
            "combined_rms_db_delta": delta(
                candidate["loudness"]["combined_rms_dbfs"],
                reference["loudness"]["combined_rms_dbfs"],
            ),
        },
        "combined": {
            "true_peak_proxy_db_delta": delta(
                candidate["channels"]["combined"]["true_peak_proxy_dbfs"],
                reference["channels"]["combined"]["true_peak_proxy_dbfs"],
            ),
            "crest_db_delta": delta(
                candidate["channels"]["combined"]["crest_db"],
                reference["channels"]["combined"]["crest_db"],
            ),
            "transient_contrast_db_delta": delta(
                candidate["channels"]["combined"]["transient_contrast_db"],
                reference["channels"]["combined"]["transient_contrast_db"],
            ),
        },
        "stereo": {
            "side_to_mid_db_delta": delta(
                candidate["stereo"]["side_to_mid_db"],
                reference["stereo"]["side_to_mid_db"],
            ),
            "left_right_correlation_delta": delta(
                candidate["stereo"]["left_right_correlation"],
                reference["stereo"]["left_right_correlation"],
            ),
        },
        "erb_like_bands": bands,
    }


def analyze_pair(
    reference_path: Path,
    candidate_path: Path,
    reference_label: str = "reference",
    candidate_label: str = "candidate",
    window_ms: float = DEFAULT_WINDOW_MS,
) -> dict[str, Any]:
    reference = analyze(reference_path, label=reference_label, window_ms=window_ms)
    candidate = analyze(candidate_path, label=candidate_label, window_ms=window_ms)
    return {
        "metric_scope": reference["metric_scope"],
        "reference": reference,
        "candidate": candidate,
        "candidate_minus_reference": compare_reports(reference, candidate),
    }


def markdown(report: dict[str, Any]) -> str:
    loudness = report["loudness"]
    combined = report["channels"]["combined"]
    stereo = report["stereo"]
    lines = [
        "# Audio Perceptual Metrics",
        "",
        f"Label: `{report['label']}`",
        "",
        "These are offline engineering proxies. They are useful for A/B direction and regression checks, but they are not official gated LUFS or certified true-peak measurements.",
        "",
        "## Summary",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
        f"| Ungated loudness proxy (LUFS-like) | {text(loudness['ungated_loudness_proxy_lufs'])} |",
        f"| Combined RMS (dBFS) | {text(loudness['combined_rms_dbfs'])} |",
        f"| True-peak proxy (dBFS) | {text(combined['true_peak_proxy_dbfs'])} |",
        f"| Sample peak (dBFS) | {text(combined['peak_dbfs'])} |",
        f"| Crest factor (dB) | {text(combined['crest_db'])} |",
        f"| 20 ms transient contrast, p99-p50 (dB) | {text(combined['transient_contrast_db'])} |",
        f"| Side/Mid RMS (dB) | {text(stereo['side_to_mid_db'])} |",
        f"| L/R correlation | {text(stereo['left_right_correlation'], 4)} |",
        "",
        "## ERB-Like Band Metrics",
        "",
        "| Band | Range | Combined RMS (dBFS) | Mid RMS (dBFS) | Side RMS (dBFS) | Side/Mid (dB) | L/R corr |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for name, values in report["erb_like_bands"].items():
        lines.append(
            f"| {name} | {values['low_hz']:.0f}-{values['high_hz']:.0f} Hz | "
            f"{text(values['combined_rms_dbfs'])} | {text(values['mid_rms_dbfs'])} | "
            f"{text(values['side_rms_dbfs'])} | {text(values['side_to_mid_db'])} | "
            f"{text(values['left_right_correlation'], 4)} |"
        )
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("wav", type=Path)
    parser.add_argument("--label")
    parser.add_argument("--window-ms", type=float, default=DEFAULT_WINDOW_MS)
    parser.add_argument("--json", type=Path)
    parser.add_argument("--markdown", type=Path)
    args = parser.parse_args()

    if args.window_ms <= 0.0:
        parser.error("--window-ms must be positive")
    report = analyze(args.wav.resolve(), label=args.label, window_ms=args.window_ms)
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    if args.markdown:
        args.markdown.parent.mkdir(parents=True, exist_ok=True)
        args.markdown.write_text(markdown(report), encoding="utf-8")
    if not args.json and not args.markdown:
        print(json.dumps(report, indent=2))
    else:
        if args.json:
            print(args.json)
        if args.markdown:
            print(args.markdown)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
