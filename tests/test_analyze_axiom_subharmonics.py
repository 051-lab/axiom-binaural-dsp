"""Tests for deterministic Axiom sub-harmonic branch characterization."""

from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import analyze_axiom_subharmonics as analyzer


class SubHarmonicsAnalyzerTests(unittest.TestCase):
    def test_slider_gain_scales_generated_branch_in_decibels(self) -> None:
        low = analyzer.render_probe(45.0, 0.0)
        high = analyzer.render_probe(45.0, 8.0)
        delta = high["injection_rms_dbfs"] - low["injection_rms_dbfs"]
        self.assertAlmostEqual(delta, 8.0, places=9)

    def test_terminal_reserve_reduces_branch_peak_by_one_db(self) -> None:
        result = analyzer.render_probe(60.0, 4.0)
        delta = (
            result["branch_peak_dbfs_before_downstream_processing"]
            - result["terminal_headroom_applied_peak_dbfs_before_downstream_processing"]
        )
        self.assertAlmostEqual(delta, 1.0, places=9)

    def test_representative_report_is_finite_and_passes_gain_law(self) -> None:
        report = analyzer.create_report((45.0, 90.0), (0.0, 4.0), (0.20, 0.35))
        self.assertTrue(report["checks"]["gain_law_pass"])
        self.assertEqual(len(report["probes"]), 8)
        for row in report["probes"]:
            for name in (
                "injection_rms_dbfs",
                "injection_relative_to_dry_db",
                "third_harmonic_dbfs",
                "fifth_harmonic_dbfs",
                "terminal_headroom_applied_peak_dbfs_before_downstream_processing",
            ):
                self.assertTrue(math.isfinite(row[name]), name)

    def test_strong_high_slider_probe_exposes_branch_local_headroom_pressure(self) -> None:
        report = analyzer.create_report((90.0,), (12.0,), (0.65,))
        maximum = report["maximum_branch_peak_probe"]
        self.assertEqual(maximum["input_amplitude"], 0.65)
        self.assertEqual(maximum["slider_db"], 12.0)
        self.assertGreater(maximum["terminal_headroom_applied_peak_dbfs_before_downstream_processing"], 0.0)


if __name__ == "__main__":
    unittest.main()
