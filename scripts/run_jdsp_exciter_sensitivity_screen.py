#!/usr/bin/env python3
"""Screen dynamic exciter sensitivity settings on registered material through real JDSP."""

from __future__ import annotations

import argparse
import json
import math
import pathlib
import sys
from typing import Any

import analyze_jdsp_transfer as transfer
from run_jdsp_local_material import MaterialError, convert_excerpt, read_manifest
from run_jdsp_width_material_screen import cascaded, coefficients, delta, display, ratio_db, rms
from run_jdsp_wsl_qualification import (
    DEFAULT_PULSE_SERVER,
    DEFAULT_ROUTE_HELPER,
    QualificationError,
    run,
    stop_managed_route,
    validate_route,
)


SETTINGS = (
    ("accepted_50", 50.0, "accepted"),
    ("reduced_35", 35.0, "reduced"),
    ("bypass_0", 0.0, "bypass"),
)
EXCITER_BANDS_HZ = (
    ("presence_edge", 4000.0, 7000.0),
    ("brilliance", 7000.0, 12000.0),
    ("air", 12000.0, 18000.0),
)


def exciter_fixture(source: pathlib.Path, destination: pathlib.Path, sensitivity_percent: float) -> None:
    text = source.read_text(encoding="ascii")
    slider_signature = "slider3:50<"
    init_signature = "slider3 = 50;"
    if text.count(slider_signature) != 1 or text.count(init_signature) != 1:
        raise QualificationError(
            f"cannot make exciter sensitivity fixture from {source}: expected slider3 default signatures missing"
        )
    value = f"{sensitivity_percent:g}"
    altered = text.replace(slider_signature, f"slider3:{value}<", 1).replace(
        init_signature, f"slider3 = {value};", 1
    )
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(altered, encoding="ascii")


def setting_descriptor(key: str, sensitivity_percent: float, label: str) -> dict[str, Any]:
    return {
        "key": key,
        "label": label,
        "slider3_percent": sensitivity_percent,
        "relative_exciter_depth": sensitivity_percent / 50.0 if sensitivity_percent > 0.0 else 0.0,
    }


def band_energy_metrics(
    wav: transfer.StereoWav,
    bands: tuple[tuple[str, float, float], ...] = EXCITER_BANDS_HZ,
) -> dict[str, dict[str, float | None]]:
    mid = [(left + right) * 0.5 for left, right in zip(wav.left, wav.right)]
    side = [(left - right) * 0.5 for left, right in zip(wav.left, wav.right)]
    result: dict[str, dict[str, float | None]] = {}
    for name, low, high in bands:
        hp = coefficients("highpass", low, wav.sample_rate)
        lp = coefficients("lowpass", high, wav.sample_rate)
        filtered_left = cascaded(cascaded(wav.left, hp), lp)
        filtered_right = cascaded(cascaded(wav.right, hp), lp)
        filtered_mid = cascaded(cascaded(mid, hp), lp)
        filtered_side = cascaded(cascaded(side, hp), lp)
        combined_rms = math.sqrt(
            sum((left * left) + (right * right) for left, right in zip(filtered_left, filtered_right))
            / (2.0 * len(filtered_left))
        ) if filtered_left else 0.0
        mid_rms = rms(filtered_mid)
        side_rms = rms(filtered_side)
        result[name] = {
            "low_hz": low,
            "high_hz": high,
            "band_rms": combined_rms,
            "band_rms_dbfs": transfer.db(combined_rms),
            "mid_rms": mid_rms,
            "side_rms": side_rms,
            "side_to_mid_db": ratio_db(side_rms, mid_rms),
        }
    return result


def analyze_item(
    item: dict[str, Any],
    excerpt: pathlib.Path,
    captures: dict[str, pathlib.Path],
) -> dict[str, Any]:
    source = transfer.read_stereo_wav(excerpt)
    source_bands = band_energy_metrics(source)
    outputs = {name: transfer.read_stereo_wav(path) for name, path in captures.items()}
    output_bands = {name: band_energy_metrics(wav) for name, wav in outputs.items()}
    result = {
        "label": item["label"],
        "name": item["name"],
        "start_seconds": item["start_seconds"],
        "duration_seconds": item["duration_seconds"],
        "levels": {name: transfer.level_metrics(wav) for name, wav in outputs.items()},
        "bands": {},
    }
    for band, _low, _high in EXCITER_BANDS_HZ:
        accepted_rms = output_bands["accepted_50"][band]["band_rms_dbfs"]
        accepted_sm = output_bands["accepted_50"][band]["side_to_mid_db"]
        result["bands"][band] = {
            "source": source_bands[band],
            **{name: output_bands[name][band] for name in output_bands},
            "accepted_minus_source_band_rms_db": delta(accepted_rms, source_bands[band]["band_rms_dbfs"]),
            "reduced_minus_accepted_band_rms_db": delta(
                output_bands["reduced_35"][band]["band_rms_dbfs"], accepted_rms
            ),
            "bypass_minus_accepted_band_rms_db": delta(
                output_bands["bypass_0"][band]["band_rms_dbfs"], accepted_rms
            ),
            "reduced_minus_accepted_side_to_mid_db": delta(
                output_bands["reduced_35"][band]["side_to_mid_db"], accepted_sm
            ),
            "bypass_minus_accepted_side_to_mid_db": delta(
                output_bands["bypass_0"][band]["side_to_mid_db"], accepted_sm
            ),
        }
    return result


def evaluate_items(items: list[dict[str, Any]], ceiling_dbfs: float) -> dict[str, Any]:
    checks: list[dict[str, str]] = []
    for item in items:
        for key, _percent, _label in SETTINGS:
            levels = item["levels"][key]
            if levels["clipped_samples"] > 0:
                status = "fail"
                detail = f"{levels['clipped_samples']} clipped channel samples"
            elif levels["peak_dbfs"] is None:
                status = "fail"
                detail = "silent output"
            elif levels["peak_dbfs"] > ceiling_dbfs:
                status = "investigate"
                detail = f"peak={levels['peak_dbfs']:.3f} dBFS exceeds observation level {ceiling_dbfs:.3f} dBFS"
            else:
                status = "pass"
                detail = f"peak={levels['peak_dbfs']:.3f} dBFS, clipping=0"
            checks.append({"name": f"{item['name']}_{key}_integrity", "status": status, "detail": detail})
    status = "fail" if any(check["status"] == "fail" for check in checks) else (
        "measurement_complete_with_investigation"
        if any(check["status"] == "investigate" for check in checks)
        else "measurement_complete"
    )
    return {"status": status, "checks": checks}


def markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Axiom Dynamic Exciter Sensitivity Screen",
        "",
        f"Status: **{report['evaluation']['status'].upper()}**",
        "",
        "This pre-candidate screen compares temporary Fletcher-Munson exciter sensitivity settings "
        "through real JDSP on registered local material. Only `slider3` changes in temporary fixtures; "
        "the accepted script is unchanged.",
        "",
        "| Setting | `slider3` | Relative accepted-depth multiplier |",
        "| --- | ---: | ---: |",
    ]
    for setting in report["settings"]:
        lines.append(
            f"| {setting['label']} | {setting['slider3_percent']:.0f}% | "
            f"`{setting['relative_exciter_depth']:.2f}x` |"
        )
    lines.extend(
        [
            "",
            "Band RMS values are output energy in the inspected high-frequency range. Negative "
            "variant-minus-accepted values represent less measured brilliance or air than the accepted baseline; "
            "they do not establish an improvement without listening.",
            "",
            "| Material | Band | Source RMS (dBFS) | Accepted RMS (dBFS) | Reduced - accepted RMS (dB) | Bypass - accepted RMS (dB) | Reduced - accepted S/M (dB) | Bypass - accepted S/M (dB) |",
            "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for item in report["items"]:
        label = item["label"].replace("|", "\\|")
        for band, _low, _high in EXCITER_BANDS_HZ:
            values = item["bands"][band]
            lines.append(
                f"| {label} | {band} | {display(values['source']['band_rms_dbfs'])} | "
                f"{display(values['accepted_50']['band_rms_dbfs'])} | "
                f"{display(values['reduced_minus_accepted_band_rms_db'])} | "
                f"{display(values['bypass_minus_accepted_band_rms_db'])} | "
                f"{display(values['reduced_minus_accepted_side_to_mid_db'])} | "
                f"{display(values['bypass_minus_accepted_side_to_mid_db'])} |"
            )
    lines.extend(["", "## Integrity Checks", "", "| Check | Status | Detail |", "| --- | --- | --- |"])
    lines.extend(
        f"| {check['name']} | {check['status'].upper()} | {check['detail']} |"
        for check in report["evaluation"]["checks"]
    )
    lines.extend(
        [
            "",
            "Interpretation boundary: this screen establishes how much the accepted exciter contributes "
            "to presence, brilliance, air, and terminal pressure. A reduced setting becomes a candidate "
            "only if it shows a meaningful harshness-control or headroom advantage without simply removing "
            "the accepted clarity.",
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
    fixtures = {"accepted_50": accepted}
    for key, percent, _label in SETTINGS[1:]:
        fixture = output_dir / "fixtures" / f"{accepted.stem}_exciter_{percent:g}.eel"
        exciter_fixture(accepted, fixture, percent)
        fixtures[key] = fixture

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
            convert_excerpt(item, excerpt)
            captures = {}
            for key, _percent, label in SETTINGS:
                output = output_dir / key / f"{item['name']}.wav"
                run(
                    [
                        sys.executable,
                        str(script_dir / "render_jdsp_host.py"),
                        str(excerpt),
                        str(fixtures[key]),
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
                    f"{item['label']} {label} exciter sensitivity host render",
                )
                captures[key] = output
            reports.append(analyze_item(item, excerpt, captures))
        report = {
            "scope": "temporary dynamic exciter sensitivity settings on registered material through real JDSP",
            "accepted_eel": str(accepted),
            "manifest": str(args.manifest.resolve()),
            "fixtures": {name: str(path) for name, path in fixtures.items()},
            "settings": [setting_descriptor(*setting) for setting in SETTINGS],
            "master_limiter_threshold_db": args.master_limiter_threshold_db,
            "ceiling_dbfs": args.ceiling_dbfs,
            "bands_hz": EXCITER_BANDS_HZ,
            "items": reports,
        }
        report["evaluation"] = evaluate_items(reports, args.ceiling_dbfs)
        (output_dir / "exciter_sensitivity_screen.json").write_text(
            json.dumps(report, indent=2) + "\n", encoding="utf-8"
        )
        (output_dir / "exciter_sensitivity_screen.md").write_text(markdown(report), encoding="utf-8")
        print(output_dir / "exciter_sensitivity_screen.json")
        print(output_dir / "exciter_sensitivity_screen.md")
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
