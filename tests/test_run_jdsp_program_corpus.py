#!/usr/bin/env python3
"""Tests for program-like corpus result classification."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import run_jdsp_program_corpus as corpus


def report(reference_peak: float, candidate_peak: float, clipped: int = 0) -> dict:
    return {
        "captures": {
            "reference": {"channels": {"combined": {"peak_dbfs": reference_peak, "silent": False, "clipped_samples": 0}}},
            "candidate": {"channels": {"combined": {"peak_dbfs": candidate_peak, "silent": False, "clipped_samples": clipped}}},
        }
    }


class CorpusResultTests(unittest.TestCase):
    def reports(self, peak: float) -> dict:
        return {name: report(peak, peak) for name in corpus.PROGRAM_NAMES}

    def test_near_ceiling_is_investigation_not_failure(self) -> None:
        checks = corpus.make_checks(self.reports(-0.08), -0.50, 0.15)
        self.assertEqual(corpus.status(checks), "pass_with_investigation")

    def test_transparency_or_clipping_failure_fails(self) -> None:
        reports = self.reports(-4.0)
        reports["dense_low_end_mix"] = report(-4.0, -2.0, clipped=1)
        checks = corpus.make_checks(reports, -0.50, 0.15)
        self.assertEqual(corpus.status(checks), "fail")


if __name__ == "__main__":
    unittest.main()
