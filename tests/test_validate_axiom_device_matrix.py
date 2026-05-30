"""Tests for Axiom device matrix validation."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import validate_axiom_device_matrix as device_matrix


def device(label: str, device_class: str = "primary_android", available: bool = True) -> dict:
    return {
        "label": label,
        "device_class": device_class,
        "platform": "Android",
        "route": "RootlessJamesDSP",
        "output_device": "wired earbuds",
        "validation_role": "primary phone validation",
        "available": available,
        "qualification_allowed": True,
        "crossfeed_policy": "off_for_qualification",
        "checks": {
            "active_script_hash_verified": True,
            "host_settings_verified": True,
            "route_stability_checked": True,
            "reboot_persistence_checked": True,
        },
    }


class DeviceMatrixValidationTests(unittest.TestCase):
    def test_complete_matrix_passes(self) -> None:
        data = {
            "schema_version": 1,
            "devices": [
                device("phone", "primary_android"),
                device("speakers", "speaker_path"),
                device("dac", "wired_or_usb"),
                device("bt", "bluetooth"),
                device("wsl", "wsl_jdsp_lab"),
            ],
        }
        result = device_matrix.validate_matrix(data, strict_coverage=True)
        self.assertEqual(result["status"], "pass")

    def test_missing_classes_warn_or_fail_strict_coverage(self) -> None:
        data = {"schema_version": 1, "devices": [device("phone")]}
        loose = device_matrix.validate_matrix(data)
        strict = device_matrix.validate_matrix(data, strict_coverage=True)
        self.assertEqual(loose["status"], "pass_with_warnings")
        self.assertEqual(strict["status"], "fail")

    def test_strict_setup_requires_available_device_checks(self) -> None:
        item = device("speakers", "speaker_path")
        item["qualification_allowed"] = False
        item["checks"]["route_stability_checked"] = False
        data = {
            "schema_version": 1,
            "devices": [
                device("phone", "primary_android"),
                item,
                device("dac", "wired_or_usb"),
                device("bt", "bluetooth"),
                device("wsl", "wsl_jdsp_lab"),
            ],
        }
        loose = device_matrix.validate_matrix(data, strict_coverage=True)
        strict = device_matrix.validate_matrix(
            data,
            strict_coverage=True,
            strict_setup=True,
        )
        self.assertEqual(loose["status"], "pass")
        self.assertEqual(strict["status"], "fail")
        self.assertTrue(any("incomplete checks" in error for error in strict["errors"]))

    def test_qualification_crossfeed_must_be_off(self) -> None:
        item = device("phone")
        item["crossfeed_policy"] = "manual_compatibility_only"
        result = device_matrix.validate_matrix({"schema_version": 1, "devices": [item]})
        self.assertEqual(result["status"], "fail")
        self.assertTrue(any("crossfeed off" in error for error in result["errors"]))

    def test_primary_android_reboot_check_warning(self) -> None:
        item = device("phone")
        item["checks"]["reboot_persistence_checked"] = False
        result = device_matrix.validate_matrix({"schema_version": 1, "devices": [item]})
        self.assertEqual(result["status"], "pass_with_warnings")
        self.assertTrue(any("reboot persistence" in warning for warning in result["warnings"]))

    def test_markdown_reports_coverage(self) -> None:
        result = device_matrix.validate_matrix({"schema_version": 1, "devices": [device("phone")]})
        text = device_matrix.markdown(result)
        self.assertIn("Device Matrix Validation", text)
        self.assertIn("primary_android", text)

    def test_cli_writes_reports(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            matrix = root / "matrix.json"
            report = root / "matrix-validation.json"
            markdown = root / "matrix-validation.md"
            matrix.write_text(json.dumps({"schema_version": 1, "devices": [device("phone")]}), encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    str(Path(__file__).resolve().parents[1] / "scripts" / "validate_axiom_device_matrix.py"),
                    str(matrix),
                    "--json",
                    str(report),
                    "--markdown",
                    str(markdown),
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0)
            self.assertIn("pass_with_warnings", report.read_text(encoding="utf-8"))
            self.assertIn("Coverage", markdown.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
