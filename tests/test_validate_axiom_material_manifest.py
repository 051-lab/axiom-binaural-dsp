"""Tests for Axiom material manifest coverage validation."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import validate_axiom_material_manifest as manifest_validator


def manifest(path: Path, **extra: object) -> dict:
    item = {
        "label": "Dense electronic hook",
        "path": str(path),
        "start_seconds": 10.0,
        "duration_seconds": 20.0,
    }
    item.update(extra)
    return {"tracks": [item]}


class MaterialManifestValidationTests(unittest.TestCase):
    def test_minimal_runner_compatible_manifest_passes_with_metadata_warnings(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            audio = Path(directory) / "item.wav"
            audio.write_bytes(b"placeholder")
            result = manifest_validator.validate_manifest(manifest(audio))
        self.assertEqual(result["status"], "pass_with_warnings")
        self.assertTrue(any("tracks[0].material_class is missing" in warning for warning in result["warnings"]))

    def test_strict_metadata_requires_taxonomy_fields(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            audio = Path(directory) / "item.wav"
            audio.write_bytes(b"placeholder")
            result = manifest_validator.validate_manifest(manifest(audio), strict_metadata=True)
        self.assertEqual(result["status"], "fail")
        self.assertIn("tracks[0].failure_modes must be a non-empty list", result["errors"])

    def test_strict_metadata_counts_coverage(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            audio = Path(directory) / "item.wav"
            audio.write_bytes(b"placeholder")
            data = manifest(
                audio,
                material_class="dense_pop_edm",
                failure_modes=["dense_mix_limiter_pressure", "air_harshness"],
                license_scope="CC0 test fixture",
                provenance="local generated placeholder",
                role="Expose dense full-band limiter pressure.",
            )
            result = manifest_validator.validate_manifest(data, strict_metadata=True)
        self.assertEqual(result["status"], "pass_with_warnings")
        self.assertEqual(result["coverage"]["dense_pop_edm"], 1)
        self.assertEqual(result["failure_mode_coverage"]["air_harshness"], 1)

    def test_duplicate_sanitized_labels_fail(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            audio = Path(directory) / "item.wav"
            audio.write_bytes(b"placeholder")
            data = {
                "tracks": [
                    {"label": "A/B", "path": str(audio), "start_seconds": 0.0, "duration_seconds": 5.0},
                    {"label": "A B", "path": str(audio), "start_seconds": 5.0, "duration_seconds": 5.0},
                ]
            }
            result = manifest_validator.validate_manifest(data)
        self.assertEqual(result["status"], "fail")
        self.assertIn("tracks[1].label duplicates another item after sanitization", result["errors"])

    def test_cli_writes_coverage_report(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            audio = root / "item.wav"
            audio.write_bytes(b"placeholder")
            manifest_path = root / "manifest.json"
            report_path = root / "manifest-validation.json"
            markdown_path = root / "manifest-validation.md"
            manifest_path.write_text(json.dumps(manifest(audio)), encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    str(Path(__file__).resolve().parents[1] / "scripts" / "validate_axiom_material_manifest.py"),
                    str(manifest_path),
                    "--json",
                    str(report_path),
                    "--markdown",
                    str(markdown_path),
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0)
            self.assertIn("pass_with_warnings", report_path.read_text(encoding="utf-8"))
            self.assertIn("Material Class Coverage", markdown_path.read_text(encoding="utf-8"))

    def test_metadata_template_adds_missing_decision_grade_fields(self) -> None:
        data = manifest(Path("/tmp/example.wav"))
        enriched = manifest_validator.metadata_template(data)
        item = enriched["tracks"][0]
        self.assertEqual(item["material_class"], "TODO")
        self.assertEqual(item["failure_modes"], [])
        self.assertEqual(item["license_scope"], "TODO")
        self.assertEqual(item["provenance"], "TODO")
        self.assertEqual(item["role"], "TODO")

    def test_cli_writes_metadata_template(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            audio = root / "item.wav"
            audio.write_bytes(b"placeholder")
            manifest_path = root / "manifest.json"
            template_path = root / "manifest-template.json"
            manifest_path.write_text(json.dumps(manifest(audio)), encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    str(Path(__file__).resolve().parents[1] / "scripts" / "validate_axiom_material_manifest.py"),
                    str(manifest_path),
                    "--write-metadata-template",
                    str(template_path),
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            template = json.loads(template_path.read_text(encoding="utf-8"))
        self.assertEqual(result.returncode, 0)
        self.assertEqual(template["tracks"][0]["role"], "TODO")


if __name__ == "__main__":
    unittest.main()
