#!/usr/bin/env python3
"""Create local evidence for a Windows default-output route qualification pass."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import pathlib
import subprocess
import sys
from typing import Any

import audit_windows_audio_endpoints as endpoint_audit
import build_android_validation_package as package_hash


REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
DEFAULT_ACCEPTED_EEL = REPO_ROOT / "src" / "axiom_binaural_dsp_v4.1.4.11.eel"
DEFAULT_PROBE = pathlib.Path("/tmp/axiom-wsl-route-stability-v4.1.4.11/stimuli/correlated_mono.wav")
DEFAULT_PULSE_SERVER = "unix:/tmp/jdsp-win/native"
DEFAULT_ROUTE_HELPER = pathlib.Path.home() / ".local/bin/jdsp-audio-reset"
EXPECTED_SETTINGS = {
    "liveprog_enable": "true",
    "master_limthreshold": "-1.0",
    "master_limrelease": "60",
    "master_postgain": "0",
    "crossfeed_enable": "false",
}


class RouteQualificationError(RuntimeError):
    pass


def run(
    command: list[str],
    label: str,
    *,
    env: dict[str, str] | None = None,
    check: bool = True,
    timeout: float | None = None,
) -> subprocess.CompletedProcess[str]:
    try:
        result = subprocess.run(
            command,
            text=True,
            capture_output=True,
            check=False,
            env=env,
            timeout=timeout,
        )
    except FileNotFoundError as exc:
        raise RouteQualificationError(f"{label} failed: command not found: {command[0]}") from exc
    except subprocess.TimeoutExpired as exc:
        raise RouteQualificationError(f"{label} timed out after {timeout:g} seconds") from exc
    if check and result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or f"exit {result.returncode}"
        raise RouteQualificationError(f"{label} failed: {detail}")
    return result


def pulse_environment(pulse_server: str) -> dict[str, str]:
    environment = os.environ.copy()
    environment["PULSE_SERVER"] = pulse_server
    return environment


def read_jdsp_setting(key: str) -> str:
    return run(["jamesdsp", "--get", key], f"read JDSP setting {key}").stdout.strip()


def host_settings() -> dict[str, str]:
    keys = list(EXPECTED_SETTINGS) + ["liveprog_file"]
    return {key: read_jdsp_setting(key) for key in keys}


def setting_errors(settings: dict[str, str], accepted_eel: pathlib.Path) -> list[str]:
    errors = []
    for key, expected in EXPECTED_SETTINGS.items():
        if settings.get(key) != expected:
            errors.append(f"{key}={settings.get(key, '<missing>')} expected {expected}")
    liveprog_file = pathlib.Path(settings.get("liveprog_file", ""))
    try:
        if liveprog_file.resolve() != accepted_eel.resolve():
            errors.append(f"liveprog_file={liveprog_file} expected {accepted_eel.resolve()}")
    except OSError:
        errors.append(f"liveprog_file={liveprog_file} cannot be resolved")
    return errors


def endpoint_report(route_class: str, powershell: str) -> dict[str, Any]:
    endpoints = endpoint_audit.collect_endpoints(powershell)
    default_render = endpoint_audit.collect_default_render_endpoint(powershell)
    report = endpoint_audit.summarize(endpoints, default_render=default_render)
    report["required_default_route"] = endpoint_audit.evaluate_required_default_route(report, route_class)
    return report


def write_endpoint_artifacts(report: dict[str, Any], output_dir: pathlib.Path) -> dict[str, str]:
    json_path = output_dir / "windows-endpoints.json"
    markdown_path = output_dir / "windows-endpoints.md"
    json_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    markdown_path.write_text(endpoint_audit.markdown(report), encoding="utf-8")
    return {"json": str(json_path), "markdown": str(markdown_path)}


def play_probe(probe: pathlib.Path, pulse_server: str, volume: int) -> None:
    if not probe.is_file():
        raise RouteQualificationError(f"probe WAV not found: {probe}")
    run(
        [
            "paplay",
            "--device=JamesDSP",
            f"--volume={volume}",
            "--latency-msec=50",
            str(probe),
        ],
        "play route probe",
        env=pulse_environment(pulse_server),
        timeout=15,
    )


def qualify_route(
    route_class: str,
    output_dir: pathlib.Path,
    *,
    accepted_eel: pathlib.Path,
    probe: pathlib.Path,
    pulse_server: str,
    route_helper: pathlib.Path,
    powershell: str,
    volume: int,
    skip_route_start: bool,
    skip_playback: bool,
    playback_confirmed: bool,
    reconnect_confirmed: bool,
) -> dict[str, Any]:
    if not accepted_eel.is_file():
        raise RouteQualificationError(f"accepted EEL script not found: {accepted_eel}")
    output_dir.mkdir(parents=True, exist_ok=True)
    report: dict[str, Any] = {
        "generated_at": dt.datetime.now(tz=dt.timezone.utc).isoformat(),
        "scope": "Windows default-output route setup/playback evidence package",
        "route_class": route_class,
        "accepted_script": {
            "path": str(accepted_eel.resolve()),
            "filename": accepted_eel.name,
            "sha256": package_hash.sha256(accepted_eel),
        },
        "probe": str(probe),
        "pulse_server": pulse_server,
        "checks": [],
        "artifacts": {},
    }

    endpoints = endpoint_report(route_class, powershell)
    report["endpoint_audit"] = endpoints
    report["artifacts"]["endpoint_audit"] = write_endpoint_artifacts(endpoints, output_dir)
    required = endpoints["required_default_route"]
    report["checks"].append(
        {
            "name": "default_windows_route",
            "status": required["status"],
            "detail": "; ".join(required["errors"]) if required["errors"] else "default route matches requested class",
        }
    )
    if required["status"] != "pass":
        report["status"] = "blocked"
        return report

    if not skip_route_start:
        if not route_helper.is_file():
            raise RouteQualificationError(f"route helper not found: {route_helper}")
        run([str(route_helper)], "start managed JDSP route", timeout=20)
    run(["jamesdsp", "--is-connected"], "verify JamesDSP service", env=pulse_environment(pulse_server), timeout=8)
    preset_name = f"Axiom-v4.1.4.11-{route_class}-route-check"
    hot_reload = run(
        [str(REPO_ROOT / "scripts" / "hot_reload_liveprog.sh"), str(accepted_eel), preset_name],
        "hot reload accepted Liveprog",
        timeout=15,
    )
    (output_dir / "hot-reload.log").write_text(hot_reload.stdout + hot_reload.stderr, encoding="utf-8")
    settings = host_settings()
    report["host_settings"] = settings
    errors = setting_errors(settings, accepted_eel)
    report["checks"].append(
        {
            "name": "host_settings",
            "status": "fail" if errors else "pass",
            "detail": "; ".join(errors) if errors else "accepted script and host settings verified",
        }
    )
    if errors:
        report["status"] = "blocked"
        return report

    if skip_playback:
        playback_status = "skipped"
        playback_detail = "playback probe skipped by request"
    else:
        play_probe(probe, pulse_server, volume)
        playback_status = "pass" if playback_confirmed else "pending_user_confirmation"
        playback_detail = (
            "user confirmed clean playback"
            if playback_confirmed
            else "probe played; confirm clean audible output before updating device matrix"
        )
    report["checks"].append(
        {
            "name": "route_playback",
            "status": playback_status,
            "detail": playback_detail,
        }
    )
    reconnect_status = "pass" if reconnect_confirmed else "pending_user_confirmation"
    report["checks"].append(
        {
            "name": "reconnect_persistence",
            "status": reconnect_status,
            "detail": (
                "user confirmed playback after reconnect"
                if reconnect_confirmed
                else "rerun after route restart and confirm clean playback before updating device matrix"
            ),
        }
    )
    if playback_confirmed and reconnect_confirmed:
        report["status"] = "pass"
    else:
        report["status"] = "pending_user_confirmation"
    return report


def markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Axiom Windows Route Qualification",
        "",
        f"Status: **{report['status'].upper()}**",
        "",
        f"Route class: `{report['route_class']}`",
        f"Accepted script: `{report['accepted_script']['filename']}`",
        f"SHA-256: `{report['accepted_script']['sha256']}`",
        f"Probe: `{report['probe']}`",
        "",
        "## Checks",
        "",
        "| Check | Status | Detail |",
        "| --- | ---: | --- |",
    ]
    for check in report["checks"]:
        lines.append(f"| {check['name']} | {check['status']} | {check['detail']} |")
    endpoint = report["endpoint_audit"].get("default_render_endpoint") or {}
    lines.extend(
        [
            "",
            "## Default Render Endpoint",
            "",
            f"- Endpoint: `{endpoint.get('matched_endpoint', '') or 'unmatched'}`",
            f"- Status: `{endpoint.get('matched_status', '') or 'unknown'}`",
            f"- Hints: `{', '.join(endpoint.get('matched_route_hints', [])) or '-'}`",
            "",
            "Full reports and host logs are local evidence. Do not commit them unless sanitized.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("route_class", choices=endpoint_audit.ROUTE_CLASSES)
    parser.add_argument("output_dir", type=pathlib.Path)
    parser.add_argument("--accepted-eel", type=pathlib.Path, default=DEFAULT_ACCEPTED_EEL)
    parser.add_argument("--probe", type=pathlib.Path, default=DEFAULT_PROBE)
    parser.add_argument("--pulse-server", default=DEFAULT_PULSE_SERVER)
    parser.add_argument("--route-helper", type=pathlib.Path, default=DEFAULT_ROUTE_HELPER)
    parser.add_argument("--powershell", default="powershell.exe")
    parser.add_argument("--volume", type=int, default=32768)
    parser.add_argument("--skip-route-start", action="store_true")
    parser.add_argument("--skip-playback", action="store_true")
    parser.add_argument("--playback-confirmed", action="store_true")
    parser.add_argument("--reconnect-confirmed", action="store_true")
    args = parser.parse_args()
    if not 1 <= args.volume <= 65536:
        parser.error("--volume must be in [1, 65536]")
    output_dir = args.output_dir.expanduser().resolve()
    try:
        report = qualify_route(
            args.route_class,
            output_dir,
            accepted_eel=args.accepted_eel.expanduser().resolve(),
            probe=args.probe.expanduser(),
            pulse_server=args.pulse_server,
            route_helper=args.route_helper.expanduser(),
            powershell=args.powershell,
            volume=args.volume,
            skip_route_start=args.skip_route_start,
            skip_playback=args.skip_playback,
            playback_confirmed=args.playback_confirmed,
            reconnect_confirmed=args.reconnect_confirmed,
        )
    except RouteQualificationError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    output_dir.mkdir(parents=True, exist_ok=True)
    report_json = output_dir / "qualification.json"
    report_md = output_dir / "qualification.md"
    report_json.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    report_md.write_text(markdown(report), encoding="utf-8")
    print(report_json)
    print(report_md)
    return 1 if report["status"] == "blocked" else 0


if __name__ == "__main__":
    raise SystemExit(main())
