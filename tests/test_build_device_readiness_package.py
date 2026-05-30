"""Tests for Axiom device-readiness package generation."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import build_device_readiness_package as readiness_package


def device(label: str, device_class: str, complete: bool = True, available: bool = True) -> dict:
    return {
        "label": label,
        "device_class": device_class,
        "platform": "test",
        "route": "test route",
        "output_device": "test output",
        "validation_role": "test role",
        "available": available,
        "qualification_allowed": complete,
        "crossfeed_policy": "not_applicable" if device_class == "wsl_jdsp_lab" else "off_for_qualification",
        "checks": {
            "active_script_hash_verified": complete,
            "host_settings_verified": complete,
            "route_stability_checked": complete,
            "reboot_persistence_checked": complete,
        },
    }


def matrix(complete: bool = True) -> dict:
    return {
        "schema_version": 1,
        "devices": [
            device("phone", "primary_android", complete=complete),
            device("speaker", "speaker_path", complete=complete),
            device("dac", "wired_or_usb", complete=complete),
            device("bt", "bluetooth", complete=complete),
            device("wsl", "wsl_jdsp_lab", complete=complete),
        ],
    }


class DeviceReadinessPackageTests(unittest.TestCase):
    def test_package_writes_manifest_and_checklist(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            accepted = root / "accepted.eel"
            accepted.write_text("desc: accepted\n", encoding="ascii")
            matrix_path = root / "matrix.json"
            matrix_path.write_text(json.dumps(matrix()), encoding="utf-8")
            output = root / "package"
            manifest = readiness_package.build_package(accepted, matrix_path, output)
            self.assertEqual(manifest["strict_validation"]["status"], "pass")
            self.assertTrue((output / "manifest.json").is_file())
            self.assertTrue((output / "device-readiness-checklist.md").is_file())

    def test_incomplete_available_route_generates_actions_and_fails_strict(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            accepted = root / "accepted.eel"
            accepted.write_text("desc: accepted\n", encoding="ascii")
            matrix_path = root / "matrix.json"
            matrix_path.write_text(json.dumps(matrix(complete=False)), encoding="utf-8")
            manifest = readiness_package.build_package(accepted, matrix_path, root / "package")
        self.assertEqual(manifest["strict_validation"]["status"], "fail")
        actions = "\n".join(action for route in manifest["routes"] for action in route["actions"])
        self.assertIn("Confirm active script filename", actions)
        self.assertIn("Use the Android validation package", actions)

    def test_cli_returns_failure_for_blocked_matrix_but_writes_package(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            accepted = root / "accepted.eel"
            accepted.write_text("desc: accepted\n", encoding="ascii")
            matrix_path = root / "matrix.json"
            matrix_path.write_text(json.dumps(matrix(complete=False)), encoding="utf-8")
            output = root / "package"
            result = subprocess.run(
                [
                    sys.executable,
                    str(Path(__file__).resolve().parents[1] / "scripts" / "build_device_readiness_package.py"),
                    str(accepted),
                    str(output),
                    "--device-matrix",
                    str(matrix_path),
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 1)
            self.assertTrue((output / "manifest.json").is_file())
            self.assertIn("strict_status=fail", result.stdout)


if __name__ == "__main__":
    unittest.main()
