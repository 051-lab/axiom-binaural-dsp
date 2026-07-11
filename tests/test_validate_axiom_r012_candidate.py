"""Regression tests for the approved R011-to-R012 candidate boundary."""

from __future__ import annotations

import importlib.util
import pathlib
import sys
import tempfile
import unittest


REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
VALIDATOR_PATH = REPO_ROOT / "scripts" / "validate_axiom_r012_candidate.py"
BASELINE_PATH = REPO_ROOT / "src" / "axiom_binaural_dsp_v4.1.4.11.eel"
CANDIDATE_PATH = REPO_ROOT / "src" / "axiom_clean_r012.eel"


def load_validator():
    spec = importlib.util.spec_from_file_location("validate_axiom_r012_candidate", VALIDATOR_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load {VALIDATOR_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


validator = load_validator()


class R012CandidateBoundaryTests(unittest.TestCase):
    def test_repository_candidate_matches_approved_boundary(self) -> None:
        self.assertEqual(validator.validate(BASELINE_PATH, CANDIDATE_PATH), [])

    def test_unrelated_crossover_change_fails(self) -> None:
        self.assert_mutation_fails("LowPassFilter_Set(150, q)", "LowPassFilter_Set(160, q)")

    def test_unrelated_exciter_change_fails(self) -> None:
        self.assert_mutation_fails("HighPassFilter_Set(11000, q)", "HighPassFilter_Set(10000, q)")

    def test_unrelated_stft_change_fails(self) -> None:
        self.assert_mutation_fails("binFloor * 2.5", "binFloor * 2.4")

    def test_interpolation_order_change_fails(self) -> None:
        self.assert_mutation_fails(
            "sat_l = (sat_l_mid + sat_l_now) * 0.5;\nprev_sub_l = sub_l;",
            "prev_sub_l = sub_l;\nsat_l = (sat_l_mid + sat_l_now) * 0.5;",
        )

    def test_unapproved_lfo_processing_fails(self) -> None:
        self.assert_mutation_fails("@sample\n", "@sample\nlfo = sin(lfo_phase);\n")

    def assert_mutation_fails(self, old: str, new: str) -> None:
        text = CANDIDATE_PATH.read_text(encoding="utf-8")
        self.assertIn(old, text)
        with tempfile.TemporaryDirectory() as directory:
            candidate = pathlib.Path(directory) / "axiom_clean_r012.eel"
            candidate.write_text(text.replace(old, new, 1), encoding="utf-8")
            failures = validator.validate(BASELINE_PATH, candidate)
        self.assertTrue(failures)
        self.assertIn("outside the approved R012 boundary", "\n".join(failures))


if __name__ == "__main__":
    unittest.main()
