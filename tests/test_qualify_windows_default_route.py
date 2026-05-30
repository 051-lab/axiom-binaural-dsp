"""Tests for Windows default route qualification reporting."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest import mock

import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import qualify_windows_default_route as route_qualifier


def endpoint_report(status: str = "pass") -> dict:
    errors = [] if status == "pass" else ["default render endpoint is not `wired_or_usb`; route hints: speaker_path"]
    return {
        "default_render_endpoint": {
            "id": "{0.0.0.00000000}.{speaker}",
            "state": 1,
            "matched_endpoint": "Speaker (Realtek(R) Audio)",
            "matched_status": "OK",
            "matched_route_hints": ["speaker_path"],
        },
        "required_default_route": {
            "route_class": "wired_or_usb",
            "status": status,
            "errors": errors,
        },
        "endpoint_count": 1,
        "render_endpoint_count": 1,
        "render_ok_count": 1,
        "route_summary": {
            "speaker_path": {"ok": ["Speaker (Realtek(R) Audio)"], "not_ok": []},
            "wired_or_usb": {"ok": [], "not_ok": []},
            "bluetooth": {"ok": [], "not_ok": []},
        },
        "endpoints": [],
    }


class WindowsDefaultRouteQualificationTests(unittest.TestCase):
    def test_blocked_report_stops_before_route_or_playback(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            eel = root / "accepted.eel"
            eel.write_text("desc: accepted\n", encoding="ascii")
            with mock.patch.object(route_qualifier, "endpoint_report", return_value=endpoint_report("fail")), \
                mock.patch.object(route_qualifier.package_hash, "sha256", return_value="abc"), \
                mock.patch.object(route_qualifier, "run") as run_mock, \
                mock.patch.object(route_qualifier, "play_probe") as play_mock:
                report = route_qualifier.qualify_route(
                    "wired_or_usb",
                    root / "out",
                    accepted_eel=eel,
                    probe=root / "probe.wav",
                    pulse_server="unix:/tmp/test",
                    route_helper=root / "helper",
                    powershell="powershell.exe",
                    volume=32768,
                    skip_route_start=False,
                    skip_playback=False,
                    playback_confirmed=False,
                    reconnect_confirmed=False,
                )
            self.assertEqual(report["status"], "blocked")
            self.assertEqual(report["checks"][0]["name"], "default_windows_route")
            run_mock.assert_not_called()
            play_mock.assert_not_called()

    def test_pass_report_requires_playback_and_reconnect_confirmation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            eel = root / "accepted.eel"
            helper = root / "helper"
            probe = root / "probe.wav"
            eel.write_text("desc: accepted\n", encoding="ascii")
            helper.write_text("#!/bin/sh\n", encoding="ascii")
            probe.write_bytes(b"RIFF")
            with mock.patch.object(route_qualifier, "endpoint_report", return_value=endpoint_report("pass")), \
                mock.patch.object(route_qualifier.package_hash, "sha256", return_value="abc"), \
                mock.patch.object(route_qualifier, "host_settings", return_value={
                    "liveprog_enable": "true",
                    "liveprog_file": str(eel),
                    "master_limthreshold": "-1.0",
                    "master_limrelease": "60",
                    "master_postgain": "0",
                    "crossfeed_enable": "false",
                }), \
                mock.patch.object(route_qualifier, "run") as run_mock, \
                mock.patch.object(route_qualifier, "play_probe") as play_mock:
                run_mock.return_value.stdout = "hot reload ok\n"
                run_mock.return_value.stderr = ""
                report = route_qualifier.qualify_route(
                    "wired_or_usb",
                    root / "out",
                    accepted_eel=eel,
                    probe=probe,
                    pulse_server="unix:/tmp/test",
                    route_helper=helper,
                    powershell="powershell.exe",
                    volume=32768,
                    skip_route_start=False,
                    skip_playback=False,
                    playback_confirmed=True,
                    reconnect_confirmed=True,
                )
            self.assertEqual(report["status"], "pass")
            self.assertEqual([check["status"] for check in report["checks"]], ["pass", "pass", "pass", "pass"])
            play_mock.assert_called_once_with(probe, "unix:/tmp/test", 32768)


if __name__ == "__main__":
    unittest.main()
