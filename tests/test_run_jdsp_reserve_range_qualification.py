"""Tests for reduced-reserve full elevated-control-range qualification."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import run_jdsp_reserve_range_qualification as qualification


def track(
    name: str = "dense",
    peak: float = -0.8,
    rms: float = -14.0,
    clipped: int = 0,
    qualified: bool = True,
    material_class: str | None = None,
) -> dict:
    return {
        "name": name,
        "label": name,
        "material_class": material_class,
        "thresholds": {"-1.0": {
            "captures": [{"peak_dbfs": peak, "silent": False}, {"peak_dbfs": peak, "silent": False}],
            "metric_qualification": {
                "clipped_samples": clipped,
                "metrics": {"rms_dbfs": {"qualified": qualified, "mean_db": rms}},
            },
        }},
    }


def slope_run(slope: float, sliders: list[tuple[float, dict]]) -> dict:
    return {
        "reserve_slope": slope,
        "slider_runs": [{"slider_db": slider_db, "tracks": [entry]} for slider_db, entry in sliders],
    }


class ReserveRangeQualificationTests(unittest.TestCase):
    def test_complete_safe_range_identifies_viable_slope(self) -> None:
        result = qualification.evaluate_range(
            [slope_run(0.75, [(6.0, track()), (8.0, track()), (10.0, track()), (12.0, track())])],
            -1.0, -0.50, [12.0, 10.0, 8.0, 6.0],
        )
        self.assertEqual(result["status"], "viable_reduced_reserve_range_identified")
        self.assertEqual(result["viable_reserve_slopes"], [0.75])

    def test_headroom_crossing_rejects_slope_without_full_coverage(self) -> None:
        result = qualification.evaluate_range(
            [slope_run(0.5, [(6.0, track(peak=-0.2))])],
            -1.0, -0.50, [12.0, 10.0, 8.0, 6.0],
        )
        self.assertEqual(result["status"], "no_reduced_reserve_range_qualifies")
        self.assertEqual(result["rejected_reserve_slopes"], [0.5])

    def test_declared_flawed_source_clipping_is_investigation_not_rejection(self) -> None:
        result = qualification.evaluate_range(
            [slope_run(0.5, [(6.0, track(peak=0.0, clipped=2, qualified=False, material_class="flawed_source"))])],
            -1.0, -0.50, [6.0],
        )
        self.assertEqual(result["status"], "viable_reduced_reserve_range_identified")
        self.assertEqual(result["rejected_reserve_slopes"], [])
        self.assertEqual(result["checks"][0]["status"], "investigate")

    def test_unstable_level_measurement_fails_range(self) -> None:
        result = qualification.evaluate_range(
            [slope_run(0.75, [(6.0, track(qualified=False))])],
            -1.0, -0.50, [6.0, 8.0],
        )
        self.assertEqual(result["status"], "fail")

    def test_incomplete_nonrejected_coverage_fails_range(self) -> None:
        result = qualification.evaluate_range(
            [slope_run(0.75, [(6.0, track())])],
            -1.0, -0.50, [6.0, 8.0],
        )
        self.assertEqual(result["status"], "fail")


if __name__ == "__main__":
    unittest.main()
