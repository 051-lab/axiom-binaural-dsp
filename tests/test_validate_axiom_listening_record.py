"""Tests for structured Axiom listening record validation."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import validate_axiom_listening_record as listening


def valid_record() -> dict:
    return {
        "schema_version": 1,
        "recorded_at": "2026-06-01T18:00:00-05:00",
        "listener": "local tester",
        "axiom_version": "v4.1.4.11",
        "comparison_version": "v4.1.4.10",
        "decision": "accept",
        "acceptance_rationale": "Cleaner center image without losing bass impact.",
        "device": "Android phone",
        "route": "RootlessJamesDSP wired output",
        "host_settings": {
            "jdsp_limiter_threshold_db": -1.0,
            "jdsp_limiter_release_ms": 60.0,
            "jdsp_postgain_db": 0.0,
            "crossfeed_enabled": False,
        },
        "slider_settings": {
            "sub_harmonics_gain_db": 4.0,
            "global_side_width_percent": 135.0,
            "fletcher_munson_sensitivity_percent": 50.0,
            "low_mid_width_percent": 126.0,
            "high_width_percent": 110.0,
            "stft_resonance_suppression_percent": 50.0,
        },
        "material": [
            {
                "label": "private track chorus",
                "source_type": "private_owned",
                "license_scope": "local listening only",
                "comparison_target": "v4.1.4.10",
                "timestamp_or_excerpt": "1:12-1:42",
                "notes": "Dense low end and bright synth stack.",
            }
        ],
        "observations": {
            "bass": "Controlled and extended.",
            "punch": "Strong transient hit.",
            "center_image": "Vocal stays centered.",
            "width": "Wide without hollow center.",
            "air": "Open but not brittle.",
            "harshness": "No obvious sibilant edge.",
            "loudness": "Comparable after normal listening adjustment.",
            "fatigue": "No short-session fatigue.",
            "artifacts": "No muting, crackle, or pumping heard.",
            "overall": "Accepted for this route.",
        },
    }


class ListeningRecordValidationTests(unittest.TestCase):
    def test_valid_record_passes_with_private_material_warning(self) -> None:
        result = listening.validate_record(valid_record())
        self.assertEqual(result["status"], "pass")
        self.assertIn("keep the full record out of public git", result["warnings"][0])

    def test_missing_slider_setting_fails(self) -> None:
        record = valid_record()
        del record["slider_settings"]["high_width_percent"]
        result = listening.validate_record(record)
        self.assertEqual(result["status"], "fail")
        self.assertIn("slider_settings.high_width_percent must be numeric", result["errors"])

    def test_acceptance_requires_rationale(self) -> None:
        record = valid_record()
        record["acceptance_rationale"] = ""
        result = listening.validate_record(record)
        self.assertEqual(result["status"], "fail")
        self.assertIn("acceptance_rationale must be set when decision is accept", result["errors"])

    def test_markdown_exposes_validation_and_observations(self) -> None:
        record = valid_record()
        validation = listening.validate_record(record)
        text = listening.markdown(record, validation)
        self.assertIn("Validation: **PASS**", text)
        self.assertIn("center_image", text)

    def test_cli_writes_validation_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            record_path = root / "record.json"
            report_path = root / "validation.json"
            markdown_path = root / "record.md"
            record_path.write_text(json.dumps(valid_record()), encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    str(Path(__file__).resolve().parents[1] / "scripts" / "validate_axiom_listening_record.py"),
                    str(record_path),
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
            self.assertTrue(report_path.read_text(encoding="utf-8"))
            self.assertIn("Axiom Listening Record", markdown_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
