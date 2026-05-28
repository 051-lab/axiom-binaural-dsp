"""Tests for dynamic exciter sensitivity program-material screening."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import run_jdsp_exciter_sensitivity_screen as screen


def item(peak: float = -2.0, clipped: int = 0) -> dict:
    level = {"peak_dbfs": peak, "clipped_samples": clipped}
    return {"name": "music", "levels": {key: level for key, _percent, _label in screen.SETTINGS}}


class ExciterSensitivityScreenTests(unittest.TestCase):
    def test_fixture_changes_only_exciter_sensitivity_default(self) -> None:
        text = "slider3:50<0,100,5>Exciter\nslider5:126<0,200,5>Mid\n@init\nslider3 = 50; slider5 = 126;\n"
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "accepted.eel"
            destination = Path(directory) / "reduced.eel"
            source.write_text(text, encoding="ascii")
            screen.exciter_fixture(source, destination, 35.0)
            altered = destination.read_text(encoding="ascii")
            self.assertIn("slider3:35<", altered)
            self.assertIn("slider5:126<", altered)
            self.assertIn("slider3 = 35; slider5 = 126;", altered)

    def test_relative_depth_matches_screened_settings(self) -> None:
        accepted = screen.setting_descriptor("accepted", 50.0, "accepted")
        reduced = screen.setting_descriptor("reduced", 35.0, "reduced")
        bypass = screen.setting_descriptor("bypass", 0.0, "bypass")
        self.assertAlmostEqual(accepted["relative_exciter_depth"], 1.0)
        self.assertAlmostEqual(reduced["relative_exciter_depth"], 0.7)
        self.assertAlmostEqual(bypass["relative_exciter_depth"], 0.0)

    def test_integrity_and_ceiling_classification(self) -> None:
        self.assertEqual(screen.evaluate_items([item()], -0.50)["status"], "measurement_complete")
        self.assertEqual(
            screen.evaluate_items([item(peak=-0.1)], -0.50)["status"],
            "measurement_complete_with_investigation",
        )
        self.assertEqual(screen.evaluate_items([item(clipped=1)], -0.50)["status"], "fail")


if __name__ == "__main__":
    unittest.main()
