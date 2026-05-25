#!/usr/bin/env python3
"""Tests for deterministic original program-like corpus generation."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import generate_axiom_program_corpus as corpus


class CorpusGenerationTests(unittest.TestCase):
    def test_corpus_contains_three_bass_heavy_passages(self) -> None:
        self.assertEqual(
            [name for name, _ in corpus.PROGRAMS],
            ["sub_kick_sequence", "sustained_bass_synth", "dense_low_end_mix"],
        )

    def test_every_program_is_peak_normalized_and_non_silent(self) -> None:
        for name, signal in corpus.PROGRAMS:
            with self.subTest(name=name):
                frames = corpus.render_program(signal, sample_rate=8000, duration_s=4.0)
                peak = max(abs(value) for frame in frames for value in frame)
                self.assertAlmostEqual(peak, corpus.TARGET_PEAK, places=9)
                self.assertTrue(any(abs(left - right) > 1.0e-9 for left, right in frames))


if __name__ == "__main__":
    unittest.main()
