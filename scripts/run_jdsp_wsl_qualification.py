#!/usr/bin/env python3
"""Run Axiom real-JDSP qualification with managed WSL audio routing."""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import signal
import subprocess
import sys
from typing import Any


DEFAULT_PULSE_SERVER = "unix:/tmp/jdsp-win/native"
DEFAULT_ROUTE_HELPER = pathlib.Path.home() / ".local/bin/jdsp-audio-reset"
CONTINUOUS_PROBES = ("bass_burst", "bass_pressure_90hz", "sweep", "correlated_mono", "side_only")
BOOST_EXACT_PROBES = ("bass_burst", "correlated_mono", "side_only")
PRESSURE_PROBES = ("bass_pressure_90hz",)


class QualificationError(RuntimeError):
    pass


def run(
    command: list[str],
    label: str,
    *,
    env: dict[str, str] | None = None,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(command, text=True, capture_output=True, check=False, env=env)
    if check and result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or f"exit {result.returncode}"
        raise QualificationError(f"{label} failed: {detail}")
    return result


def pulse_environment(pulse_server: str) -> dict[str, str]:
    environment = os.environ.copy()
    environment["PULSE_SERVER"] = pulse_server
    return environment


def validate_route(pulse_server: str) -> None:
    environment = pulse_environment(pulse_server)
    sinks = run(["pactl", "list", "short", "sinks"], "inspect managed PulseAudio sinks", env=environment).stdout
    names = {line.split("\t")[1] for line in sinks.splitlines() if "\t" in line}
    if "JamesDSP" not in names:
        raise QualificationError(
            f"managed route does not expose the JamesDSP sink; available sinks: {', '.join(sorted(names)) or '<none>'}"
        )
    run(["jamesdsp", "--is-connected"], "verify JamesDSP service", env=environment)


def read_jdsp_setting(key: str) -> str:
    return run(["jamesdsp", "--get", key], f"read JDSP setting {key}").stdout.strip()


def set_jdsp_setting(key: str, value: str) -> None:
    run(["jamesdsp", "--set", f"{key}={value}"], f"write JDSP setting {key}", check=False)
    applied = read_jdsp_setting(key)
    if applied != value:
        raise QualificationError(f"JDSP did not apply {key}={value}; current value is {applied}")


def ancestor_pids() -> set[int]:
    protected = {os.getpid()}
    pid = os.getppid()
    while pid > 1 and pid not in protected:
        protected.add(pid)
        try:
            fields = pathlib.Path(f"/proc/{pid}/stat").read_text(encoding="ascii").split()
            pid = int(fields[3])
        except (FileNotFoundError, OSError, ValueError, IndexError):
            break
    return protected


def stop_managed_route(pulse_server: str) -> list[str]:
    errors: list[str] = []
    runtime_dir = pathlib.Path("/tmp/jdsp-win")
    for pid_name in ("xvfb.pid", "openbox.pid", "cursor.pid", "x11vnc.pid", "novnc.pid"):
        pid_path = runtime_dir / pid_name
        try:
            pid = int(pid_path.read_text(encoding="ascii").strip())
            os.kill(pid, signal.SIGTERM)
        except FileNotFoundError:
            continue
        except ProcessLookupError:
            continue
        except (OSError, ValueError) as exc:
            errors.append(f"unable to stop {pid_name}: {exc}")
    run(["pkill", "-x", "jamesdsp"], "stop managed JamesDSP", check=False)
    protected = ancestor_pids()
    for process_path in pathlib.Path("/proc").glob("[0-9]*/cmdline"):
        try:
            pid = int(process_path.parent.name)
            command = process_path.read_bytes().replace(b"\0", b" ")
            if pid not in protected and b"/tmp/jdsp-win/out.raw" in command:
                os.kill(pid, signal.SIGTERM)
        except (FileNotFoundError, ProcessLookupError):
            continue
        except (OSError, ValueError) as exc:
            errors.append(f"unable to stop managed pipe-sink feeder: {exc}")
    run(
        [
            "powershell.exe",
            "-NoProfile",
            "-Command",
            "Get-Process ffplay -ErrorAction SilentlyContinue | Stop-Process -Force",
        ],
        "stop managed Windows audio sink",
        check=False,
    )
    run(["pactl", "exit"], "stop managed PulseAudio server", env=pulse_environment(pulse_server), check=False)
    service = run(
        ["systemctl", "--user", "start", "pipewire-pulse.socket", "pipewire-pulse.service"],
        "restore PipeWire-Pulse service",
        check=False,
    )
    if service.returncode != 0:
        errors.append(service.stderr.strip() or "unable to restore PipeWire-Pulse service")
    return errors


def slider_fixture(source: pathlib.Path, destination: pathlib.Path, slider_db: float) -> None:
    value = f"{slider_db:g}"
    text = source.read_text(encoding="ascii")
    slider_signature = "slider1:4<"
    init_signature = "slider1 = 4;"
    if text.count(slider_signature) != 1 or text.count(init_signature) != 1:
        raise QualificationError(f"cannot make audited slider fixture from {source}: expected default slider signatures missing")
    altered = text.replace(slider_signature, f"slider1:{value}<", 1).replace(
        init_signature, f"slider1 = {value};", 1
    )
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(altered, encoding="ascii")


def load_json(path: pathlib.Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="ascii"))


def combined_metrics(summary: dict[str, Any], stimulus: str, label: str) -> dict[str, Any]:
    return summary["stimuli"][stimulus]["captures"][label]["channels"]["combined"]


def peak_delta(summary: dict[str, Any], stimulus: str) -> float:
    reference = combined_metrics(summary, stimulus, "reference")["peak_dbfs"]
    candidate = combined_metrics(summary, stimulus, "candidate")["peak_dbfs"]
    return candidate - reference


def run_ab_suite(
    script_dir: pathlib.Path,
    baseline: pathlib.Path,
    candidate: pathlib.Path,
    destination: pathlib.Path,
    pulse_server: str,
    master_limiter_threshold_db: float,
) -> dict[str, Any]:
    run(
        [
            sys.executable,
            str(script_dir / "run_jdsp_ab_testbench.py"),
            str(baseline),
            str(candidate),
            str(destination),
            "--pulse-server",
            pulse_server,
            "--master-limiter-threshold-db",
            str(master_limiter_threshold_db),
        ],
        f"real-host A/B suite for {destination.name}",
    )
    return load_json(destination / "summary.json")


def run_boundary_capture(
    script_dir: pathlib.Path,
    baseline: pathlib.Path,
    candidate: pathlib.Path,
    destination: pathlib.Path,
    pulse_server: str,
    master_limiter_threshold_db: float,
) -> dict[str, Any]:
    stimuli = destination / "stimuli"
    baseline_wav = destination / "baseline-bass_burst.wav"
    candidate_wav = destination / "candidate-bass_burst.wav"
    comparison_json = destination / "bass_burst.json"
    comparison_md = destination / "bass_burst.md"
    run(
        [sys.executable, str(script_dir / "generate_jdsp_stimuli.py"), str(stimuli), "--duration", "2.0"],
        "generate boundary stimulus",
    )
    for eel, output, label in (
        (baseline, baseline_wav, "baseline"),
        (candidate, candidate_wav, "candidate"),
    ):
        run(
            [
                sys.executable,
                str(script_dir / "render_jdsp_host.py"),
                str(stimuli / "bass_burst.wav"),
                str(eel),
                str(output),
                "--pulse-server",
                pulse_server,
                "--pre-roll-ms",
                "500",
                "--tail-ms",
                "2000",
                "--master-limiter-threshold-db",
                str(master_limiter_threshold_db),
            ],
            f"boundary {label} host render",
        )
    run(
        [
            sys.executable,
            str(script_dir / "compare_jdsp_captures.py"),
            str(baseline_wav),
            str(candidate_wav),
            "--json",
            str(comparison_json),
            "--markdown",
            str(comparison_md),
        ],
        "boundary capture comparison",
    )
    return load_json(comparison_json)


def run_program_corpus(
    script_dir: pathlib.Path,
    baseline: pathlib.Path,
    candidate: pathlib.Path,
    destination: pathlib.Path,
    pulse_server: str,
    master_limiter_threshold_db: float,
    pressure_ceiling_dbfs: float,
    default_tolerance_db: float,
) -> dict[str, Any]:
    run(
        [
            sys.executable,
            str(script_dir / "run_jdsp_program_corpus.py"),
            str(baseline),
            str(candidate),
            str(destination),
            "--pulse-server",
            pulse_server,
            "--master-limiter-threshold-db",
            str(master_limiter_threshold_db),
            "--ceiling-dbfs",
            str(pressure_ceiling_dbfs),
            "--transparency-db",
            str(default_tolerance_db),
        ],
        "default-control program-like corpus",
    )
    return load_json(destination / "summary.json")


def run_local_material(
    script_dir: pathlib.Path,
    baseline: pathlib.Path,
    candidate: pathlib.Path,
    manifest: pathlib.Path,
    destination: pathlib.Path,
    pulse_server: str,
    master_limiter_threshold_db: float,
    pressure_ceiling_dbfs: float,
    default_tolerance_db: float,
) -> dict[str, Any]:
    result = run(
        [
            sys.executable,
            str(script_dir / "run_jdsp_local_material.py"),
            str(baseline),
            str(candidate),
            str(manifest),
            str(destination),
            "--pulse-server",
            pulse_server,
            "--master-limiter-threshold-db",
            str(master_limiter_threshold_db),
            "--ceiling-dbfs",
            str(pressure_ceiling_dbfs),
            "--transparency-db",
            str(default_tolerance_db),
        ],
        "private local-material qualification",
        check=False,
    )
    report_path = destination / "summary.json"
    if not report_path.is_file():
        detail = result.stderr.strip() or result.stdout.strip() or f"exit {result.returncode}"
        raise QualificationError(f"private local-material qualification did not produce a report: {detail}")
    return load_json(report_path)


def local_material_retry_eligible(report: dict[str, Any]) -> bool:
    failed = [check for check in report["checks"] if check["status"] == "fail"]
    if not failed or not all(check["name"].startswith("local_") and check["name"].endswith("_integrity") for check in failed):
        return False
    for item in report["items"]:
        captures = item["report"]["captures"]
        reference = captures["reference"]["channels"]["combined"]
        candidate = captures["candidate"]["channels"]["combined"]
        if reference["clipped_samples"] > 0 or candidate["clipped_samples"] > 0 or candidate["silent"]:
            return False
    return True


def check_report(
    default_report: dict[str, Any],
    boosted_report: dict[str, Any],
    boundary_report: dict[str, Any],
    default_tolerance_db: float,
    boost_slider_db: float,
    boosted_tolerance_db: float,
    boundary_min_margin_db: float,
    pressure_ceiling_dbfs: float,
    expected_boost_delta_db: float | None = None,
    boundary_evaluation: str = "additional_margin",
) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []

    def record(name: str, passed: bool, detail: str) -> None:
        checks.append({"name": name, "status": "pass" if passed else "fail", "detail": detail})

    def observe(name: str, investigate: bool, detail: str) -> None:
        checks.append({"name": name, "status": "investigate" if investigate else "pass", "detail": detail})

    for stimulus in CONTINUOUS_PROBES:
        candidate = combined_metrics(default_report, stimulus, "candidate")
        delta = peak_delta(default_report, stimulus)
        record(
            f"default_{stimulus}_transparent",
            candidate["clipped_samples"] == 0 and abs(delta) <= default_tolerance_db,
            f"candidate clipping={candidate['clipped_samples']}, peak delta={delta:+.3f} dB; tolerance=+/-{default_tolerance_db:.3f} dB",
        )

    for stimulus in PRESSURE_PROBES:
        candidate = combined_metrics(default_report, stimulus, "candidate")
        peak_dbfs = candidate["peak_dbfs"]
        observe(
            f"default_{stimulus}_terminal_margin",
            peak_dbfs is not None and peak_dbfs > pressure_ceiling_dbfs,
            f"candidate peak={peak_dbfs:.3f} dBFS; investigate terminal-limiter involvement above {pressure_ceiling_dbfs:.3f} dBFS",
        )

    expected_boost_delta = (
        expected_boost_delta_db if expected_boost_delta_db is not None else -(boost_slider_db - 4.0)
    )
    for stimulus in BOOST_EXACT_PROBES:
        candidate = combined_metrics(boosted_report, stimulus, "candidate")
        delta = peak_delta(boosted_report, stimulus)
        record(
            f"boosted_{stimulus}_reserve",
            candidate["clipped_samples"] == 0 and abs(delta - expected_boost_delta) <= boosted_tolerance_db,
            f"candidate clipping={candidate['clipped_samples']}, peak delta={delta:+.3f} dB; expected={expected_boost_delta:+.3f} +/-{boosted_tolerance_db:.3f} dB",
        )

    for stimulus in PRESSURE_PROBES:
        candidate = combined_metrics(boosted_report, stimulus, "candidate")
        peak_dbfs = candidate["peak_dbfs"]
        record(
            f"boosted_{stimulus}_terminal_margin",
            candidate["clipped_samples"] == 0
            and peak_dbfs is not None
            and peak_dbfs <= pressure_ceiling_dbfs,
            f"candidate clipping={candidate['clipped_samples']}, peak={peak_dbfs:.3f} dBFS; required <= {pressure_ceiling_dbfs:.3f} dBFS",
        )

    reference = boundary_report["captures"]["reference"]["channels"]["combined"]
    candidate = boundary_report["captures"]["candidate"]["channels"]["combined"]
    if boundary_evaluation == "terminal_ceiling":
        record(
            "maximum_bass_boundary_terminal_margin",
            candidate["clipped_samples"] == 0
            and candidate["peak_dbfs"] is not None
            and candidate["peak_dbfs"] <= pressure_ceiling_dbfs,
            f"baseline peak={reference['peak_dbfs']:.3f} dBFS, candidate peak={candidate['peak_dbfs']:.3f} dBFS, "
            f"candidate clipping={candidate['clipped_samples']}; required <= {pressure_ceiling_dbfs:.3f} dBFS",
        )
    else:
        margin = reference["peak_dbfs"] - candidate["peak_dbfs"]
        record(
            "maximum_bass_boundary_margin",
            candidate["clipped_samples"] == 0 and margin >= boundary_min_margin_db,
            f"baseline peak={reference['peak_dbfs']:.3f} dBFS, candidate peak={candidate['peak_dbfs']:.3f} dBFS, added margin={margin:.3f} dB; minimum={boundary_min_margin_db:.3f} dB",
        )
    return checks


def report_status(checks: list[dict[str, Any]]) -> str:
    if any(check["status"] == "fail" for check in checks):
        return "fail"
    if any(check["status"] == "investigate" for check in checks):
        return "pass_with_investigation"
    return "pass"


def markdown_report(report: dict[str, Any]) -> str:
    lines = [
        "# Axiom WSL Real-Host Qualification",
        "",
        f"Status: **{report['status'].upper()}**",
        "",
        f"Baseline: `{report['baseline_eel']}`",
        "",
        f"Candidate: `{report['candidate_eel']}`",
        "",
        "## Checks",
        "",
        "| Check | Status | Detail |",
        "| --- | ---: | --- |",
    ]
    for check in report["checks"]:
        lines.append(f"| {check['name']} | {check['status'].upper()} | {check['detail']} |")
    lines.extend(["", "## Reports", ""])
    for label, name in (
        ("Default-control A/B", "default"),
        ("Elevated Sub Harmonics A/B", "boosted"),
        ("Maximum Sub Harmonics bass boundary", "boundary"),
        ("Original program-like corpus", "program_corpus"),
        ("Private local material", "local_material"),
    ):
        if name in report["reports"]:
            lines.append(f"- {label}: `{report['reports'][name]}`")
    lines.extend(
        [
            "",
            "Generated elevated-control EEL files are test fixtures only; the source scripts are unchanged.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("baseline_eel", type=pathlib.Path)
    parser.add_argument("candidate_eel", type=pathlib.Path)
    parser.add_argument("output_dir", type=pathlib.Path)
    parser.add_argument("--pulse-server", default=DEFAULT_PULSE_SERVER)
    parser.add_argument("--master-limiter-threshold-db", type=float, default=-1.0)
    parser.add_argument("--route-helper", type=pathlib.Path, default=DEFAULT_ROUTE_HELPER)
    parser.add_argument("--skip-route-start", action="store_true", help="use an already running JamesDSP route")
    parser.add_argument("--keep-route-running", action="store_true", help="do not restore PipeWire-Pulse when finished")
    parser.add_argument(
        "--local-material-manifest",
        type=pathlib.Path,
        help="optional private JSON excerpt manifest; source audio and paths remain outside the repository",
    )
    parser.add_argument("--boost-slider-db", type=float, default=8.0)
    parser.add_argument("--boundary-slider-db", type=float, default=12.0)
    parser.add_argument("--default-tolerance-db", type=float, default=0.15)
    parser.add_argument("--boosted-tolerance-db", type=float, default=0.10)
    parser.add_argument("--boundary-min-margin-db", type=float, default=4.0)
    parser.add_argument(
        "--expected-boost-delta-db",
        type=float,
        help="expected candidate-minus-baseline peak delta for boosted exact probes",
    )
    parser.add_argument(
        "--boundary-evaluation",
        choices=("additional_margin", "terminal_ceiling"),
        help="maximum-boost gate: require added relative margin or safe absolute output ceiling",
    )
    parser.add_argument(
        "--pressure-ceiling-dbfs",
        type=float,
        default=-0.50,
        help="default-control pressure-probe peak above this level is flagged for limiter investigation",
    )
    args = parser.parse_args()

    baseline = args.baseline_eel.resolve()
    candidate = args.candidate_eel.resolve()
    output_dir = args.output_dir.resolve()
    script_dir = pathlib.Path(__file__).resolve().parent
    for eel in (baseline, candidate):
        if not eel.is_file():
            parser.error(f"EEL script not found: {eel}")
    if args.boost_slider_db <= 4.0 or args.boundary_slider_db <= args.boost_slider_db:
        parser.error("qualification requires --boost-slider-db > 4 and --boundary-slider-db > --boost-slider-db")
    reduced_reserve_comparison = (
        baseline.name == "axiom_binaural_dsp_v4.1.4.8.eel"
        and candidate.name == "axiom_binaural_dsp_v4.1.4.9.eel"
    )
    expected_boost_delta_db = args.expected_boost_delta_db
    boundary_evaluation = args.boundary_evaluation
    if reduced_reserve_comparison:
        if expected_boost_delta_db is None:
            expected_boost_delta_db = (args.boost_slider_db - 4.0) * 0.25
        if boundary_evaluation is None:
            boundary_evaluation = "terminal_ceiling"
    if boundary_evaluation is None:
        boundary_evaluation = "additional_margin"
    output_dir.mkdir(parents=True, exist_ok=True)
    fixtures = output_dir / "fixtures"
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
        boosted_baseline = fixtures / f"{baseline.stem}_sub_plus{args.boost_slider_db:g}.eel"
        boosted_candidate = fixtures / f"{candidate.stem}_sub_plus{args.boost_slider_db:g}.eel"
        boundary_baseline = fixtures / f"{baseline.stem}_sub_plus{args.boundary_slider_db:g}.eel"
        boundary_candidate = fixtures / f"{candidate.stem}_sub_plus{args.boundary_slider_db:g}.eel"
        slider_fixture(baseline, boosted_baseline, args.boost_slider_db)
        slider_fixture(candidate, boosted_candidate, args.boost_slider_db)
        slider_fixture(baseline, boundary_baseline, args.boundary_slider_db)
        slider_fixture(candidate, boundary_candidate, args.boundary_slider_db)
        default_report = run_ab_suite(
            script_dir, baseline, candidate, output_dir / "default", args.pulse_server, args.master_limiter_threshold_db
        )
        boosted_report = run_ab_suite(
            script_dir,
            boosted_baseline,
            boosted_candidate,
            output_dir / "boosted",
            args.pulse_server,
            args.master_limiter_threshold_db,
        )
        boundary_report = run_boundary_capture(
            script_dir,
            boundary_baseline,
            boundary_candidate,
            output_dir / "boundary",
            args.pulse_server,
            args.master_limiter_threshold_db,
        )
        program_report = run_program_corpus(
            script_dir,
            baseline,
            candidate,
            output_dir / "program_corpus",
            args.pulse_server,
            args.master_limiter_threshold_db,
            args.pressure_ceiling_dbfs,
            args.default_tolerance_db,
        )
        local_report = None
        local_report_path = None
        initial_local_report_path = None
        if args.local_material_manifest:
            local_report_path = output_dir / "local_material/summary.md"
            local_report = run_local_material(
                script_dir,
                baseline,
                candidate,
                args.local_material_manifest.resolve(),
                output_dir / "local_material",
                args.pulse_server,
                args.master_limiter_threshold_db,
                args.pressure_ceiling_dbfs,
                args.default_tolerance_db,
            )
            if local_material_retry_eligible(local_report):
                initial_local_report_path = local_report_path
                retry_destination = output_dir / "local_material_retry"
                retry_report = run_local_material(
                    script_dir,
                    baseline,
                    candidate,
                    args.local_material_manifest.resolve(),
                    retry_destination,
                    args.pulse_server,
                    args.master_limiter_threshold_db,
                    args.pressure_ceiling_dbfs,
                    args.default_tolerance_db,
                )
                local_report = retry_report
                local_report_path = retry_destination / "summary.md"
                if retry_report["status"] != "fail":
                    local_report["checks"].append(
                        {
                            "name": "local_material_initial_capture_instability",
                            "status": "investigate",
                            "detail": "initial integrity-only failure with no clipping cleared on one fresh host rerun",
                        }
                    )
        checks = check_report(
            default_report,
            boosted_report,
            boundary_report,
            args.default_tolerance_db,
            args.boost_slider_db,
            args.boosted_tolerance_db,
            args.boundary_min_margin_db,
            args.pressure_ceiling_dbfs,
            expected_boost_delta_db,
            boundary_evaluation,
        )
        checks.extend(program_report["checks"])
        if local_report:
            checks.extend(local_report["checks"])
        reports = {
            "default": str(output_dir / "default/summary.md"),
            "boosted": str(output_dir / "boosted/summary.md"),
            "boundary": str(output_dir / "boundary/bass_burst.md"),
            "program_corpus": str(output_dir / "program_corpus/summary.md"),
        }
        if local_report:
            reports["local_material"] = str(local_report_path)
        if initial_local_report_path:
            reports["local_material_initial_attempt"] = str(initial_local_report_path)
        report = {
            "status": report_status(checks),
            "baseline_eel": str(baseline),
            "candidate_eel": str(candidate),
            "pulse_server": args.pulse_server,
            "configuration": {
                "default_sub_harmonics_db": 4.0,
                "boost_slider_db": args.boost_slider_db,
                "boundary_slider_db": args.boundary_slider_db,
                "default_tolerance_db": args.default_tolerance_db,
                "boosted_tolerance_db": args.boosted_tolerance_db,
                "boundary_min_margin_db": args.boundary_min_margin_db,
                "expected_boost_delta_db": expected_boost_delta_db,
                "boundary_evaluation": boundary_evaluation,
                "pressure_ceiling_dbfs": args.pressure_ceiling_dbfs,
                "master_limiter_threshold_db": args.master_limiter_threshold_db,
            },
            "checks": checks,
            "reports": reports,
        }
        (output_dir / "qualification.json").write_text(json.dumps(report, indent=2) + "\n", encoding="ascii")
        (output_dir / "qualification.md").write_text(markdown_report(report), encoding="ascii")
        print(output_dir / "qualification.json")
        print(output_dir / "qualification.md")
        return 1 if report["status"] == "fail" else 0
    finally:
        if restored_master_threshold is not None:
            try:
                set_jdsp_setting("master_limthreshold", restored_master_threshold)
            except QualificationError as exc:
                print(f"warning: {exc}", file=sys.stderr)
        if route_started and not args.keep_route_running:
            cleanup_errors = stop_managed_route(args.pulse_server)
            for error in cleanup_errors:
                print(f"warning: {error}", file=sys.stderr)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except QualificationError as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1)
