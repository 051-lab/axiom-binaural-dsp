#!/usr/bin/env python3
"""Tests for deterministic real-host input stimuli."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import generate_jdsp_stimuli as stimuli


class StimulusTests(unittest.TestCase):
    def test_bass_pressure_probe_is_included(self) -> None:
        self.assertIn("bass_pressure_90hz", [name for name, _ in stimuli.STIMULI])

    def test_bass_pressure_probe_is_correlated_and_reaches_target_peak(self) -> None:
        total_frames = stimuli.DEFAULT_SAMPLE_RATE * 2
        values = [
            stimuli.bass_pressure_90hz(frame, stimuli.DEFAULT_SAMPLE_RATE, total_frames)
            for frame in range(total_frames)
        ]
        self.assertTrue(all(left == right for left, right in values))
        self.assertAlmostEqual(max(abs(left) for left, _ in values), 0.65, places=6)
        self.assertEqual(values[0], (0.0, 0.0))


if __name__ == "__main__":
    unittest.main()
