"""Tests for Windows audio endpoint audit normalization."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import audit_windows_audio_endpoints as endpoint_audit


FIXTURE = [
    {
        "Status": "OK",
        "FriendlyName": "Speaker (Realtek(R) Audio)",
        "InstanceId": r"SWD\MMDEVAPI\{0.0.0.00000000}.{SPEAKER}",
    },
    {
        "Status": "Unknown",
        "FriendlyName": "Headphones (KT USB Audio)",
        "InstanceId": r"SWD\MMDEVAPI\{0.0.0.00000000}.{USB}",
    },
    {
        "Status": "Unknown",
        "FriendlyName": "Headset (EarPods)",
        "InstanceId": r"SWD\MMDEVAPI\{0.0.0.00000000}.{BT}",
    },
    {
        "Status": "OK",
        "FriendlyName": "Microphone Array (AMD Audio Device)",
        "InstanceId": r"SWD\MMDEVAPI\{0.0.1.00000000}.{MIC}",
    },
]


class WindowsAudioEndpointAuditTests(unittest.TestCase):
    def test_summary_separates_render_status_and_route_hints(self) -> None:
        report = endpoint_audit.summarize(FIXTURE)
        self.assertEqual(report["endpoint_count"], 4)
        self.assertEqual(report["render_endpoint_count"], 3)
        self.assertEqual(report["render_ok_count"], 1)
        self.assertEqual(report["route_summary"]["speaker_path"]["ok"], ["Speaker (Realtek(R) Audio)"])
        self.assertEqual(report["route_summary"]["wired_or_usb"]["not_ok"], ["Headphones (KT USB Audio)"])
        self.assertEqual(report["route_summary"]["bluetooth"]["not_ok"], ["Headset (EarPods)"])

    def test_single_powershell_object_json_is_normalized_to_array(self) -> None:
        payload = json.dumps(FIXTURE[0])
        endpoints = endpoint_audit.load_json_array(payload)
        self.assertEqual(len(endpoints), 1)
        self.assertEqual(endpoints[0]["FriendlyName"], "Speaker (Realtek(R) Audio)")

    def test_cli_writes_json_and_markdown_from_saved_payload(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            input_json = root / "endpoints.json"
            report_json = root / "report.json"
            report_md = root / "report.md"
            input_json.write_text(json.dumps(FIXTURE), encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    str(Path(__file__).resolve().parents[1] / "scripts" / "audit_windows_audio_endpoints.py"),
                    "--input-json",
                    str(input_json),
                    "--json",
                    str(report_json),
                    "--markdown",
                    str(report_md),
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0)
            self.assertTrue(report_json.is_file())
            self.assertTrue(report_md.is_file())
            report = json.loads(report_json.read_text(encoding="utf-8"))
            self.assertEqual(report["route_summary"]["speaker_path"]["ok"], ["Speaker (Realtek(R) Audio)"])
            self.assertIn("Axiom Windows Audio Endpoint Audit", report_md.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
