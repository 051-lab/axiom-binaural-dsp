#!/usr/bin/env python3
"""Tests for private local-material configuration and report classification."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import run_jdsp_local_material as material


def capture_report(reference_peak: float, candidate_peak: float, clipping: int = 0, reference_clipping: int = 0) -> dict:
    return {
        "captures": {
            "reference": {"channels": {"combined": {"peak_dbfs": reference_peak, "silent": False, "clipped_samples": reference_clipping}}},
            "candidate": {"channels": {"combined": {"peak_dbfs": candidate_peak, "silent": False, "clipped_samples": clipping}}},
        }
    }


class LocalMaterialTests(unittest.TestCase):
    def test_manifest_reads_private_excerpt_configuration(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            audio = root / "track.flac"
            audio.write_bytes(b"local")
            manifest = root / "manifest.json"
            manifest.write_text(
                json.dumps({"tracks": [{"label": "Track A chorus", "path": str(audio), "start_seconds": 12.5, "duration_seconds": 15.0}]}),
                encoding="utf-8",
            )
            items = material.read_manifest(manifest)
            self.assertEqual(items[0]["name"], "Track_A_chorus")
            self.assertEqual(items[0]["duration_seconds"], 15.0)

    def test_local_pressure_is_investigation_not_failure(self) -> None:
        reports = [{"name": "selection", "report": capture_report(-0.08, -0.08)}]
        checks = material.evaluate_reports(reports, -0.50, 0.15)
        self.assertEqual(material.report_status(checks), "pass_with_investigation")

    def test_candidate_clipping_fails_local_report(self) -> None:
        reports = [{"name": "selection", "report": capture_report(-2.0, -2.0, clipping=2)}]
        checks = material.evaluate_reports(reports, -0.50, 0.15)
        self.assertEqual(material.report_status(checks), "fail")

    def test_integrity_detail_exposes_baseline_and_candidate_clipping(self) -> None:
        reports = [{"name": "selection", "report": capture_report(0.0, 0.0, clipping=2, reference_clipping=3)}]
        checks = material.evaluate_reports(reports, -0.50, 0.15)
        self.assertIn("baseline clipping=3, candidate clipping=2", checks[0]["detail"])


if __name__ == "__main__":
    unittest.main()
