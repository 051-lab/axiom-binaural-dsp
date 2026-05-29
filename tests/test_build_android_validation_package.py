"""Tests for Android validation package generation."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import build_android_validation_package as android_package


class AndroidValidationPackageTests(unittest.TestCase):
    def test_package_copies_script_and_records_hash(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            accepted = root / "accepted.eel"
            accepted.write_text("desc: accepted\n", encoding="ascii")
            output = root / "package"
            manifest = android_package.build_package(accepted, output, package_name="test-package")
            copied = output / "scripts" / accepted.name
            self.assertTrue(copied.is_file())
            self.assertEqual(manifest["scripts"][0]["sha256"], android_package.sha256(copied))
            self.assertTrue((output / "android-validation-checklist.md").is_file())
            self.assertTrue((output / "listening-record-template.json").is_file())

    def test_candidate_package_records_both_roles(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            accepted = root / "accepted.eel"
            candidate = root / "candidate.eel"
            accepted.write_text("desc: accepted\n", encoding="ascii")
            candidate.write_text("desc: candidate\n", encoding="ascii")
            manifest = android_package.build_package(accepted, root / "package", candidate=candidate)
        self.assertEqual([item["role"] for item in manifest["scripts"]], ["accepted", "candidate"])

    def test_missing_script_raises_package_error(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(android_package.PackageError):
                android_package.build_package(Path(directory) / "missing.eel", Path(directory) / "package")

    def test_checklist_contains_rootless_jamesdsp_hash_and_host_settings(self) -> None:
        manifest = {
            "package_name": "test-package",
            "scripts": [{"role": "accepted", "filename": "accepted.eel", "sha256": "abc123"}],
        }
        text = android_package.checklist(manifest)
        self.assertIn("RootlessJamesDSP", text)
        self.assertIn("SHA-256", text)
        self.assertIn("-1.00 dB", text)

    def test_cli_builds_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            accepted = root / "accepted.eel"
            accepted.write_text("desc: accepted\n", encoding="ascii")
            output = root / "package"
            result = subprocess.run(
                [
                    sys.executable,
                    str(Path(__file__).resolve().parents[1] / "scripts" / "build_android_validation_package.py"),
                    str(accepted),
                    str(output),
                    "--package-name",
                    "cli-package",
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(result.returncode, 0)
        self.assertEqual(manifest["package_name"], "cli-package")


if __name__ == "__main__":
    unittest.main()
