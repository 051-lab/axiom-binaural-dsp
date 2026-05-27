"""Tests for high-frequency width program-material screening."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import run_jdsp_high_width_screen as screen


def item(peak: float = -2.0, clipped: int = 0) -> dict:
    level = {"peak_dbfs": peak, "clipped_samples": clipped}
    return {"name": "music", "levels": {key: level for key, _percent, _label in screen.SETTINGS}}


class HighWidthScreenTests(unittest.TestCase):
    def test_fixture_changes_only_high_frequency_width_default(self) -> None:
        text = "slider5:126<0,200,5>Mid\nslider6:110<0,150,5>High\n@init\nslider5 = 126; slider6 = 110;\n"
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "accepted.eel"
            destination = Path(directory) / "restrained.eel"
            source.write_text(text, encoding="ascii")
            screen.high_width_fixture(source, destination, 105.0)
            altered = destination.read_text(encoding="ascii")
            self.assertIn("slider5:126<", altered)
            self.assertIn("slider6:105<", altered)
            self.assertIn("slider5 = 126; slider6 = 105;", altered)

    def test_products_match_screened_settings(self) -> None:
        accepted = screen.setting_descriptor("accepted", 110.0, "accepted")
        restrained = screen.setting_descriptor("restrained", 105.0, "restrained")
        neutral = screen.setting_descriptor("neutral", 100.0, "neutral")
        self.assertAlmostEqual(accepted["high_side_product"], 1.485)
        self.assertAlmostEqual(restrained["high_side_product"], 1.4175)
        self.assertAlmostEqual(neutral["high_side_product"], 1.35)

    def test_integrity_and_ceiling_classification(self) -> None:
        self.assertEqual(screen.evaluate_items([item()], -0.50)["status"], "measurement_complete")
        self.assertEqual(
            screen.evaluate_items([item(peak=-0.1)], -0.50)["status"],
            "measurement_complete_with_investigation",
        )
        self.assertEqual(screen.evaluate_items([item(clipped=1)], -0.50)["status"], "fail")


if __name__ == "__main__":
    unittest.main()
