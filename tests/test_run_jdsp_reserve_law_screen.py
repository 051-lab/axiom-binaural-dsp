"""Tests for experimental reserve-law screen classification and fixture creation."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import run_jdsp_reserve_law_screen as screen


def slope_run(slope: float, peak: float, rms: float, clipped: int = 0, qualified: bool = True) -> dict:
    return {
        "reserve_slope": slope,
        "tracks": [{
            "name": "dense",
            "label": "dense",
            "thresholds": {
                "-1.0": {
                    "captures": [{"peak_dbfs": peak, "silent": False}, {"peak_dbfs": peak, "silent": False}],
                    "metric_qualification": {
                        "clipped_samples": clipped,
                        "metrics": {
                            "rms_dbfs": {"qualified": qualified, "mean_db": rms},
                            "p95_rms_dbfs": {"qualified": qualified},
                            "p99_rms_dbfs": {"qualified": qualified},
                        },
                    },
                }
            },
        }],
    }


class ReserveLawScreenTests(unittest.TestCase):
    def test_fixture_replaces_only_slider_and_reserve_expression(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "source.eel"
            target = Path(directory) / "fixture.eel"
            source.write_text(
                "slider1:4<-12,12,0.5>Sub\n@init\nslider1 = 4;\n" + screen.CURRENT_RESERVE_LINE + "\n",
                encoding="ascii",
            )
            screen.reserve_fixture(source, target, 8.0, 0.75)
            text = target.read_text(encoding="ascii")
            self.assertIn("slider1:8<", text)
            self.assertIn("slider1 = 8;", text)
            self.assertIn("(slider1 - 4.0) * 0.75", text)

    def test_safe_rms_recovery_identifies_viable_reduced_reserve(self) -> None:
        result = screen.evaluate_screen(
            [slope_run(1.0, -1.0, -16.0), slope_run(0.75, -0.7, -15.0)],
            -1.0, 1.0, -0.50, 0.50,
        )
        self.assertEqual(result["status"], "viable_reduced_reserve_identified")
        self.assertEqual(result["viable_reserve_slopes"], [0.75])

    def test_peak_pressure_rejects_reduced_reserve(self) -> None:
        result = screen.evaluate_screen(
            [slope_run(1.0, -1.0, -16.0), slope_run(0.5, -0.2, -14.0)],
            -1.0, 1.0, -0.50, 0.50,
        )
        self.assertEqual(result["status"], "full_reserve_retained")
        self.assertEqual(result["rejected_reserve_slopes"], [0.5])

    def test_viability_requires_recovery_on_every_screened_track(self) -> None:
        reference = slope_run(1.0, -1.0, -16.0)
        candidate = slope_run(0.75, -0.7, -15.0)
        candidate["tracks"].append({
            "name": "second",
            "label": "second",
            "thresholds": candidate["tracks"][0]["thresholds"],
        })
        reference["tracks"].append({
            "name": "second",
            "label": "second",
            "thresholds": {
                "-1.0": {
                    "captures": [{"peak_dbfs": -1.0, "silent": False}, {"peak_dbfs": -1.0, "silent": False}],
                    "metric_qualification": {
                        "clipped_samples": 0,
                        "metrics": {
                            "rms_dbfs": {"qualified": True, "mean_db": -15.2},
                            "p95_rms_dbfs": {"qualified": True},
                            "p99_rms_dbfs": {"qualified": True},
                        },
                    },
                }
            },
        })
        result = screen.evaluate_screen([reference, candidate], -1.0, 1.0, -0.50, 0.50)
        self.assertEqual(result["status"], "full_reserve_retained")

    def test_bad_reference_measurement_fails_screen(self) -> None:
        result = screen.evaluate_screen(
            [slope_run(1.0, -0.4, -16.0), slope_run(0.75, -0.7, -15.0)],
            -1.0, 1.0, -0.50, 0.50,
        )
        self.assertEqual(result["status"], "fail")

    def test_non_rms_repeatability_cannot_support_rms_recovery_conclusion(self) -> None:
        reference = slope_run(1.0, -1.0, -16.0)
        reference["tracks"][0]["thresholds"]["-1.0"]["metric_qualification"]["metrics"]["rms_dbfs"]["qualified"] = False
        result = screen.evaluate_screen(
            [reference, slope_run(0.75, -0.7, -15.0)],
            -1.0, 1.0, -0.50, 0.50,
        )
        self.assertEqual(result["status"], "fail")


if __name__ == "__main__":
    unittest.main()
