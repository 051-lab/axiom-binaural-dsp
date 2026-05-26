"""Tests for program-material stereo-width characterization."""

from __future__ import annotations

import math
import sys
import tempfile
import unittest
import wave
import struct
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import analyze_jdsp_transfer as transfer
import run_jdsp_width_material_screen as screen


def write_tone(path: Path, frequency: float, side_ratio: float) -> None:
    rate = 48000
    frames = []
    for frame in range(rate):
        mid = 0.2 * math.sin(2.0 * math.pi * frequency * frame / rate)
        side = mid * side_ratio
        frames.append((mid + side, mid - side))
    with wave.open(str(path), "wb") as output:
        output.setnchannels(2)
        output.setsampwidth(2)
        output.setframerate(rate)
        output.writeframes(
            b"".join(
                struct.pack("<hh", int(left * 32767), int(right * 32767))
                for left, right in frames
            )
        )


def item(peak: float = -2.0, clipped: int = 0) -> dict:
    level = {"peak_dbfs": peak, "clipped_samples": clipped}
    return {"name": "music", "levels": {"unity_width": level, "accepted_width": level}}


class WidthMaterialScreenTests(unittest.TestCase):
    def test_band_metrics_recognize_upper_bass_side_ratio(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "tone.wav"
            write_tone(path, 100.0, 0.5)
            bands = screen.band_metrics(transfer.read_stereo_wav(path))
            self.assertAlmostEqual(bands["upper_bass"]["side_to_mid_db"], 20.0 * math.log10(0.5), delta=0.03)

    def test_delta_requires_both_values(self) -> None:
        self.assertIsNone(screen.delta(None, -2.0))
        self.assertIsNone(screen.delta(1.0, None))
        self.assertEqual(screen.delta(3.0, 1.5), 1.5)

    def test_integrity_and_ceiling_classification(self) -> None:
        result = screen.evaluate_items([item()], -0.50)
        self.assertEqual(result["status"], "measurement_complete")
        result = screen.evaluate_items([item(peak=-0.2)], -0.50)
        self.assertEqual(result["status"], "measurement_complete_with_investigation")
        result = screen.evaluate_items([item(clipped=1)], -0.50)
        self.assertEqual(result["status"], "fail")


if __name__ == "__main__":
    unittest.main()
