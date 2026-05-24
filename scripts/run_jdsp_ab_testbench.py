#!/usr/bin/env python3
"""Run a deterministic real-host A/B capture suite for two Axiom EEL scripts."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import subprocess
import sys


STIMULUS_NAMES = ("impulse", "bass_burst", "sweep", "correlated_mono", "side_only")


class TestbenchError(RuntimeError):
    pass


def run(command: list[str], label: str) -> None:
    result = subprocess.run(command, text=True, capture_output=True, check=False)
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or f"exit {result.returncode}"
        raise TestbenchError(f"{label} failed: {detail}")


def metric_db(value: float | None) -> str:
    return "-inf" if value is None else f"{value:.3f}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("baseline_eel", type=pathlib.Path)
    parser.add_argument("candidate_eel", type=pathlib.Path)
    parser.add_argument("output_dir", type=pathlib.Path)
    parser.add_argument("--pulse-server", required=True)
    parser.add_argument("--sample-rate", type=int, default=48000)
    parser.add_argument("--duration", type=float, default=2.0)
    parser.add_argument("--pre-roll-ms", type=int, default=500)
    parser.add_argument("--tail-ms", type=int, default=2000)
    args = parser.parse_args()

    script_dir = pathlib.Path(__file__).resolve().parent
    generator = script_dir / "generate_jdsp_stimuli.py"
    renderer = script_dir / "render_jdsp_host.py"
    comparator = script_dir / "compare_jdsp_captures.py"
    baseline = args.baseline_eel.resolve()
    candidate = args.candidate_eel.resolve()
    output_dir = args.output_dir.resolve()
    stimuli_dir = output_dir / "stimuli"
    baseline_dir = output_dir / "baseline"
    candidate_dir = output_dir / "candidate"
    comparison_dir = output_dir / "comparison"
    for eel in (baseline, candidate):
        if not eel.is_file():
            parser.error(f"EEL script not found: {eel}")
    if args.pre_roll_ms < 0 or args.tail_ms < 0:
        parser.error("--pre-roll-ms and --tail-ms must be non-negative")

    output_dir.mkdir(parents=True, exist_ok=True)
    run(
        [
            sys.executable,
            str(generator),
            str(stimuli_dir),
            "--sample-rate",
            str(args.sample_rate),
            "--duration",
            str(args.duration),
        ],
        "stimulus generation",
    )
    reports: dict[str, dict] = {}
    for name in STIMULUS_NAMES:
        stimulus = stimuli_dir / f"{name}.wav"
        baseline_capture = baseline_dir / f"{name}.wav"
        candidate_capture = candidate_dir / f"{name}.wav"
        for label, eel, destination in (
            ("baseline", baseline, baseline_capture),
            ("candidate", candidate, candidate_capture),
        ):
            run(
                [
                    sys.executable,
                    str(renderer),
                    str(stimulus),
                    str(eel),
                    str(destination),
                    "--pulse-server",
                    args.pulse_server,
                    "--pre-roll-ms",
                    str(args.pre_roll_ms),
                    "--tail-ms",
                    str(args.tail_ms),
                ],
                f"{name} {label} host render",
            )
        json_path = comparison_dir / f"{name}.json"
        markdown_path = comparison_dir / f"{name}.md"
        run(
            [
                sys.executable,
                str(comparator),
                str(baseline_capture),
                str(candidate_capture),
                "--json",
                str(json_path),
                "--markdown",
                str(markdown_path),
            ],
            f"{name} capture comparison",
        )
        reports[name] = json.loads(json_path.read_text(encoding="ascii"))

    aggregate = {
        "generated_at": dt.datetime.now(tz=dt.timezone.utc).isoformat(),
        "baseline_eel": str(baseline),
        "candidate_eel": str(candidate),
        "pulse_server": args.pulse_server,
        "sample_rate_hz": args.sample_rate,
        "stimuli": reports,
    }
    (output_dir / "summary.json").write_text(
        json.dumps(aggregate, indent=2, sort_keys=True) + "\n", encoding="ascii"
    )
    rows = [
        "# Axiom JDSP Real-Host A/B Report",
        "",
        f"Baseline: `{baseline}`",
        "",
        f"Candidate: `{candidate}`",
        "",
        "| Stimulus | Status | Delay (ms) | Difference RMS (dBFS) | Candidate peak (dBFS) | Candidate clipped |",
        "| --- | --- | ---: | ---: | ---: | ---: |",
    ]
    for name in STIMULUS_NAMES:
        report = reports[name]
        comparison = report["comparison"]
        candidate_metrics = report["captures"]["candidate"]["channels"]["combined"]
        rows.append(
            f"| {name} | {report['status']} | "
            f"{comparison['alignment']['candidate_delay_ms']:.6f} | "
            f"{metric_db(comparison['difference']['rms_difference_dbfs'])} | "
            f"{metric_db(candidate_metrics['peak_dbfs'])} | "
            f"{candidate_metrics['clipped_samples']} |"
        )
    rows.extend(["", f"Detailed per-stimulus reports: `{comparison_dir}`", ""])
    (output_dir / "summary.md").write_text("\n".join(rows), encoding="ascii")
    print(output_dir / "summary.json")
    print(output_dir / "summary.md")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except TestbenchError as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1)
