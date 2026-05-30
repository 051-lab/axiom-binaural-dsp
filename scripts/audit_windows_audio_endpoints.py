#!/usr/bin/env python3
"""Audit Windows audio endpoints from WSL without changing audio routing."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import shutil
import subprocess
from pathlib import Path
from typing import Any


ROUTE_CLASSES = ("speaker_path", "wired_or_usb", "bluetooth")


class EndpointAuditError(RuntimeError):
    pass


def load_json_array(text: str) -> list[dict[str, Any]]:
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise EndpointAuditError(f"PowerShell endpoint JSON is invalid: {exc}") from exc
    if isinstance(data, dict):
        data = [data]
    if not isinstance(data, list):
        raise EndpointAuditError("PowerShell endpoint JSON must be an object or array")
    endpoints: list[dict[str, Any]] = []
    for index, item in enumerate(data):
        if not isinstance(item, dict):
            raise EndpointAuditError(f"endpoint[{index}] must be an object")
        endpoints.append(item)
    return endpoints


def collect_endpoints(powershell: str = "powershell.exe") -> list[dict[str, Any]]:
    if shutil.which(powershell) is None:
        raise EndpointAuditError(f"PowerShell executable not found: {powershell}")
    command = [
        powershell,
        "-NoProfile",
        "-Command",
        (
            "Get-PnpDevice -Class AudioEndpoint | "
            "Select-Object Status,FriendlyName,InstanceId | "
            "ConvertTo-Json -Depth 3"
        ),
    ]
    result = subprocess.run(command, text=True, capture_output=True, check=False)
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or f"exit {result.returncode}"
        raise EndpointAuditError(f"PowerShell endpoint audit failed: {detail}")
    return load_json_array(result.stdout)


def endpoint_flow(instance_id: str) -> str:
    normalized = instance_id.upper()
    if r"{0.0.0." in normalized:
        return "render"
    if r"{0.0.1." in normalized:
        return "capture"
    return "unknown"


def route_hints(name: str, flow: str) -> list[str]:
    if flow != "render":
        return []
    lowered = name.lower()
    hints: list[str] = []
    if "speaker" in lowered or "realtek" in lowered:
        hints.append("speaker_path")
    if "usb" in lowered or "dac" in lowered:
        hints.append("wired_or_usb")
    if "bluetooth" in lowered or "earpods" in lowered or "soundcore" in lowered or "skdy" in lowered:
        hints.append("bluetooth")
    return hints


def normalize_endpoint(item: dict[str, Any]) -> dict[str, Any]:
    name = str(item.get("FriendlyName", "")).strip()
    status = str(item.get("Status", "")).strip()
    instance_id = str(item.get("InstanceId", "")).strip()
    flow = endpoint_flow(instance_id)
    return {
        "friendly_name": name,
        "status": status,
        "status_ok": status.lower() == "ok",
        "flow": flow,
        "route_hints": route_hints(name, flow),
        "instance_id": instance_id,
    }


def summarize(endpoints: list[dict[str, Any]]) -> dict[str, Any]:
    normalized = [normalize_endpoint(item) for item in endpoints]
    route_summary = {
        name: {
            "ok": [
                endpoint["friendly_name"]
                for endpoint in normalized
                if endpoint["status_ok"] and name in endpoint["route_hints"]
            ],
            "not_ok": [
                endpoint["friendly_name"]
                for endpoint in normalized
                if not endpoint["status_ok"] and name in endpoint["route_hints"]
            ],
        }
        for name in ROUTE_CLASSES
    }
    render_endpoints = [endpoint for endpoint in normalized if endpoint["flow"] == "render"]
    return {
        "generated_at": dt.datetime.now(tz=dt.timezone.utc).isoformat(),
        "scope": "Windows audio endpoint status audit; playback qualification still requires listening evidence",
        "endpoint_count": len(normalized),
        "render_endpoint_count": len(render_endpoints),
        "render_ok_count": sum(1 for endpoint in render_endpoints if endpoint["status_ok"]),
        "route_summary": route_summary,
        "endpoints": normalized,
    }


def markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Axiom Windows Audio Endpoint Audit",
        "",
        "This audit reports Windows endpoint status only. It does not prove playback route stability.",
        "",
        f"- Endpoint count: `{report['endpoint_count']}`",
        f"- Render endpoints: `{report['render_endpoint_count']}`",
        f"- Render endpoints with `OK` status: `{report['render_ok_count']}`",
        "",
        "## Route Hints",
        "",
        "| Route class | OK endpoints | Not-OK endpoints |",
        "| --- | --- | --- |",
    ]
    for route_class in ROUTE_CLASSES:
        item = report["route_summary"][route_class]
        ok = ", ".join(f"`{name}`" for name in item["ok"]) or "-"
        not_ok = ", ".join(f"`{name}`" for name in item["not_ok"]) or "-"
        lines.append(f"| {route_class} | {ok} | {not_ok} |")
    lines.extend(
        [
            "",
            "## Endpoints",
            "",
            "| Flow | Status | Name | Route hints |",
            "| --- | --- | --- | --- |",
        ]
    )
    for endpoint in report["endpoints"]:
        hints = ", ".join(endpoint["route_hints"]) or "-"
        lines.append(
            f"| {endpoint['flow']} | {endpoint['status']} | `{endpoint['friendly_name']}` | {hints} |"
        )
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-json", type=Path, help="read a saved Get-PnpDevice JSON payload instead of PowerShell")
    parser.add_argument("--json", type=Path, help="write normalized endpoint report JSON")
    parser.add_argument("--markdown", type=Path, help="write normalized endpoint report Markdown")
    parser.add_argument("--powershell", default="powershell.exe")
    args = parser.parse_args()
    try:
        if args.input_json:
            endpoints = load_json_array(args.input_json.read_text(encoding="utf-8"))
        else:
            endpoints = collect_endpoints(args.powershell)
        report = summarize(endpoints)
    except (OSError, EndpointAuditError) as exc:
        print(f"error: {exc}")
        return 1
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
