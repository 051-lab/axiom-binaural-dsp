#!/usr/bin/env python3
"""Render an original program-like corpus through JDSP and report output margin."""

from __future__ import annotations

import argparse
import json
import pathlib
import subprocess
import sys
from typing import Any


PROGRAM_NAMES = ("sub_kick_sequence", "sustained_bass_synth", "dense_low_end_mix")


class CorpusError(RuntimeError):
    pass


def run(command: list[str], label: str) -> None:
    result = subprocess.run(command, text=True, capture_output=True, check=False)
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or f"exit {result.returncode}"
        raise CorpusError(f"{label} failed: {detail}")


def make_checks(reports: dict[str, dict[str, Any]], ceiling_dbfs: float, transparency_db: float) -> list[dict[str, str]]:
    checks: list[dict[str, str]] = []
    for name in PROGRAM_NAMES:
        report = reports[name]
        reference = report["captures"]["reference"]["channels"]["combined"]
        candidate = report["captures"]["candidate"]["channels"]["combined"]
        delta = candidate["peak_dbfs"] - reference["peak_dbfs"]
        failed = candidate["silent"] or candidate["clipped_samples"] > 0 or abs(delta) > transparency_db
        checks.append(
            {
                "name": f"program_{name}_integrity",
                "status": "fail" if failed else "pass",
                "detail": (
                    f"candidate silent={candidate['silent']}, clipping={candidate['clipped_samples']}, "
                    f"peak delta={delta:+.3f} dB; transparency tolerance=+/-{transparency_db:.3f} dB"
                ),
            }
        )
        checks.append(
            {
                "name": f"program_{name}_terminal_margin",
                "status": "investigate" if candidate["peak_dbfs"] > ceiling_dbfs else "pass",
                "detail": (
                    f"candidate peak={candidate['peak_dbfs']:.3f} dBFS; "
                    f"investigate terminal-limiter involvement above {ceiling_dbfs:.3f} dBFS"
                ),
            }
        )
    return checks


def status(checks: list[dict[str, str]]) -> str:
    if any(check["status"] == "fail" for check in checks):
        return "fail"
    if any(check["status"] == "investigate" for check in checks):
        return "pass_with_investigation"
    return "pass"


def markdown(report: dict[str, Any]) -> str:
    rows = [
        "# Axiom JDSP Program-Like Corpus Report",
        "",
        f"Status: **{report['status'].upper()}**",
        "",
        "All passages are original deterministic test material generated in-repository; they are not commercial music excerpts.",
        "",
        "| Passage | Baseline peak (dBFS) | Candidate peak (dBFS) | Candidate clipped | Status |",
        "| --- | ---: | ---: | ---: | --- |",
    ]
    for name in PROGRAM_NAMES:
        item = report["captures"][name]
        reference = item["captures"]["reference"]["channels"]["combined"]
        candidate = item["captures"]["candidate"]["channels"]["combined"]
        observation = next(check for check in report["checks"] if check["name"] == f"program_{name}_terminal_margin")
        rows.append(
            f"| {name} | {reference['peak_dbfs']:.3f} | {candidate['peak_dbfs']:.3f} | "
            f"{candidate['clipped_samples']} | {observation['status'].upper()} |"
        )
    rows.extend(["", "## Checks", "", "| Check | Status | Detail |", "| --- | --- | --- |"])
    rows.extend(f"| {item['name']} | {item['status'].upper()} | {item['detail']} |" for item in report["checks"])
    rows.append("")
    return "\n".join(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("baseline_eel", type=pathlib.Path)
    parser.add_argument("candidate_eel", type=pathlib.Path)
    parser.add_argument("output_dir", type=pathlib.Path)
    parser.add_argument("--pulse-server", required=True)
    parser.add_argument("--master-limiter-threshold-db", type=float, default=-1.0)
    parser.add_argument("--ceiling-dbfs", type=float, default=-0.50)
    parser.add_argument("--transparency-db", type=float, default=0.15)
    args = parser.parse_args()
    script_dir = pathlib.Path(__file__).resolve().parent
    output_dir = args.output_dir.resolve()
    stimuli_dir = output_dir / "stimuli"
    reports: dict[str, dict[str, Any]] = {}
    output_dir.mkdir(parents=True, exist_ok=True)
    run([sys.executable, str(script_dir / "generate_axiom_program_corpus.py"), str(stimuli_dir)], "generate corpus")
    for name in PROGRAM_NAMES:
        stimulus = stimuli_dir / f"{name}.wav"
        baseline_wav = output_dir / "baseline" / f"{name}.wav"
        candidate_wav = output_dir / "candidate" / f"{name}.wav"
        for eel, output, label in (
            (args.baseline_eel.resolve(), baseline_wav, "baseline"),
            (args.candidate_eel.resolve(), candidate_wav, "candidate"),
        ):
            run(
                [
                    sys.executable,
                    str(script_dir / "render_jdsp_host.py"),
                    str(stimulus),
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
                f"{name} {label} render",
            )
        report_path = output_dir / "comparison" / f"{name}.json"
        markdown_path = output_dir / "comparison" / f"{name}.md"
        run(
            [
                sys.executable,
                str(script_dir / "compare_jdsp_captures.py"),
                str(baseline_wav),
                str(candidate_wav),
                "--json",
                str(report_path),
                "--markdown",
                str(markdown_path),
            ],
            f"{name} compare",
        )
        reports[name] = json.loads(report_path.read_text(encoding="ascii"))
    checks = make_checks(reports, args.ceiling_dbfs, args.transparency_db)
    report = {
        "status": status(checks),
        "baseline_eel": str(args.baseline_eel.resolve()),
        "candidate_eel": str(args.candidate_eel.resolve()),
        "master_limiter_threshold_db": args.master_limiter_threshold_db,
        "ceiling_dbfs": args.ceiling_dbfs,
        "transparency_db": args.transparency_db,
        "checks": checks,
        "captures": reports,
    }
    (output_dir / "summary.json").write_text(json.dumps(report, indent=2) + "\n", encoding="ascii")
    (output_dir / "summary.md").write_text(markdown(report), encoding="ascii")
    print(output_dir / "summary.json")
    print(output_dir / "summary.md")
    return 1 if report["status"] == "fail" else 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except CorpusError as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1)
