"""Tests for same-script terminal-limiter threshold classification."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import run_jdsp_limiter_sweep as sweep


def threshold(peak: float, rms: float, crest: float, p95: float, qualified: bool = True, clipped: int = 0) -> dict:
    return {
        "aggregate": {
            "mean_peak_dbfs": peak,
            "mean_rms_dbfs": rms,
            "mean_crest_db": crest,
            "mean_p95_rms_dbfs": p95,
            "mean_p99_rms_dbfs": p95,
        },
        "metric_qualification": {
            "clipped_samples": clipped,
            "metrics": {
                name: {"mean_db": value, "qualified": qualified}
                for name, value in {
                    "peak_dbfs": peak, "rms_dbfs": rms, "crest_db": crest,
                    "p95_rms_dbfs": p95, "p99_rms_dbfs": p95,
                }.items()
            },
        },
        "repeatability": {"status": "pass" if qualified else "fail"},
    }


class LimiterSweepTests(unittest.TestCase):
    def test_detects_reliable_accepted_threshold_change(self) -> None:
        tracks = [{
            "label": "dense electronic",
            "thresholds": {
                "0.0": threshold(-0.20, -8.00, 7.80, -5.0),
                "-1.0": threshold(-0.95, -8.20, 7.25, -5.2),
            },
        }]
        result = sweep.classify(tracks, 0.0, -1.0, 0.15)
        self.assertEqual(result["status"], "limiter_participation_detected")
        self.assertEqual(result["affected_tracks"][0]["accepted_minus_reference"]["peak_dbfs"], -0.75)

    def test_does_not_invent_participation_inside_effect_floor(self) -> None:
        tracks = [{
            "label": "stable",
            "thresholds": {
                "0.0": threshold(-2.00, -10.00, 8.00, -7.0),
                "-1.0": threshold(-2.04, -10.03, 7.99, -7.03),
            },
        }]
        result = sweep.classify(tracks, 0.0, -1.0, 0.15)
        self.assertEqual(result["status"], "no_reliable_limiter_participation_detected")

    def test_repeatability_failure_prevents_a_conclusion(self) -> None:
        tracks = [{
            "label": "unstable",
            "thresholds": {
                "0.0": threshold(-0.20, -8.00, 7.80, -5.0, False),
                "-1.0": threshold(-0.95, -8.20, 7.25, -5.2),
            },
        }]
        result = sweep.classify(tracks, 0.0, -1.0, 0.15)
        self.assertEqual(result["status"], "unqualified")

    def test_clipped_reference_prevents_participation_claim(self) -> None:
        tracks = [{
            "label": "clipped",
            "thresholds": {
                "0.0": threshold(0.0, -8.00, 8.00, -5.0, clipped=4),
                "-1.0": threshold(-0.60, -8.30, 7.70, -5.3),
            },
        }]
        result = sweep.classify(tracks, 0.0, -1.0, 0.15)
        self.assertEqual(result["status"], "unqualified")


if __name__ == "__main__":
    unittest.main()
