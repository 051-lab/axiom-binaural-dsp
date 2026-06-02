"""Tests for accepted-setting dense-material stress classification."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import run_jdsp_accepted_stress as stress


def track(
    peaks: list[float],
    clipped: int = 0,
    rms_qualified: bool = True,
    silent: bool = False,
    material_class: str | None = None,
) -> dict:
    return {
        "label": "dense material",
        "name": "dense_material",
        "material_class": material_class,
        "thresholds": {
            "-1.0": {
                "captures": [{"peak_dbfs": peak, "silent": silent} for peak in peaks],
                "metric_qualification": {
                    "clipped_samples": clipped,
                    "metrics": {
                        "peak_dbfs": {"qualified": True},
                        "rms_dbfs": {"qualified": rms_qualified},
                        "crest_db": {"qualified": False},
                        "p95_rms_dbfs": {"qualified": rms_qualified},
                        "p99_rms_dbfs": {"qualified": False},
                    },
                },
            }
        },
    }


class AcceptedStressTests(unittest.TestCase):
    def test_near_ceiling_baseline_pressure_is_recorded_not_failed(self) -> None:
        evaluation = stress.evaluate_tracks([track([-0.55, -0.47, -0.52])], -1.0, -0.50)
        self.assertEqual(evaluation["status"], "pass_with_investigation")
        self.assertEqual(evaluation["checks"][0]["status"], "pass")
        self.assertEqual(evaluation["checks"][1]["status"], "investigate")

    def test_clipping_fails_accepted_setting_gate(self) -> None:
        evaluation = stress.evaluate_tracks([track([-0.40, 0.0], clipped=1)], -1.0, -0.50)
        self.assertEqual(evaluation["status"], "fail")
        self.assertIn("clipped", evaluation["checks"][0]["detail"])

    def test_flawed_source_clipping_is_investigation_not_failure(self) -> None:
        evaluation = stress.evaluate_tracks(
            [track([-0.40, 0.0], clipped=1, rms_qualified=False, material_class="flawed_source")],
            -1.0,
            -0.50,
        )
        self.assertEqual(evaluation["status"], "pass_with_investigation")
        self.assertEqual(evaluation["checks"][0]["status"], "investigate")
        self.assertIn("flawed-source", evaluation["checks"][0]["detail"])

    def test_safe_peak_detail_does_not_claim_limiter_pressure(self) -> None:
        evaluation = stress.evaluate_tracks([track([-0.8, -0.7])], -1.0, -0.50)
        self.assertEqual(evaluation["status"], "pass")
        self.assertIn("within observation boundary", evaluation["checks"][1]["detail"])

    def test_unrepeatable_level_profile_fails_gate(self) -> None:
        evaluation = stress.evaluate_tracks([track([-1.2, -1.1], rms_qualified=False)], -1.0, -0.50)
        self.assertEqual(evaluation["status"], "fail")
        self.assertIn("no repeated level metric", evaluation["checks"][0]["detail"])


if __name__ == "__main__":
    unittest.main()
