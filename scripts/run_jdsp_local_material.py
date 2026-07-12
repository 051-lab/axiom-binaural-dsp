#!/usr/bin/env python3
"""Render private local audio excerpts through JDSP without storing sources in-repository."""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import subprocess
import sys
from typing import Any

import analyze_audio_perceptual_metrics as perceptual


class MaterialError(RuntimeError):
    pass


def run(command: list[str], label: str) -> None:
    result = subprocess.run(command, text=True, capture_output=True, check=False)
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or f"exit {result.returncode}"
        raise MaterialError(f"{label} failed: {detail}")


def metric_db(value: float | None) -> str:
    return "-" if value is None else f"{value:.3f}"


def slug(label: str) -> str:
    value = re.sub(r"[^A-Za-z0-9._-]+", "_", label.strip()).strip("._-")
    if not value:
        raise MaterialError("each local-material item requires a non-empty filesystem-safe label")
    return value


def read_manifest(path: pathlib.Path) -> list[dict[str, Any]]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise MaterialError(f"cannot read local-material manifest {path}: {exc}") from exc
    tracks = data.get("tracks") if isinstance(data, dict) else None
    if not isinstance(tracks, list) or not tracks:
        raise MaterialError("local-material manifest must contain a non-empty tracks list")
    parsed: list[dict[str, Any]] = []
    names: set[str] = set()
    for item in tracks:
        if not isinstance(item, dict):
            raise MaterialError("each local-material manifest track must be an object")
        label = str(item.get("label", "")).strip()
        name = slug(label)
        if name in names:
            raise MaterialError(f"duplicate local-material label after sanitization: {label}")
        source = pathlib.Path(str(item.get("path", ""))).expanduser().resolve()
        if not source.is_file():
            raise MaterialError(f"local-material source not found: {source}")
        try:
            start = float(item.get("start_seconds", 0.0))
            duration = float(item.get("duration_seconds", 20.0))
        except (TypeError, ValueError) as exc:
            raise MaterialError(f"{label}: start_seconds and duration_seconds must be numeric") from exc
        if start < 0.0 or duration <= 0.0 or duration > 60.0:
            raise MaterialError(f"{label}: start must be non-negative and duration must be in (0, 60] seconds")
        parsed_item = dict(item)
        parsed_item.update(
            {
                "label": label,
                "name": name,
                "path": source,
                "start_seconds": start,
                "duration_seconds": duration,
            }
        )
        parsed.append(parsed_item)
        names.add(name)
    return parsed


def convert_excerpt(item: dict[str, Any], destination: pathlib.Path, sample_rate: int = 48000) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    run(
        [
            "ffmpeg",
            "-nostdin",
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            "-i",
            str(item["path"]),
            "-ss",
            str(item["start_seconds"]),
            "-t",
            str(item["duration_seconds"]),
            "-vn",
            "-ac",
            "2",
            "-ar",
            str(sample_rate),
            "-c:a",
            "pcm_s16le",
            str(destination),
        ],
        f"decode local excerpt {item['label']}",
    )


def evaluate_reports(reports: list[dict[str, Any]], ceiling_dbfs: float, transparency_db: float) -> list[dict[str, str]]:
    checks: list[dict[str, str]] = []
    for item in reports:
        reference = item["report"]["captures"]["reference"]["channels"]["combined"]
        candidate = item["report"]["captures"]["candidate"]["channels"]["combined"]
        delta = candidate["peak_dbfs"] - reference["peak_dbfs"]
        integrity_fail = candidate["silent"] or candidate["clipped_samples"] > 0 or abs(delta) > transparency_db
        checks.append(
            {
                "name": f"local_{item['name']}_integrity",
                "status": "fail" if integrity_fail else "pass",
                "detail": (
                    f"candidate silent={candidate['silent']}, baseline clipping={reference['clipped_samples']}, "
                    f"candidate clipping={candidate['clipped_samples']}, "
                    f"peak delta={delta:+.3f} dB; transparency tolerance=+/-{transparency_db:.3f} dB"
                ),
            }
        )
        checks.append(
            {
                "name": f"local_{item['name']}_terminal_margin",
                "status": "investigate" if candidate["peak_dbfs"] > ceiling_dbfs else "pass",
                "detail": (
                    f"candidate peak={candidate['peak_dbfs']:.3f} dBFS; "
                    f"investigate terminal-limiter involvement above {ceiling_dbfs:.3f} dBFS"
                ),
            }
        )
    return checks


def report_status(checks: list[dict[str, str]]) -> str:
    if any(check["status"] == "fail" for check in checks):
        return "fail"
    if any(check["status"] == "investigate" for check in checks):
        return "pass_with_investigation"
    return "pass"


def markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Axiom JDSP Local Material Report",
        "",
        f"Status: **{report['status'].upper()}**",
        "",
        "Source audio is private local material. Excerpts and reports are generated only in the selected output directory.",
        "",
        "| Label | Start (s) | Duration (s) | Baseline peak (dBFS) | Candidate peak (dBFS) | Candidate true-peak proxy (dBFS) | Loudness delta (dB) | S/M delta (dB) | Baseline clipped | Candidate clipped | Margin status |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for item in report["items"]:
        reference = item["report"]["captures"]["reference"]["channels"]["combined"]
        candidate = item["report"]["captures"]["candidate"]["channels"]["combined"]
        metrics = item["report"].get("perceptual_metrics", {})
        metric_candidate = metrics.get("candidate", {})
        metric_delta = metrics.get("candidate_minus_reference", {})
        margin = next(check for check in report["checks"] if check["name"] == f"local_{item['name']}_terminal_margin")
        label = item["label"].replace("|", "\\|")
        lines.append(
            f"| {label} | {item['start_seconds']:.3f} | {item['duration_seconds']:.3f} | "
            f"{reference['peak_dbfs']:.3f} | {candidate['peak_dbfs']:.3f} | "
            f"{metric_db(metric_candidate.get('channels', {}).get('combined', {}).get('true_peak_proxy_dbfs'))} | "
            f"{metric_db(metric_delta.get('loudness', {}).get('ungated_loudness_proxy_lufs_delta'))} | "
            f"{metric_db(metric_delta.get('stereo', {}).get('side_to_mid_db_delta'))} | "
            f"{reference['clipped_samples']} | {candidate['clipped_samples']} | {margin['status'].upper()} |"
        )
    lines.extend(["", "## Checks", "", "| Check | Status | Detail |", "| --- | --- | --- |"])
    lines.extend(f"| {check['name']} | {check['status'].upper()} | {check['detail']} |" for check in report["checks"])
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("baseline_eel", type=pathlib.Path)
    parser.add_argument("candidate_eel", type=pathlib.Path)
    parser.add_argument("manifest", type=pathlib.Path, help="private JSON manifest kept outside the repository")
    parser.add_argument("output_dir", type=pathlib.Path)
    parser.add_argument("--pulse-server", required=True)
    parser.add_argument("--master-limiter-threshold-db", type=float, default=-1.0)
    parser.add_argument("--ceiling-dbfs", type=float, default=-0.50)
    parser.add_argument("--transparency-db", type=float, default=0.15)
    parser.add_argument("--sample-rate", type=int, default=48000)
    args = parser.parse_args()
    if args.sample_rate < 8000:
        parser.error("--sample-rate must be at least 8000")
    script_dir = pathlib.Path(__file__).resolve().parent
    output_dir = args.output_dir.resolve()
    items = read_manifest(args.manifest.resolve())
    reports: list[dict[str, Any]] = []
    for item in items:
        input_wav = output_dir / "excerpts" / f"{item['name']}.wav"
        baseline_wav = output_dir / "baseline" / f"{item['name']}.wav"
        candidate_wav = output_dir / "candidate" / f"{item['name']}.wav"
        compare_json = output_dir / "comparison" / f"{item['name']}.json"
        compare_md = output_dir / "comparison" / f"{item['name']}.md"
        convert_excerpt(item, input_wav, args.sample_rate)
        for eel, output, label in (
            (args.baseline_eel.resolve(), baseline_wav, "baseline"),
            (args.candidate_eel.resolve(), candidate_wav, "candidate"),
        ):
            run(
                [
                    sys.executable,
                    str(script_dir / "render_jdsp_host.py"),
                    str(input_wav),
                    str(eel),
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
                f"{item['label']} {label} host render",
            )
        run(
            [
                sys.executable,
                str(script_dir / "compare_jdsp_captures.py"),
                str(baseline_wav),
                str(candidate_wav),
                "--json",
                str(compare_json),
                "--markdown",
                str(compare_md),
            ],
            f"{item['label']} comparison",
        )
        comparison_report = json.loads(compare_json.read_text(encoding="ascii"))
        comparison_report["perceptual_metrics"] = perceptual.analyze_pair(
            baseline_wav,
            candidate_wav,
            reference_label=f"{item['name']}-baseline",
            candidate_label=f"{item['name']}-candidate",
        )
        reports.append(
            {
                "label": item["label"],
                "name": item["name"],
                "source_path": str(item["path"]),
                "start_seconds": item["start_seconds"],
                "duration_seconds": item["duration_seconds"],
                "report": comparison_report,
            }
        )
    checks = evaluate_reports(reports, args.ceiling_dbfs, args.transparency_db)
    report = {
        "status": report_status(checks),
        "scope": "private local program excerpts at original decoded level; files are not copied into the repository",
        "manifest": str(args.manifest.resolve()),
        "baseline_eel": str(args.baseline_eel.resolve()),
        "candidate_eel": str(args.candidate_eel.resolve()),
        "master_limiter_threshold_db": args.master_limiter_threshold_db,
        "ceiling_dbfs": args.ceiling_dbfs,
        "transparency_db": args.transparency_db,
        "sample_rate_hz": args.sample_rate,
        "items": reports,
        "checks": checks,
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "summary.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    (output_dir / "summary.md").write_text(markdown(report), encoding="utf-8")
    print(output_dir / "summary.json")
    print(output_dir / "summary.md")
    return 1 if report["status"] == "fail" else 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except MaterialError as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1)
