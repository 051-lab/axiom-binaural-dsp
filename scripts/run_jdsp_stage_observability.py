#!/usr/bin/env python3
"""Measure Axiom stage taps with same-render diagnostic channel pairing."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import math
import pathlib
import sys
from typing import Any

from compare_jdsp_captures import analyze_capture, dbfs, read_capture, signal_metrics
from render_jdsp_host import NEUTRAL_SETTINGS
from run_jdsp_width_material_screen import cascaded, coefficients, rms
from run_jdsp_wsl_qualification import (
    DEFAULT_PULSE_SERVER,
    DEFAULT_ROUTE_HELPER,
    QualificationError,
    run,
    stop_managed_route,
    validate_route,
)


ACCEPTED_V410_SHA256 = "2b72288048f3e6a180eb5a0e3d951f34fc463d113bb8d716c03cfda8aeafffc5"
INIT_OUTPUT_GAIN_LINE = "outputGain = headroomGain;\n"
SPATIAL_RECOMBINE_BLOCK = "out_L = low_mono + m_l + h_l;\nout_R = low_mono + m_r + h_r;"
BASS_INJECTION_BLOCK = "out_L += harm_l * subGainLin;\nout_R += harm_r * subGainLin;"
OUTPUT_GAIN_LINE = (
    "outputGain = (slider1 > 4.0) ? "
    "(headroomGain * exp(-((slider1 - 4.0) * 0.75) * DB_2_LOG)) : headroomGain;"
)
FINAL_STAGE_HEADER = """// ==========================================
// FINAL OUTPUT ASSIGNMENT
// ==========================================
"""
FINAL_OUTPUT_BLOCK = (
    FINAL_STAGE_HEADER
    + "// Preserve the v4.1.4.7 default sound; elevated bass gain uses the qualified reduced reserve slope.\n"
    + OUTPUT_GAIN_LINE + "\n"
    + "out_L *= outputGain;\n"
    + "out_R *= outputGain;\n"
    + "spl0 = out_L;\n"
    + "spl1 = out_R;\n"
)
BASS_RESERVE_STIMULI = ("bass_burst", "bass_pressure_90hz", "correlated_mono")
AVAILABLE_STIMULI = ("impulse", "bass_burst", "bass_pressure_90hz", "sweep", "correlated_mono", "side_only")
BANDS_HZ = (
    ("low_bass", 20.0, 70.0),
    ("upper_bass", 70.0, 150.0),
    ("low_mid", 150.0, 4000.0),
    ("presence", 2000.0, 6000.0),
    ("brilliance", 6000.0, 12000.0),
    ("air", 12000.0, 18000.0),
)
PAIRINGS = {
    "spatial_to_bass": {
        "reference_tap": "spatial_out",
        "candidate_tap": "bass_post",
        "description": "left = post-spatial mono path, right = post-bass-injection mono path",
    },
    "reserve_pre_to_post": {
        "reference_tap": "reserve_pre",
        "candidate_tap": "reserve_post",
        "description": "left = post-STFT mono before terminal reserve, right = same path after reserve",
    },
}


def sha256_file(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def require_once(text: str, needle: str, label: str, source: pathlib.Path) -> None:
    if text.count(needle) != 1:
        raise QualificationError(f"cannot create stage-observability fixture from {source}: {label} missing or duplicated")


def add_diagnostic_init(text: str, source: pathlib.Path) -> str:
    require_once(text, INIT_OUTPUT_GAIN_LINE, "@init outputGain signature", source)
    return text.replace(
        INIT_OUTPUT_GAIN_LINE,
        INIT_OUTPUT_GAIN_LINE + "axiomDiagRef = 0.0;\naxiomDiagCand = 0.0;\n",
        1,
    )


def stage_observability_fixture(source: pathlib.Path, destination: pathlib.Path, pairing: str) -> None:
    text = source.read_text(encoding="ascii")
    if pairing not in PAIRINGS:
        raise QualificationError(f"unknown stage-observability pairing: {pairing}")
    for needle, label in (
        (SPATIAL_RECOMBINE_BLOCK, "spatial recombine block"),
        (BASS_INJECTION_BLOCK, "bass injection block"),
        (FINAL_STAGE_HEADER, "final output marker"),
        (OUTPUT_GAIN_LINE, "accepted reserve law"),
    ):
        require_once(text, needle, label, source)
    altered = add_diagnostic_init(text, source)
    if pairing == "spatial_to_bass":
        altered = altered.replace(
            SPATIAL_RECOMBINE_BLOCK,
            SPATIAL_RECOMBINE_BLOCK + "\naxiomDiagRef = (out_L + out_R) * 0.5;",
            1,
        )
        altered = altered.replace(
            BASS_INJECTION_BLOCK,
            BASS_INJECTION_BLOCK + "\naxiomDiagCand = (out_L + out_R) * 0.5;",
            1,
        )
        altered = altered.replace(
            FINAL_STAGE_HEADER,
            "// Diagnostic fixture only: output spatial_out on left and bass_post on right.\n"
            "out_L = axiomDiagRef;\n"
            "out_R = axiomDiagCand;\n\n"
            + FINAL_STAGE_HEADER,
            1,
        )
    elif pairing == "reserve_pre_to_post":
        require_once(altered, FINAL_OUTPUT_BLOCK, "final output block", source)
        altered = altered.replace(
            FINAL_OUTPUT_BLOCK,
            FINAL_STAGE_HEADER
            + "// Diagnostic fixture only: output reserve_pre on left and reserve_post on right.\n"
            + OUTPUT_GAIN_LINE + "\n"
            + "axiomDiagRef = (out_L + out_R) * 0.5;\n"
            + "axiomDiagCand = axiomDiagRef * outputGain;\n"
            + "out_L = axiomDiagRef;\n"
            + "out_R = axiomDiagCand;\n"
            + "spl0 = out_L;\n"
            + "spl1 = out_R;\n",
            1,
        )
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(altered, encoding="ascii")


def percentile(values: list[float], quantile: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    position = (len(ordered) - 1) * quantile
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    weight = position - lower
    return ordered[lower] * (1.0 - weight) + ordered[upper] * weight


def dbfs_optional(value: float | None) -> float | None:
    return dbfs(value) if value is not None else None


def window_envelope(values: list[float], sample_rate: int, window_ms: float = 20.0) -> dict[str, float | None]:
    window_frames = max(1, round(sample_rate * window_ms / 1000.0))
    levels: list[float] = []
    for start in range(0, len(values), window_frames):
        chunk = values[start:start + window_frames]
        if chunk:
            levels.append(math.sqrt(sum(value * value for value in chunk) / len(chunk)))
    peak = max(levels, default=0.0)
    p95 = percentile(levels, 0.95)
    p99 = percentile(levels, 0.99)
    return {
        "window_ms": window_ms,
        "peak_rms": peak,
        "peak_rms_dbfs": dbfs(peak),
        "p95_rms": p95,
        "p95_rms_dbfs": dbfs_optional(p95),
        "p99_rms": p99,
        "p99_rms_dbfs": dbfs_optional(p99),
    }


def band_energy(values: list[float], sample_rate: int) -> dict[str, dict[str, float | None]]:
    result: dict[str, dict[str, float | None]] = {}
    for name, low, high in BANDS_HZ:
        highpass = coefficients("highpass", low, sample_rate)
        lowpass = coefficients("lowpass", high, sample_rate)
        filtered = cascaded(cascaded(values, highpass), lowpass)
        band_rms = rms(filtered)
        result[name] = {
            "low_hz": low,
            "high_hz": high,
            "rms": band_rms,
            "rms_dbfs": dbfs(band_rms),
        }
    return result


def diagnostic_channel_metrics(
    values: list[float],
    sample_rate: int,
    clip_level: float,
    silence_dbfs: float,
) -> dict[str, Any]:
    silence_level = 10.0 ** (silence_dbfs / 20.0)
    metrics = signal_metrics(values, clip_level, silence_level)
    return {
        **metrics,
        "window_20ms": window_envelope(values, sample_rate, 20.0),
        "bands": band_energy(values, sample_rate),
    }


def delta(candidate: float | None, reference: float | None) -> float | None:
    return candidate - reference if candidate is not None and reference is not None else None


def stage_delta(candidate: dict[str, Any], reference: dict[str, Any]) -> dict[str, Any]:
    return {
        "candidate_minus_reference": {
            "peak_db": delta(candidate["peak_dbfs"], reference["peak_dbfs"]),
            "rms_db": delta(candidate["rms_dbfs"], reference["rms_dbfs"]),
            "crest_db": delta(candidate["crest_db"], reference["crest_db"]),
            "window_20ms_peak_rms_db": delta(
                candidate["window_20ms"]["peak_rms_dbfs"], reference["window_20ms"]["peak_rms_dbfs"]
            ),
            "window_20ms_p95_rms_db": delta(
                candidate["window_20ms"]["p95_rms_dbfs"], reference["window_20ms"]["p95_rms_dbfs"]
            ),
        },
        "band_rms_candidate_minus_reference_db": {
            name: delta(candidate["bands"][name]["rms_dbfs"], reference["bands"][name]["rms_dbfs"])
            for name, _low, _high in BANDS_HZ
        },
    }


def diagnostic_capture_metrics(capture: Any, silence_dbfs: float = -90.0) -> dict[str, Any]:
    reference = diagnostic_channel_metrics(capture.left, capture.sample_rate, capture.clip_level, silence_dbfs)
    candidate = diagnostic_channel_metrics(capture.right, capture.sample_rate, capture.clip_level, silence_dbfs)
    return {
        "capture_integrity": capture.integrity,
        "diagnostic_channel_semantics": {
            "left": "reference_tap",
            "right": "candidate_tap",
            "mid_side_note": "mid/side metrics describe the diagnostic pair, not the production stereo image",
        },
        "reference": reference,
        "candidate": candidate,
        "mid_side": analyze_capture(capture, silence_dbfs)["mid_side"],
        "stage_delta": stage_delta(candidate, reference),
    }


def evaluate_pairings(pairings: dict[str, Any], ceiling_dbfs: float) -> dict[str, Any]:
    checks: list[dict[str, str]] = []
    for pairing_name, pairing in pairings.items():
        for stimulus_name, item in pairing["stimuli"].items():
            for side in ("reference", "candidate"):
                metrics = item["metrics"][side]
                failures: list[str] = []
                if metrics["silent"]:
                    failures.append("silent")
                if metrics["clipped_samples"]:
                    failures.append(f"{metrics['clipped_samples']} clipped samples")
                if failures:
                    status = "fail"
                    detail = "; ".join(failures)
                elif metrics["peak_dbfs"] is not None and metrics["peak_dbfs"] > ceiling_dbfs:
                    status = "investigate"
                    detail = f"peak={metrics['peak_dbfs']:.3f} dBFS exceeds observation level {ceiling_dbfs:.3f} dBFS"
                else:
                    status = "pass"
                    detail = f"peak={format_value(metrics['peak_dbfs'])} dBFS, clipping=0"
                checks.append({
                    "name": f"{pairing_name}_{stimulus_name}_{side}_integrity",
                    "status": status,
                    "detail": detail,
                })
    status = "fail" if any(check["status"] == "fail" for check in checks) else (
        "measurement_complete_with_investigation"
        if any(check["status"] == "investigate" for check in checks)
        else "measurement_complete"
    )
    return {"status": status, "checks": checks}


def format_value(value: float | None) -> str:
    return "-" if value is None else f"{value:.3f}"


def run_pairing(
    script_dir: pathlib.Path,
    fixture: pathlib.Path,
    stimuli_dir: pathlib.Path,
    output_dir: pathlib.Path,
    stimuli: tuple[str, ...],
    pulse_server: str,
    limiter_threshold_db: float,
    silence_dbfs: float,
) -> dict[str, Any]:
    reports: dict[str, Any] = {}
    for stimulus in stimuli:
        capture_path = output_dir / "capture" / f"{stimulus}.wav"
        run(
            [
                sys.executable,
                str(script_dir / "render_jdsp_host.py"),
                str(stimuli_dir / f"{stimulus}.wav"),
                str(fixture),
                str(capture_path),
                "--pulse-server",
                pulse_server,
                "--pre-roll-ms",
                "500",
                "--tail-ms",
                "2000",
                "--master-limiter-threshold-db",
                str(limiter_threshold_db),
            ],
            f"stage observability {output_dir.name} {stimulus} host render",
        )
        capture, integrity = read_capture(capture_path)
        if not capture:
            raise QualificationError(f"invalid stage-observability capture for {stimulus}: {integrity}")
        reports[stimulus] = {
            "capture": str(capture_path),
            "metrics": diagnostic_capture_metrics(capture, silence_dbfs),
        }
    return reports


def markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Axiom Stage Observability",
        "",
        f"Status: **{report['evaluation']['status'].upper()}**",
        "",
        "This is diagnostic host-path evidence. Temporary EEL fixtures route one internal reference tap to the left output channel and one processed tap to the right output channel in the same render. The accepted source script is unchanged.",
        "",
        f"Accepted script: `{report['accepted_eel']}`",
        f"Accepted SHA-256: `{report['accepted_sha256']}`",
        f"Mode: `{report['mode']}`",
        f"Host limiter threshold: `{report['host_policy']['master_limthreshold']} dB`; release: `{report['host_policy']['master_limrelease']} ms`; postgain: `{report['host_policy']['master_postgain']} dB`; crossfeed: `{report['host_policy']['crossfeed_enable']}`.",
        "",
        "| Pairing | Stimulus | Reference tap | Candidate tap | Ref peak (dBFS) | Cand peak (dBFS) | Ref RMS (dBFS) | Cand RMS (dBFS) | Cand - ref RMS (dB) | Low-bass delta (dB) | Upper-bass delta (dB) | Clipped samples |",
        "| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for pairing_name, pairing in report["pairings"].items():
        for stimulus, item in pairing["stimuli"].items():
            metrics = item["metrics"]
            reference = metrics["reference"]
            candidate = metrics["candidate"]
            stage = metrics["stage_delta"]
            bands = stage["band_rms_candidate_minus_reference_db"]
            clipped = reference["clipped_samples"] + candidate["clipped_samples"]
            lines.append(
                f"| {pairing_name} | {stimulus} | {pairing['reference_tap']} | {pairing['candidate_tap']} | "
                f"{format_value(reference['peak_dbfs'])} | {format_value(candidate['peak_dbfs'])} | "
                f"{format_value(reference['rms_dbfs'])} | {format_value(candidate['rms_dbfs'])} | "
                f"{format_value(stage['candidate_minus_reference']['rms_db'])} | "
                f"{format_value(bands['low_bass'])} | {format_value(bands['upper_bass'])} | {clipped} |"
            )
    lines.extend(["", "## Integrity Checks", "", "| Check | Status | Detail |", "| --- | --- | --- |"])
    lines.extend(
        f"| {check['name']} | {check['status'].upper()} | {check['detail']} |"
        for check in report["evaluation"]["checks"]
    )
    lines.extend(
        [
            "",
            "Interpretation boundary: this is a tap-level diagnostic, not a production stereo render. "
            "Use it to locate where bass weight, reserve, and host-limiter pressure appear before proposing a sound-changing candidate.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("accepted_eel", type=pathlib.Path)
    parser.add_argument("output_dir", type=pathlib.Path)
    parser.add_argument("--mode", choices=("bass_reserve",), default="bass_reserve")
    parser.add_argument("--pulse-server", default=DEFAULT_PULSE_SERVER)
    parser.add_argument("--route-helper", type=pathlib.Path, default=DEFAULT_ROUTE_HELPER)
    parser.add_argument("--master-limiter-threshold-db", type=float, default=-1.0)
    parser.add_argument("--ceiling-dbfs", type=float, default=-0.50)
    parser.add_argument("--silence-dbfs", type=float, default=-90.0)
    parser.add_argument("--stimulus", choices=AVAILABLE_STIMULI, action="append", dest="stimuli")
    parser.add_argument("--skip-route-start", action="store_true")
    parser.add_argument("--keep-route-running", action="store_true")
    parser.add_argument("--allow-non-accepted-hash", action="store_true")
    args = parser.parse_args()

    accepted = args.accepted_eel.resolve()
    output_dir = args.output_dir.resolve()
    script_dir = pathlib.Path(__file__).resolve().parent
    if not accepted.is_file():
        parser.error(f"EEL script not found: {accepted}")
    accepted_sha256 = sha256_file(accepted)
    if accepted_sha256 != ACCEPTED_V410_SHA256 and not args.allow_non_accepted_hash:
        parser.error(
            f"{accepted} is not the accepted v4.1.4.10 baseline; "
            "pass --allow-non-accepted-hash only for tool development"
        )
    if not -30.0 <= args.master_limiter_threshold_db <= 0.0:
        parser.error("--master-limiter-threshold-db must be in [-30, 0] dB")
    if args.ceiling_dbfs > 0.0:
        parser.error("--ceiling-dbfs must be <= 0 dBFS")
    stimuli = tuple(args.stimuli or BASS_RESERVE_STIMULI)
    output_dir.mkdir(parents=True, exist_ok=True)
    run(
        [sys.executable, str(script_dir / "generate_jdsp_stimuli.py"), str(output_dir / "stimuli")],
        "stage observability stimulus generation",
    )
    fixture_dir = output_dir / "fixtures"
    fixtures: dict[str, pathlib.Path] = {}
    for pairing in PAIRINGS:
        fixture = fixture_dir / f"{accepted.stem}_{pairing}.eel"
        stage_observability_fixture(accepted, fixture, pairing)
        run([str(script_dir / "validate_axiom_static.sh"), str(fixture)], f"{pairing} fixture static validation")
        fixtures[pairing] = fixture

    route_started = False
    try:
        if not args.skip_route_start:
            if not args.route_helper.is_file():
                raise QualificationError(f"route helper not found: {args.route_helper}")
            run([str(args.route_helper)], "start managed JamesDSP WSL audio route")
            route_started = True
        validate_route(args.pulse_server)
        pairings: dict[str, Any] = {}
        for pairing, fixture in fixtures.items():
            pairings[pairing] = {
                **PAIRINGS[pairing],
                "fixture": str(fixture),
                "fixture_sha256": sha256_file(fixture),
                "stimuli": run_pairing(
                    script_dir,
                    fixture,
                    output_dir / "stimuli",
                    output_dir / pairing,
                    stimuli,
                    args.pulse_server,
                    args.master_limiter_threshold_db,
                    args.silence_dbfs,
                ),
            }
        host_policy = dict(NEUTRAL_SETTINGS)
        host_policy["master_limthreshold"] = f"{args.master_limiter_threshold_db:g}"
        report = {
            "generated_at": dt.datetime.now(tz=dt.timezone.utc).isoformat(),
            "scope": "same-render diagnostic tap pairing through JDSP",
            "mode": args.mode,
            "accepted_eel": str(accepted),
            "accepted_sha256": accepted_sha256,
            "host_policy": host_policy,
            "ceiling_dbfs": args.ceiling_dbfs,
            "silence_dbfs": args.silence_dbfs,
            "stimuli": stimuli,
            "bands_hz": BANDS_HZ,
            "pairings": pairings,
        }
        report["evaluation"] = evaluate_pairings(pairings, args.ceiling_dbfs)
        (output_dir / "stage_observability.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        (output_dir / "stage_observability.md").write_text(markdown(report), encoding="utf-8")
        print(output_dir / "stage_observability.json")
        print(output_dir / "stage_observability.md")
        print(f"status={report['evaluation']['status']}")
        return 1 if report["evaluation"]["status"] == "fail" else 0
    finally:
        if route_started and not args.keep_route_running:
            for error in stop_managed_route(args.pulse_server):
                print(f"warning: {error}", file=sys.stderr)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except QualificationError as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1)
