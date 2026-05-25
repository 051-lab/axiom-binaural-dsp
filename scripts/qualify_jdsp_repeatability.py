#!/usr/bin/env python3
"""Qualify repeated offline JDSP WAV captures of one script and stimulus."""

from __future__ import annotations

import argparse
import json
import statistics
from pathlib import Path

from compare_jdsp_captures import analyze_capture, compare_aligned, read_capture


def format_db(value: float | None) -> str:
    return "-inf" if value is None else f"{value:.6f}"


def spread_metrics(values: list[float | None]) -> dict:
    finite = [value for value in values if value is not None]
    if len(finite) != len(values) or not finite:
        return {"values_dbfs": values, "mean_dbfs": None, "standard_deviation_db": None, "spread_db": None}
    return {
        "values_dbfs": values,
        "mean_dbfs": statistics.fmean(finite),
        "standard_deviation_db": statistics.pstdev(finite),
        "spread_db": max(finite) - min(finite),
    }


def add_failure(failures: list[str], reason: str) -> None:
    if reason not in failures:
        failures.append(reason)


def qualify(
    paths: list[Path],
    silence_dbfs: float,
    max_lag_ms: float,
    max_peak_spread_db: float,
    max_rms_spread_db: float,
    min_correlation: float,
    max_relative_jitter_ms: float | None,
) -> dict:
    captures = []
    analyses = []
    failures: list[str] = []
    for path in paths:
        capture, integrity = read_capture(path)
        captures.append(capture)
        analyses.append(
            analyze_capture(capture, silence_dbfs) if capture else {"format_integrity": integrity}
        )
        if not capture:
            add_failure(failures, f"{path}: invalid or unsupported stereo PCM WAV")

    valid = [capture for capture in captures if capture is not None]
    reference = captures[0]
    if valid and len(valid) != len(captures):
        add_failure(failures, "repeatability metrics unavailable until every capture passes format validation")
    if len(valid) == len(captures) and reference:
        expected = (reference.sample_rate, reference.sample_width, len(reference.left))
        for path, capture in zip(paths[1:], captures[1:]):
            if (capture.sample_rate, capture.sample_width, len(capture.left)) != expected:
                add_failure(
                    failures,
                    f"{path}: format or frame count differs from the reference capture",
                )
        for path, analysis in zip(paths, analyses):
            if analysis["channels"]["combined"]["silent"]:
                add_failure(failures, f"{path}: capture is silent at {silence_dbfs:.1f} dBFS threshold")
            clipped = analysis["channels"]["combined"]["clipped_samples"]
            if clipped:
                add_failure(failures, f"{path}: capture contains {clipped} clipped channel samples")

    compatible = len(valid) == len(captures) and not any(
        "format or frame count differs" in failure for failure in failures
    )
    metrics = {"peak": {}, "rms": {}}
    alignments: list[dict] = []
    jitter: dict = {
        "qualified": False,
        "reason": "informational only; set --max-relative-jitter-ms when the stimulus has a reliable timing feature",
        "spread_ms": None,
        "threshold_ms": max_relative_jitter_ms,
    }
    usable_for_alignment = compatible and not any(
        reason in failure for reason in ("capture is silent", "clipped channel samples") for failure in failures
    )
    if compatible:
        peak_values = [analysis["channels"]["combined"]["peak_dbfs"] for analysis in analyses]
        rms_values = [analysis["channels"]["combined"]["rms_dbfs"] for analysis in analyses]
        metrics = {"peak": spread_metrics(peak_values), "rms": spread_metrics(rms_values)}
        if metrics["peak"]["spread_db"] is not None and metrics["peak"]["spread_db"] > max_peak_spread_db:
            add_failure(
                failures,
                f"peak spread {metrics['peak']['spread_db']:.6f} dB exceeds {max_peak_spread_db:.6f} dB",
            )
        if metrics["rms"]["spread_db"] is not None and metrics["rms"]["spread_db"] > max_rms_spread_db:
            add_failure(
                failures,
                f"RMS spread {metrics['rms']['spread_db']:.6f} dB exceeds {max_rms_spread_db:.6f} dB",
            )
    if usable_for_alignment and reference:
        alignments.append(
            {
                "capture_path": str(paths[0]),
                "relative_delay_frames": 0,
                "relative_delay_ms": 0.0,
                "normalized_correlation": 1.0,
                "confident": True,
            }
        )
        max_lag_frames = int(round(reference.sample_rate * max_lag_ms / 1000.0))
        for path, capture in zip(paths[1:], captures[1:]):
            alignment = compare_aligned(reference, capture, max_lag_ms)["alignment"]
            correlation = alignment["normalized_correlation"]
            boundary = max_lag_frames > 0 and abs(alignment["candidate_delay_frames"]) >= max_lag_frames
            confident = correlation >= min_correlation and not boundary
            alignments.append(
                {
                    "capture_path": str(path),
                    "relative_delay_frames": alignment["candidate_delay_frames"],
                    "relative_delay_ms": alignment["candidate_delay_ms"],
                    "normalized_correlation": correlation,
                    "search_boundary_reached": boundary,
                    "confident": confident,
                }
            )
            if correlation < min_correlation:
                add_failure(
                    failures,
                    f"{path}: aligned correlation {correlation:.9f} is below {min_correlation:.9f}",
                )
            if boundary:
                add_failure(f"{path}: best alignment reached the configured lag search boundary")
        confident = all(item["confident"] for item in alignments)
        if max_relative_jitter_ms is not None:
            if confident:
                delays = [item["relative_delay_ms"] for item in alignments]
                jitter_spread = max(delays) - min(delays)
                jitter = {
                    "qualified": True,
                    "reason": "relative content-alignment spread; not absolute host latency",
                    "spread_ms": jitter_spread,
                    "threshold_ms": max_relative_jitter_ms,
                }
                if jitter_spread > max_relative_jitter_ms:
                    add_failure(
                        failures,
                        f"relative jitter {jitter_spread:.6f} ms exceeds {max_relative_jitter_ms:.6f} ms",
                    )
            else:
                jitter["reason"] = "not qualified because at least one content alignment lacks confidence"

    return {
        "status": "pass" if not failures else "fail",
        "qualification": {
            "scope": "real-host capture-path relative repeatability only",
            "capture_count": len(paths),
            "decision_grade_recommendation": "Use at least 5 same-script, same-stimulus captures for decision-grade reports.",
            "failures": failures,
            "threshold_policy": "Variance, correlation, and optional jitter limits are caller-supplied acceptance policy; this tool does not claim validated host tolerances.",
            "thresholds": {
                "silence_dbfs": silence_dbfs,
                "max_peak_spread_db": max_peak_spread_db,
                "max_rms_spread_db": max_rms_spread_db,
                "min_aligned_correlation": min_correlation,
                "max_lag_ms": max_lag_ms,
                "max_relative_jitter_ms": max_relative_jitter_ms,
            },
        },
        "captures": [
            {"path": str(path), **analysis} for path, analysis in zip(paths, analyses)
        ],
        "variance": metrics,
        "alignment": {
            "basis": "Relative repeatability: each run is content-aligned against the first capture.",
            "absolute_latency": "not measured or qualified; no original stimulus time reference is supplied",
            "runs": alignments,
            "relative_jitter": jitter,
        },
    }


def markdown_report(report: dict) -> str:
    thresholds = report["qualification"]["thresholds"]
    jitter_limit = thresholds["max_relative_jitter_ms"]
    jitter_limit_text = "-" if jitter_limit is None else f"{jitter_limit:.6f}"
    lines = [
        "# JDSP Repeated-Run Qualification",
        "",
        f"Status: **{report['status'].upper()}**",
        "",
        f"Scope: {report['qualification']['scope']}.",
        "",
        f"{report['qualification']['threshold_policy']}",
        "",
        f"{report['qualification']['decision_grade_recommendation']}",
        "",
        "## Acceptance Policy",
        "",
        "| Gate | Caller-selected limit |",
        "| --- | ---: |",
        f"| Silence rejection threshold (dBFS) | {thresholds['silence_dbfs']:.6f} |",
        f"| Maximum peak spread (dB) | {thresholds['max_peak_spread_db']:.6f} |",
        f"| Maximum RMS spread (dB) | {thresholds['max_rms_spread_db']:.6f} |",
        f"| Minimum aligned correlation | {thresholds['min_aligned_correlation']:.9f} |",
        f"| Alignment search range (ms) | {thresholds['max_lag_ms']:.6f} |",
        f"| Maximum relative jitter (ms) | {jitter_limit_text} |",
        "",
        "## Result",
        "",
    ]
    failures = report["qualification"]["failures"]
    if failures:
        lines.extend([f"- FAIL: {failure}" for failure in failures])
    else:
        lines.append("- PASS: all requested qualification thresholds were met.")
    lines.extend(
        [
            "",
            "## Captures",
            "",
            "| Run | File | Valid stereo PCM | Silent | Clipped samples | Peak (dBFS) | RMS (dBFS) |",
            "| ---: | --- | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for number, item in enumerate(report["captures"], start=1):
        valid = item["format_integrity"].get("valid_stereo_pcm", False)
        combined = item.get("channels", {}).get("combined", {})
        lines.append(
            f"| {number} | `{item['path']}` | {valid} | {combined.get('silent', '-')} | "
            f"{combined.get('clipped_samples', '-')} | {format_db(combined.get('peak_dbfs'))} | "
            f"{format_db(combined.get('rms_dbfs'))} |"
        )
    variance = report["variance"]
    lines.extend(
        [
            "",
            "## Variance",
            "",
            "| Metric | Spread (dB) | Standard deviation (dB) |",
            "| --- | ---: | ---: |",
            f"| Peak | {format_db(variance['peak'].get('spread_db'))} | {format_db(variance['peak'].get('standard_deviation_db'))} |",
            f"| RMS | {format_db(variance['rms'].get('spread_db'))} | {format_db(variance['rms'].get('standard_deviation_db'))} |",
            "",
            "## Relative Alignment",
            "",
            f"{report['alignment']['basis']} Absolute latency is {report['alignment']['absolute_latency']}.",
            "",
            "| Run | Relative delay (ms) | Correlation | Confident |",
            "| ---: | ---: | ---: | ---: |",
        ]
    )
    for number, item in enumerate(report["alignment"]["runs"], start=1):
        lines.append(
            f"| {number} | {item['relative_delay_ms']:.6f} | "
            f"{item['normalized_correlation']:.9f} | {item['confident']} |"
        )
    jitter = report["alignment"]["relative_jitter"]
    lines.extend(
        [
            "",
            f"Relative jitter qualified: `{jitter['qualified']}`. {jitter['reason']}.",
        ]
    )
    if jitter["qualified"]:
        lines.append(
            f"Relative jitter spread: `{jitter['spread_ms']:.6f} ms` "
            f"(limit `{jitter['threshold_ms']:.6f} ms`)."
        )
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "captures",
        nargs="+",
        type=Path,
        help="three or more existing captures of one script/stimulus; five recommended",
    )
    parser.add_argument("--json", dest="json_path", type=Path, help="JSON report destination")
    parser.add_argument("--markdown", dest="markdown_path", type=Path, help="Markdown report destination")
    parser.add_argument("--silence-dbfs", type=float, default=-90.0)
    parser.add_argument("--max-lag-ms", type=float, default=100.0)
    parser.add_argument(
        "--max-peak-spread-db",
        type=float,
        required=True,
        help="caller-selected peak repeatability acceptance limit",
    )
    parser.add_argument(
        "--max-rms-spread-db",
        type=float,
        required=True,
        help="caller-selected RMS repeatability acceptance limit",
    )
    parser.add_argument(
        "--min-correlation",
        type=float,
        required=True,
        help="caller-selected confidence floor for content alignment",
    )
    parser.add_argument(
        "--max-relative-jitter-ms",
        type=float,
        help="enable relative-delay spread gating only for timing-identifiable stimuli",
    )
    args = parser.parse_args()
    if len(args.captures) < 3:
        parser.error("provide at least three capture WAV files; five are recommended for decision-grade reports")
    for name in ("max_lag_ms", "max_peak_spread_db", "max_rms_spread_db"):
        if getattr(args, name) < 0.0:
            parser.error(f"--{name.replace('_', '-')} cannot be negative")
    if args.max_relative_jitter_ms is not None and args.max_relative_jitter_ms < 0.0:
        parser.error("--max-relative-jitter-ms cannot be negative")
    if args.max_relative_jitter_ms is not None and args.max_lag_ms == 0.0:
        parser.error("--max-relative-jitter-ms requires --max-lag-ms greater than zero")
    if not -1.0 <= args.min_correlation <= 1.0:
        parser.error("--min-correlation must be within [-1, 1]")
    json_path = args.json_path or args.captures[0].parent / "repeatability.json"
    markdown_path = args.markdown_path or args.captures[0].parent / "repeatability.md"
    report = qualify(
        args.captures,
        args.silence_dbfs,
        args.max_lag_ms,
        args.max_peak_spread_db,
        args.max_rms_spread_db,
        args.min_correlation,
        args.max_relative_jitter_ms,
    )
    json_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="ascii")
    markdown_path.write_text(markdown_report(report), encoding="ascii")
    print(json_path)
    print(markdown_path)
    print(f"status={report['status']}")
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
