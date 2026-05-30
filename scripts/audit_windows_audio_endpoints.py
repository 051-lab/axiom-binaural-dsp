#!/usr/bin/env python3
"""Audit Windows audio endpoints from WSL without changing audio routing."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any


ROUTE_CLASSES = ("speaker_path", "wired_or_usb", "bluetooth")
DEFAULT_RENDER_ENDPOINT_SOURCE = r'''
using System;
using System.Runtime.InteropServices;

public enum EDataFlow { eRender = 0, eCapture = 1, eAll = 2 }
public enum ERole { eConsole = 0, eMultimedia = 1, eCommunications = 2 }

[ComImport]
[Guid("A95664D2-9614-4F35-A746-DE8DB63617E6")]
[InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
public interface IMMDeviceEnumerator
{
    int EnumAudioEndpoints(EDataFlow dataFlow, uint dwStateMask, IntPtr ppDevices);
    int GetDefaultAudioEndpoint(EDataFlow dataFlow, ERole role, out IMMDevice ppDevice);
    int GetDevice(string pwstrId, out IMMDevice ppDevice);
    int RegisterEndpointNotificationCallback(IntPtr pClient);
    int UnregisterEndpointNotificationCallback(IntPtr pClient);
}

[ComImport]
[Guid("D666063F-1587-4E43-81F1-B948E807363F")]
[InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
public interface IMMDevice
{
    int Activate(ref Guid iid, uint dwClsCtx, IntPtr pActivationParams, out IntPtr ppInterface);
    int OpenPropertyStore(uint stgmAccess, out IntPtr ppProperties);
    int GetId([MarshalAs(UnmanagedType.LPWStr)] out string ppstrId);
    int GetState(out uint pdwState);
}

public static class AxiomCoreAudio
{
    public static string DefaultRenderEndpointJson()
    {
        var type = Type.GetTypeFromCLSID(new Guid("BCDE0395-E52F-467C-8E3D-C4579291692E"));
        var enumerator = (IMMDeviceEnumerator)Activator.CreateInstance(type);
        IMMDevice device;
        int hr = enumerator.GetDefaultAudioEndpoint(EDataFlow.eRender, ERole.eMultimedia, out device);
        if (hr != 0) Marshal.ThrowExceptionForHR(hr);
        string id;
        uint state;
        device.GetId(out id);
        device.GetState(out state);
        return "{\"flow\":\"render\",\"role\":\"multimedia\",\"id\":\"" + JsonEscape(id) + "\",\"state\":" + state.ToString() + "}";
    }

    static string JsonEscape(string value)
    {
        return value.Replace("\\", "\\\\").Replace("\"", "\\\"");
    }
}
'''


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


def collect_default_render_endpoint(powershell: str = "powershell.exe") -> dict[str, Any]:
    if shutil.which(powershell) is None:
        raise EndpointAuditError(f"PowerShell executable not found: {powershell}")
    command_text = (
        "$ErrorActionPreference='Stop'; Add-Type -TypeDefinition @'\n"
        + DEFAULT_RENDER_ENDPOINT_SOURCE
        + "\n'@; [AxiomCoreAudio]::DefaultRenderEndpointJson()"
    )
    result = subprocess.run(
        [powershell, "-NoProfile", "-Command", command_text],
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or f"exit {result.returncode}"
        raise EndpointAuditError(f"PowerShell default render endpoint audit failed: {detail}")
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise EndpointAuditError(f"PowerShell default render endpoint JSON is invalid: {exc}") from exc
    if not isinstance(data, dict):
        raise EndpointAuditError("PowerShell default render endpoint JSON must be an object")
    return data


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


def endpoint_coreaudio_id(instance_id: str) -> str:
    match = re.search(r"(\{0\.0\.[01]\.[^}]+\}\.\{[^}]+\})", instance_id, re.IGNORECASE)
    return match.group(1).lower() if match else ""


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
        "coreaudio_id": endpoint_coreaudio_id(instance_id),
        "instance_id": instance_id,
    }


def normalize_default_render(
    default_render: dict[str, Any] | None,
    endpoints: list[dict[str, Any]],
) -> dict[str, Any] | None:
    if default_render is None:
        return None
    endpoint_id = str(default_render.get("id", "")).lower()
    matched = next((endpoint for endpoint in endpoints if endpoint["coreaudio_id"] == endpoint_id), None)
    return {
        "id": str(default_render.get("id", "")),
        "state": default_render.get("state"),
        "matched_endpoint": matched["friendly_name"] if matched else "",
        "matched_status": matched["status"] if matched else "",
        "matched_route_hints": matched["route_hints"] if matched else [],
    }


def summarize(endpoints: list[dict[str, Any]], default_render: dict[str, Any] | None = None) -> dict[str, Any]:
    normalized = [normalize_endpoint(item) for item in endpoints]
    default_render_endpoint = normalize_default_render(default_render, normalized)
    for endpoint in normalized:
        endpoint["is_default_render"] = bool(
            default_render_endpoint
            and endpoint["coreaudio_id"]
            and endpoint["coreaudio_id"] == str(default_render_endpoint["id"]).lower()
        )
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
        "default_render_endpoint": default_render_endpoint,
        "route_summary": route_summary,
        "endpoints": normalized,
    }


def evaluate_required_default_route(report: dict[str, Any], route_class: str) -> dict[str, Any]:
    errors: list[str] = []
    default_render = report.get("default_render_endpoint")
    if default_render is None:
        errors.append("default render endpoint was not collected")
    else:
        endpoint = str(default_render.get("matched_endpoint", ""))
        status = str(default_render.get("matched_status", ""))
        hints = default_render.get("matched_route_hints", [])
        if not endpoint:
            errors.append("default render endpoint did not match any audited endpoint")
        if status.lower() != "ok":
            errors.append(f"default render endpoint is not OK: {status or 'unknown'}")
        if route_class not in hints:
            joined = ", ".join(str(hint) for hint in hints) or "<none>"
            errors.append(f"default render endpoint is not `{route_class}`; route hints: {joined}")
    return {
        "route_class": route_class,
        "status": "fail" if errors else "pass",
        "errors": errors,
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
    ]
    default_render = report.get("default_render_endpoint")
    if default_render:
        hints = ", ".join(default_render["matched_route_hints"]) or "-"
        lines.extend(
            [
                "## Default Render Endpoint",
                "",
                f"- Endpoint: `{default_render['matched_endpoint'] or 'unmatched'}`",
                f"- Status: `{default_render['matched_status'] or 'unknown'}`",
                f"- Route hints: `{hints}`",
                f"- CoreAudio ID: `{default_render['id']}`",
                "",
            ]
        )
    required = report.get("required_default_route")
    if required:
        lines.extend(
            [
                "## Required Default Route",
                "",
                f"- Route class: `{required['route_class']}`",
                f"- Status: `{required['status']}`",
                "",
            ]
        )
        if required["errors"]:
            lines.extend(f"- {error}" for error in required["errors"])
            lines.append("")
    lines.extend(
        [
            "## Route Hints",
            "",
            "| Route class | OK endpoints | Not-OK endpoints |",
            "| --- | --- | --- |",
        ]
    )
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
            "| Flow | Default | Status | Name | Route hints |",
            "| --- | ---: | --- | --- | --- |",
        ]
    )
    for endpoint in report["endpoints"]:
        hints = ", ".join(endpoint["route_hints"]) or "-"
        lines.append(
            f"| {endpoint['flow']} | `{endpoint['is_default_render']}` | {endpoint['status']} | `{endpoint['friendly_name']}` | {hints} |"
        )
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-json", type=Path, help="read a saved Get-PnpDevice JSON payload instead of PowerShell")
    parser.add_argument("--json", type=Path, help="write normalized endpoint report JSON")
    parser.add_argument("--markdown", type=Path, help="write normalized endpoint report Markdown")
    parser.add_argument("--powershell", default="powershell.exe")
    parser.add_argument(
        "--skip-default-render",
        action="store_true",
        help="skip CoreAudio default render endpoint lookup",
    )
    parser.add_argument(
        "--require-default-route",
        choices=ROUTE_CLASSES,
        help="fail unless the active default render endpoint is OK and matches this route class",
    )
    args = parser.parse_args()
    try:
        default_render = None
        if args.input_json:
            endpoints = load_json_array(args.input_json.read_text(encoding="utf-8"))
        else:
            endpoints = collect_endpoints(args.powershell)
            if not args.skip_default_render:
                default_render = collect_default_render_endpoint(args.powershell)
        report = summarize(endpoints, default_render=default_render)
        if args.require_default_route:
            report["required_default_route"] = evaluate_required_default_route(
                report,
                args.require_default_route,
            )
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
    required = report.get("required_default_route")
    return 1 if required and required["status"] == "fail" else 0


if __name__ == "__main__":
    raise SystemExit(main())
