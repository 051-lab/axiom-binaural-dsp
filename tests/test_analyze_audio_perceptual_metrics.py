"""Tests for offline perceptual-proxy audio metrics."""

from __future__ import annotations

import math
import struct
import sys
import tempfile
import unittest
import wave
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import analyze_audio_perceptual_metrics as metrics


def write_wav(path: Path, frames: list[tuple[float, float]], sample_rate: int = 48000) -> None:
    with wave.open(str(path), "wb") as output:
        output.setnchannels(2)
        output.setsampwidth(2)
        output.setframerate(sample_rate)
        data = bytearray()
        for left, right in frames:
            data.extend(struct.pack("<hh", int(left * 32767), int(right * 32767)))
        output.writeframes(data)


class AnalyzeAudioPerceptualMetricsTests(unittest.TestCase):
    def test_mono_low_frequency_signal_reports_centered_stereo_and_bass_energy(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "mono_bass.wav"
            frames = [
                (0.3 * math.sin(2.0 * math.pi * 90.0 * frame / 48000.0),) * 2
                for frame in range(48000)
            ]
            write_wav(path, frames)
            report = metrics.analyze(path)
        self.assertGreater(report["loudness"]["ungated_loudness_proxy_lufs"], -20.0)
        self.assertLess(report["stereo"]["side"]["rms"], 1e-9)
        self.assertAlmostEqual(report["stereo"]["left_right_correlation"], 1.0, places=5)
        self.assertGreater(
            report["erb_like_bands"]["bass"]["combined_rms_dbfs"],
            report["erb_like_bands"]["air"]["combined_rms_dbfs"],
        )

    def test_side_only_signal_reports_infinite_side_to_mid_flag(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "side.wav"
            frames = [
                (
                    0.2 * math.sin(2.0 * math.pi * 1000.0 * frame / 48000.0),
                    -0.2 * math.sin(2.0 * math.pi * 1000.0 * frame / 48000.0),
                )
                for frame in range(48000)
            ]
            write_wav(path, frames)
            report = metrics.analyze(path)
        self.assertTrue(report["stereo"]["side_to_mid_infinite"])
        self.assertAlmostEqual(report["stereo"]["left_right_correlation"], -1.0, places=5)

    def test_impulsive_signal_has_transient_contrast(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "pulses.wav"
            frames = []
            for frame in range(48000):
                value = 0.8 if frame % 4800 == 0 else 0.02 * math.sin(2.0 * math.pi * 400.0 * frame / 48000.0)
                frames.append((value, value))
            write_wav(path, frames)
            report = metrics.analyze(path)
        self.assertGreater(report["channels"]["combined"]["transient_contrast_db"], 0.5)

    def test_combined_true_peak_does_not_interpolate_between_channels(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "channel_boundary.wav"
            frames = [(0.0, 0.0)] * 32
            frames[-2] = (-0.9, 0.0)
            frames[-1] = (-0.9, 0.9)
            write_wav(path, frames)
            report = metrics.analyze(path)
        left_peak = report["channels"]["left"]["true_peak_proxy"]
        right_peak = report["channels"]["right"]["true_peak_proxy"]
        combined_peak = report["channels"]["combined"]["true_peak_proxy"]
        self.assertAlmostEqual(combined_peak, max(left_peak, right_peak), places=9)

    def test_compare_reports_exposes_directional_deltas(self) -> None:
        reference = {
            "loudness": {"ungated_loudness_proxy_lufs": -18.0, "combined_rms_dbfs": -20.0},
            "channels": {"combined": {"true_peak_proxy_dbfs": -4.0, "crest_db": 9.0, "transient_contrast_db": 2.0}},
            "stereo": {"side_to_mid_db": -12.0, "left_right_correlation": 0.4},
            "erb_like_bands": {
                "bass": {
                    "combined_rms_dbfs": -24.0,
                    "mid_rms_dbfs": -24.0,
                    "side_rms_dbfs": -42.0,
                    "side_to_mid_db": -18.0,
                    "left_right_correlation": 0.8,
                }
            },
        }
        candidate = {
            "loudness": {"ungated_loudness_proxy_lufs": -17.0, "combined_rms_dbfs": -19.0},
            "channels": {"combined": {"true_peak_proxy_dbfs": -3.5, "crest_db": 8.0, "transient_contrast_db": 2.5}},
            "stereo": {"side_to_mid_db": -10.5, "left_right_correlation": 0.3},
            "erb_like_bands": {
                "bass": {
                    "combined_rms_dbfs": -23.0,
                    "mid_rms_dbfs": -23.5,
                    "side_rms_dbfs": -40.0,
                    "side_to_mid_db": -16.5,
                    "left_right_correlation": 0.7,
                }
            },
        }
        comparison = metrics.compare_reports(reference, candidate)
        self.assertAlmostEqual(comparison["loudness"]["ungated_loudness_proxy_lufs_delta"], 1.0)
        self.assertAlmostEqual(comparison["combined"]["true_peak_proxy_db_delta"], 0.5)
        self.assertAlmostEqual(comparison["stereo"]["side_to_mid_db_delta"], 1.5)
        self.assertAlmostEqual(comparison["erb_like_bands"]["bass"]["side_rms_db_delta"], 2.0)

    def test_analyze_pair_packages_reference_candidate_and_delta(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            reference = root / "reference.wav"
            candidate = root / "candidate.wav"
            write_wav(reference, [(0.1 * math.sin(2.0 * math.pi * 500.0 * frame / 48000.0),) * 2 for frame in range(4800)])
            write_wav(candidate, [(0.2 * math.sin(2.0 * math.pi * 500.0 * frame / 48000.0),) * 2 for frame in range(4800)])
            pair = metrics.analyze_pair(reference, candidate)
        self.assertEqual(pair["reference"]["label"], "reference")
        self.assertEqual(pair["candidate"]["label"], "candidate")
        self.assertGreater(pair["candidate_minus_reference"]["loudness"]["ungated_loudness_proxy_lufs_delta"], 5.0)

    def test_markdown_contains_scope_warning_and_band_table(self) -> None:
        report = {
            "label": "test",
            "loudness": {"ungated_loudness_proxy_lufs": -12.0, "combined_rms_dbfs": -15.0},
            "channels": {"combined": {"true_peak_proxy_dbfs": -1.0, "peak_dbfs": -1.2, "crest_db": 8.0, "transient_contrast_db": 3.0}},
            "stereo": {"side_to_mid_db": -12.0, "left_right_correlation": 0.5},
            "erb_like_bands": {
                "bass": {
                    "low_hz": 60.0,
                    "high_hz": 150.0,
                    "combined_rms_dbfs": -20.0,
                    "mid_rms_dbfs": -21.0,
                    "side_rms_dbfs": -40.0,
                    "side_to_mid_db": -19.0,
                    "left_right_correlation": 0.9,
                }
            },
        }
        text = metrics.markdown(report)
        self.assertIn("not official gated LUFS", text)
        self.assertIn("ERB-Like Band Metrics", text)


if __name__ == "__main__":
    unittest.main()
