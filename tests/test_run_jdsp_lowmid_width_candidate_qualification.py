"""Tests for restrained low-mid width candidate qualification."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import run_jdsp_lowmid_width_candidate_qualification as qualification


def item(delta: float = -0.90, peak: float = -1.0, clipped: int = 0) -> dict:
    bands = {
        band: {"candidate_minus_accepted_side_to_mid_db": delta}
        for band, _low, _high in qualification.LOW_MID_BANDS_HZ
    }
    levels = {
        "accepted_140": {"peak_dbfs": -1.0, "clipped_samples": 0},
        "candidate_126": {"peak_dbfs": peak, "clipped_samples": clipped},
    }
    return {"name": "music", "levels": levels, "bands": bands}


class LowMidWidthCandidateQualificationTests(unittest.TestCase):
    def test_candidate_scope_allows_description_and_slider5_defaults_only(self) -> None:
        baseline = "desc: Axiom v4.1.4.9\nslider5:140<0,200,5>Mid\n@init\nslider5 = 140;\nslider6 = 110;\n"
        candidate = "desc: Axiom Binaural DSP v4.1.4.10 (Restrained Low-Mid Width Candidate)\nslider5:126<0,200,5>Mid\n@init\nslider5 = 126;\nslider6 = 110;\n"
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "accepted.eel"
            target = Path(directory) / "candidate.eel"
            source.write_text(baseline, encoding="ascii")
            target.write_text(candidate, encoding="ascii")
            qualification.validate_restrained_candidate(source, target)

    def test_candidate_scope_rejects_an_extra_processing_change(self) -> None:
        baseline = "desc: Base\nslider5:140<0,200,5>Mid\n@init\nslider5 = 140;\nslider6 = 110;\n"
        candidate = "desc: Candidate\nslider5:126<0,200,5>Mid\n@init\nslider5 = 126;\nslider6 = 100;\n"
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "accepted.eel"
            target = Path(directory) / "candidate.eel"
            source.write_text(baseline, encoding="ascii")
            target.write_text(candidate, encoding="ascii")
            with self.assertRaises(qualification.QualificationError):
                qualification.validate_restrained_candidate(source, target)

    def test_expected_reduction_passes_and_terminal_observation_is_recorded(self) -> None:
        result = qualification.evaluate_items([item()], -0.50)
        self.assertEqual(result["status"], "pass")
        result = qualification.evaluate_items([item(peak=-0.20)], -0.50)
        self.assertEqual(result["status"], "pass_with_investigation")

    def test_missing_reduction_or_clipping_fails(self) -> None:
        self.assertEqual(qualification.evaluate_items([item(delta=-0.10)], -0.50)["status"], "fail")
        self.assertEqual(qualification.evaluate_items([item(clipped=1)], -0.50)["status"], "fail")


if __name__ == "__main__":
    unittest.main()
