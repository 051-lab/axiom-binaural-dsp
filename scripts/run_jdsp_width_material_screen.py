#!/usr/bin/env python3
"""Characterize accepted Axiom stereo width on registered program material through real JDSP."""

from __future__ import annotations

import argparse
import json
import math
import pathlib
import sys
from typing import Any

import analyze_jdsp_transfer as transfer
from run_jdsp_local_material import MaterialError, convert_excerpt, read_manifest
from run_jdsp_width_mono_audit import unity_width_fixture
from run_jdsp_wsl_qualification import (
    DEFAULT_PULSE_SERVER,
    DEFAULT_ROUTE_HELPER,
    QualificationError,
    run,
    stop_managed_route,
    validate_route,
)


BANDS_HZ = (
    ("deep_bass", 20.0, 70.0),
    ("upper_bass", 70.0, 150.0),
    ("low_mid", 150.0, 4000.0),
    ("high", 4000.0, 18000.0),
)


def coefficients(filter_type: str, frequency: float, sample_rate: int, q_factor: float = 0.7071) -> tuple[float, ...]:
    safe_frequency = min(max(frequency, 5.0), sample_rate * 0.45)
    x = safe_frequency * 2.0 * math.pi / sample_rate
    sin_x = math.sin(x)
    cos_x = math.cos(x)
    alpha = sin_x / (q_factor * 2.0)
    a0 = 1.0 + alpha
    a1 = -2.0 * cos_x
    a2 = 1.0 - alpha
    if filter_type == "lowpass":
        b0 = (1.0 - cos_x) / 2.0
        b1 = 1.0 - cos_x
        b2 = (1.0 - cos_x) / 2.0
    elif filter_type == "highpass":
        b0 = (1.0 + cos_x) / 2.0
        b1 = -(1.0 + cos_x)
        b2 = (1.0 + cos_x) / 2.0
    else:
        raise ValueError(f"unknown filter type: {filter_type}")
    return b0 / a0, b1 / a0, b2 / a0, -a1 / a0, -a2 / a0


def filter_samples(samples: list[float], values: tuple[float, ...]) -> list[float]:
    b0, b1, b2, a1, a2 = values
    x1 = x2 = y1 = y2 = 0.0
    output = []
    for sample in samples:
        value = sample * b0 + x1 * b1 + x2 * b2 + y1 * a1 + y2 * a2
        x2, x1 = x1, sample
        y2, y1 = y1, value
        output.append(value)
    return output


def cascaded(samples: list[float], values: tuple[float, ...]) -> list[float]:
    return filter_samples(filter_samples(samples, values), values)


def rms(samples: list[float]) -> float:
    return math.sqrt(sum(value * value for value in samples) / len(samples)) if samples else 0.0


def ratio_db(numerator: float, denominator: float) -> float | None:
    return 20.0 * math.log10(numerator / denominator) if numerator > 0.0 and denominator > 0.0 else None


def band_metrics(
    wav: transfer.StereoWav,
    bands: tuple[tuple[str, float, float], ...] = BANDS_HZ,
) -> dict[str, dict[str, float | None]]:
    mid = [(left + right) * 0.5 for left, right in zip(wav.left, wav.right)]
    side = [(left - right) * 0.5 for left, right in zip(wav.left, wav.right)]
    result: dict[str, dict[str, float | None]] = {}
    for name, low, high in bands:
        hp = coefficients("highpass", low, wav.sample_rate)
        lp = coefficients("lowpass", high, wav.sample_rate)
        filtered_mid = cascaded(cascaded(mid, hp), lp)
        filtered_side = cascaded(cascaded(side, hp), lp)
        mid_rms = rms(filtered_mid)
        side_rms = rms(filtered_side)
        result[name] = {
            "low_hz": low,
            "high_hz": high,
            "mid_rms": mid_rms,
            "side_rms": side_rms,
            "side_to_mid_db": ratio_db(side_rms, mid_rms),
        }
    return result


def delta(candidate: float | None, baseline: float | None) -> float | None:
    return None if candidate is None or baseline is None else candidate - baseline


def analyze_item(
    item: dict[str, Any],
    input_wav: pathlib.Path,
    unity_wav: pathlib.Path,
    accepted_wav: pathlib.Path,
) -> dict[str, Any]:
    source = transfer.read_stereo_wav(input_wav)
    unity = transfer.read_stereo_wav(unity_wav)
    accepted = transfer.read_stereo_wav(accepted_wav)
    source_bands = band_metrics(source)
    unity_bands = band_metrics(unity)
    accepted_bands = band_metrics(accepted)
    bands = {}
    for name, _low, _high in BANDS_HZ:
        bands[name] = {
            "source": source_bands[name],
            "unity_width": unity_bands[name],
            "accepted_width": accepted_bands[name],
            "accepted_minus_unity_side_to_mid_db": delta(
                accepted_bands[name]["side_to_mid_db"], unity_bands[name]["side_to_mid_db"]
            ),
            "accepted_minus_source_side_to_mid_db": delta(
                accepted_bands[name]["side_to_mid_db"], source_bands[name]["side_to_mid_db"]
            ),
        }
    return {
        "label": item["label"],
        "name": item["name"],
        "start_seconds": item["start_seconds"],
        "duration_seconds": item["duration_seconds"],
        "levels": {
            "unity_width": transfer.level_metrics(unity),
            "accepted_width": transfer.level_metrics(accepted),
        },
        "bands": bands,
    }


def evaluate_items(items: list[dict[str, Any]], ceiling_dbfs: float) -> dict[str, Any]:
    checks = []
    for item in items:
        for mode in ("unity_width", "accepted_width"):
            level = item["levels"][mode]
            if level["clipped_samples"] > 0:
                status = "fail"
                detail = f"{level['clipped_samples']} clipped channel samples"
            elif level["peak_dbfs"] is None:
                status = "fail"
                detail = "silent output"
            elif level["peak_dbfs"] > ceiling_dbfs:
                status = "investigate"
                detail = f"peak={level['peak_dbfs']:.3f} dBFS exceeds observation level {ceiling_dbfs:.3f} dBFS"
            else:
                status = "pass"
                detail = f"peak={level['peak_dbfs']:.3f} dBFS, clipping=0"
            checks.append({"name": f"{item['name']}_{mode}_integrity", "status": status, "detail": detail})
    status = "fail" if any(check["status"] == "fail" for check in checks) else (
        "measurement_complete_with_investigation"
        if any(check["status"] == "investigate" for check in checks)
        else "measurement_complete"
    )
    return {"status": status, "checks": checks}


def display(value: float | None) -> str:
    return "-" if value is None else f"{value:.3f}"


def markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Axiom Width Material Screen",
        "",
        f"Status: **{report['evaluation']['status'].upper()}**",
        "",
        "This report characterizes spatial balance in registered local material through real JDSP. "
        "The accepted `.9` source is unchanged; the comparison fixture sets all width controls to `100%`.",
        "",
        "Band values are output side-to-mid RMS ratios. Positive accepted-minus-unity values indicate "
        "that accepted width increases side emphasis in that band; they are preference evidence, not defects.",
        "",
        "| Material | Band | Source S/M (dB) | Unity S/M (dB) | Accepted S/M (dB) | Accepted - unity (dB) |",
        "| --- | --- | ---: | ---: | ---: | ---: |",
    ]
    for item in report["items"]:
        label = item["label"].replace("|", "\\|")
        for name, _low, _high in BANDS_HZ:
            band = item["bands"][name]
            lines.append(
                f"| {label} | {name.replace('_', ' ')} | "
                f"{display(band['source']['side_to_mid_db'])} | "
                f"{display(band['unity_width']['side_to_mid_db'])} | "
                f"{display(band['accepted_width']['side_to_mid_db'])} | "
                f"{display(band['accepted_minus_unity_side_to_mid_db'])} |"
            )
    lines.extend(
        [
            "",
            "## Integrity Checks",
            "",
            "| Check | Status | Detail |",
            "| --- | --- | --- |",
        ]
    )
    lines.extend(
        f"| {check['name']} | {check['status'].upper()} | {check['detail']} |"
        for check in report["evaluation"]["checks"]
    )
    lines.extend(
        [
            "",
            "Interpretation boundary: symmetrical side widening does not alter the output mono sum. "
            "A low-bass S/M increase can affect stereo bass placement and the contrast between stereo "
            "and mono playback, but is not by itself a mono-sum failure.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("accepted_eel", type=pathlib.Path)
    parser.add_argument("manifest", type=pathlib.Path)
    parser.add_argument("output_dir", type=pathlib.Path)
    parser.add_argument("--pulse-server", default=DEFAULT_PULSE_SERVER)
    parser.add_argument("--route-helper", type=pathlib.Path, default=DEFAULT_ROUTE_HELPER)
    parser.add_argument("--master-limiter-threshold-db", type=float, default=-1.0)
    parser.add_argument("--ceiling-dbfs", type=float, default=-0.50)
    parser.add_argument("--skip-route-start", action="store_true")
    parser.add_argument("--keep-route-running", action="store_true")
    args = parser.parse_args()

    accepted = args.accepted_eel.resolve()
    if not accepted.is_file():
        parser.error(f"EEL script not found: {accepted}")
    items = read_manifest(args.manifest.resolve())
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    fixture = output_dir / "fixtures" / f"{accepted.stem}_unity_width.eel"
    unity_width_fixture(accepted, fixture)

    route_started = False
    try:
        if not args.skip_route_start:
            if not args.route_helper.is_file():
                raise QualificationError(f"route helper not found: {args.route_helper}")
            run([str(args.route_helper)], "start managed JamesDSP WSL audio route")
            route_started = True
        validate_route(args.pulse_server)
        script_dir = pathlib.Path(__file__).resolve().parent
        reports = []
        for item in items:
            excerpt = output_dir / "excerpts" / f"{item['name']}.wav"
            unity_output = output_dir / "unity_width" / f"{item['name']}.wav"
            accepted_output = output_dir / "accepted_width" / f"{item['name']}.wav"
            convert_excerpt(item, excerpt)
            for eel, output, label in (
                (fixture, unity_output, "unity width"),
                (accepted, accepted_output, "accepted width"),
            ):
                run(
                    [
                        sys.executable,
                        str(script_dir / "render_jdsp_host.py"),
                        str(excerpt),
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
            reports.append(analyze_item(item, excerpt, unity_output, accepted_output))
        report = {
            "scope": "registered local material width balance through real JDSP",
            "accepted_eel": str(accepted),
            "manifest": str(args.manifest.resolve()),
            "fixtures": {"unity_width": str(fixture)},
            "master_limiter_threshold_db": args.master_limiter_threshold_db,
            "ceiling_dbfs": args.ceiling_dbfs,
            "bands_hz": BANDS_HZ,
            "items": reports,
        }
        report["evaluation"] = evaluate_items(reports, args.ceiling_dbfs)
        (output_dir / "width_material_screen.json").write_text(
            json.dumps(report, indent=2) + "\n", encoding="utf-8"
        )
        (output_dir / "width_material_screen.md").write_text(markdown(report), encoding="utf-8")
        print(output_dir / "width_material_screen.json")
        print(output_dir / "width_material_screen.md")
        print(f"status={report['evaluation']['status']}")
        return 1 if report["evaluation"]["status"] == "fail" else 0
    finally:
        if route_started and not args.keep_route_running:
            for error in stop_managed_route(args.pulse_server):
                print(f"warning: {error}", file=sys.stderr)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (MaterialError, QualificationError, transfer.AnalysisError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1)
