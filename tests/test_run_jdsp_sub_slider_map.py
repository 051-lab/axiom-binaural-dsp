"""Tests for dense-material Sub Harmonics Gain map classification."""

from __future__ import annotations

import sys
import subprocess
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import run_jdsp_sub_slider_map as slider_map


def slider(
    slider_db: float,
    peak: float,
    clipped: int = 0,
    qualified: bool = True,
    silent: bool = False,
    rms: float = -12.0,
    material_class: str | None = None,
) -> dict:
    return {
        "slider_db": slider_db,
        "tracks": [{
            "label": "dense",
            "name": "dense",
            "material_class": material_class,
            "thresholds": {
                "-1.0": {
                    "captures": [{"peak_dbfs": peak, "silent": silent}, {"peak_dbfs": peak, "silent": silent}],
                    "metric_qualification": {
                        "clipped_samples": clipped,
                        "metrics": {
                            "peak_dbfs": {"qualified": qualified},
                            "rms_dbfs": {"qualified": qualified, "mean_db": rms},
                            "crest_db": {"qualified": qualified},
                            "p95_rms_dbfs": {"qualified": qualified},
                            "p99_rms_dbfs": {"qualified": qualified},
                        },
                    },
                }
            },
        }],
    }


class SubSliderMapTests(unittest.TestCase):
    def test_cli_rejects_two_repetitions_before_host_work(self) -> None:
        script = Path(__file__).resolve().parents[1] / "scripts" / "run_jdsp_sub_slider_map.py"
        result = subprocess.run(
            [sys.executable, str(script), "--repetitions", "2", "missing.eel", "missing.json", "/tmp/out"],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("at least 3", result.stderr)

    def test_elevated_clipping_records_boundary_without_rejecting_default(self) -> None:
        evaluation = slider_map.evaluate_map(
            [slider(4.0, -0.7), slider(8.0, -0.4), slider(12.0, 0.0, clipped=3)],
            -1.0, 4.0, -0.50,
        )
        self.assertEqual(evaluation["status"], "usable_range_boundary_detected")
        self.assertEqual(evaluation["highest_tested_unclipped_slider_db"], 8.0)
        self.assertEqual(evaluation["clipped_slider_values_db"], [12.0])

    def test_default_clipping_fails_map(self) -> None:
        evaluation = slider_map.evaluate_map([slider(4.0, 0.0, clipped=1)], -1.0, 4.0, -0.50)
        self.assertEqual(evaluation["status"], "fail")

    def test_flawed_source_clipping_is_investigation_not_range_boundary(self) -> None:
        evaluation = slider_map.evaluate_map(
            [slider(4.0, 0.0, clipped=1, qualified=False, material_class="flawed_source")],
            -1.0,
            4.0,
            -0.50,
        )
        self.assertEqual(evaluation["status"], "pass_with_investigation")
        self.assertEqual(evaluation["clipped_slider_values_db"], [])
        self.assertEqual(evaluation["checks"][0]["status"], "investigate")

    def test_pressure_without_clipping_is_investigation(self) -> None:
        evaluation = slider_map.evaluate_map([slider(4.0, -0.7), slider(8.0, -0.2)], -1.0, 4.0, -0.50)
        self.assertEqual(evaluation["status"], "pass_with_investigation")
        self.assertEqual(evaluation["pressure_slider_values_db"], [8.0])

    def test_unqualified_level_measurement_fails_map(self) -> None:
        evaluation = slider_map.evaluate_map([slider(4.0, -1.0, qualified=False)], -1.0, 4.0, -0.50)
        self.assertEqual(evaluation["status"], "fail")

    def test_repeatable_level_retreat_is_investigation_finding(self) -> None:
        evaluation = slider_map.evaluate_map(
            [slider(4.0, -0.7, rms=-12.0), slider(8.0, -0.9, rms=-14.0)],
            -1.0, 4.0, -0.50,
        )
        self.assertEqual(evaluation["status"], "pass_with_investigation")
        self.assertAlmostEqual(evaluation["level_retreat_findings"][0]["rms_delta_from_default_db"], -2.0)


if __name__ == "__main__":
    unittest.main()
