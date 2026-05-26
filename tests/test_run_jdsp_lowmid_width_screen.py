"""Tests for low-mid width program-material screening."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import run_jdsp_lowmid_width_screen as screen


def item(peak: float = -2.0, clipped: int = 0) -> dict:
    level = {"peak_dbfs": peak, "clipped_samples": clipped}
    return {"name": "music", "levels": {key: level for key, _percent, _label in screen.SETTINGS}}


class LowMidWidthScreenTests(unittest.TestCase):
    def test_fixture_changes_only_low_mid_width_default(self) -> None:
        text = "slider5:140<0,200,5>Mid\n@init\nslider5 = 140;\nslider6 = 110;\n"
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "accepted.eel"
            destination = Path(directory) / "restrained.eel"
            source.write_text(text, encoding="ascii")
            screen.lowmid_fixture(source, destination, 126.0)
            altered = destination.read_text(encoding="ascii")
            self.assertIn("slider5:126<", altered)
            self.assertIn("slider5 = 126;", altered)
            self.assertIn("slider6 = 110;", altered)

    def test_products_match_screened_settings(self) -> None:
        accepted = screen.setting_descriptor("accepted", 140.0, "accepted")
        restrained = screen.setting_descriptor("restrained", 126.0, "restrained")
        conservative = screen.setting_descriptor("conservative", 115.0, "conservative")
        self.assertAlmostEqual(accepted["low_mid_side_product"], 1.89)
        self.assertAlmostEqual(restrained["low_mid_side_product"], 1.701)
        self.assertAlmostEqual(conservative["low_mid_side_product"], 1.5525)

    def test_integrity_and_ceiling_classification(self) -> None:
        result = screen.evaluate_items([item()], -0.50)
        self.assertEqual(result["status"], "measurement_complete")
        result = screen.evaluate_items([item(peak=-0.1)], -0.50)
        self.assertEqual(result["status"], "measurement_complete_with_investigation")
        result = screen.evaluate_items([item(clipped=1)], -0.50)
        self.assertEqual(result["status"], "fail")


if __name__ == "__main__":
    unittest.main()
