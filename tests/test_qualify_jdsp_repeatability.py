#!/usr/bin/env python3
"""Deterministic temporary-WAV tests for repeated capture qualification."""

from __future__ import annotations

import json
import math
import struct
import subprocess
import sys
import tempfile
import unittest
import wave
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
QUALIFIER = ROOT / "scripts" / "qualify_jdsp_repeatability.py"
RATE = 8000
FRAMES = 2400
POLICY = [
    "--max-peak-spread-db",
    "0.10",
    "--max-rms-spread-db",
    "0.10",
    "--min-correlation",
    "0.999",
]


def probe(shift=0, gain=1.0, alternate=False):
    samples = []
    for frame in range(FRAMES):
        source = frame - shift
        if 200 <= source < FRAMES - 200:
            time_s = source / RATE
            first = 0.42 * math.sin(2.0 * math.pi * 311.0 * time_s)
            second = 0.24 * math.sin(2.0 * math.pi * 997.0 * time_s + 0.29)
            marker = 0.5 if source == 415 else 0.0
            value = gain * (first + second + marker)
            if alternate:
                value = gain * 0.45 * math.sin(2.0 * math.pi * 733.0 * time_s + 0.6)
        else:
            value = 0.0
        integer = max(-32768, min(32767, round(value * 32767)))
        samples.append((integer, integer))
    return samples


def write_wav(path, samples, channels=2):
    with wave.open(str(path), "wb") as destination:
        destination.setnchannels(channels)
        destination.setsampwidth(2)
        destination.setframerate(RATE)
        if channels == 2:
            payload = b"".join(struct.pack("<hh", left, right) for left, right in samples)
        else:
            payload = b"".join(struct.pack("<h", left) for left, _ in samples)
        destination.writeframes(payload)


class QualificationTests(unittest.TestCase):
    def invoke(self, directory, names, extra_args=()):
        report = Path(directory) / "report.json"
        markdown = Path(directory) / "report.md"
        command = [
            sys.executable,
            str(QUALIFIER),
            *[str(Path(directory) / name) for name in names],
            *POLICY,
            "--json",
            str(report),
            "--markdown",
            str(markdown),
            *extra_args,
        ]
        result = subprocess.run(command, check=False, capture_output=True, text=True)
        return result, json.loads(report.read_text(encoding="ascii")), markdown.read_text(encoding="ascii")

    def test_identical_metric_runs_pass_with_qualified_relative_jitter(self):
        with tempfile.TemporaryDirectory() as directory:
            write_wav(Path(directory) / "one.wav", probe())
            write_wav(Path(directory) / "two.wav", probe(shift=3))
            write_wav(Path(directory) / "three.wav", probe(shift=1))
            result, report, markdown = self.invoke(
                directory,
                ["one.wav", "two.wav", "three.wav"],
                ["--max-relative-jitter-ms", "0.5"],
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(report["status"], "pass")
            self.assertAlmostEqual(report["variance"]["rms"]["spread_db"], 0.0, places=5)
            self.assertTrue(report["alignment"]["relative_jitter"]["qualified"])
            self.assertIn("Status: **PASS**", markdown)
            self.assertIn("Maximum peak spread (dB) | 0.100000", markdown)
            self.assertIn("not measured or qualified", markdown)

    def test_format_rejection_fails_qualification(self):
        with tempfile.TemporaryDirectory() as directory:
            write_wav(Path(directory) / "one.wav", probe())
            write_wav(Path(directory) / "mono.wav", probe(), channels=1)
            write_wav(Path(directory) / "three.wav", probe())
            result, report, _ = self.invoke(directory, ["one.wav", "mono.wav", "three.wav"])
            self.assertEqual(result.returncode, 1)
            self.assertEqual(report["status"], "fail")
            self.assertIn("invalid or unsupported stereo PCM WAV", " ".join(report["qualification"]["failures"]))

    def test_silence_rejection_fails_qualification(self):
        with tempfile.TemporaryDirectory() as directory:
            write_wav(Path(directory) / "one.wav", probe())
            write_wav(Path(directory) / "silent.wav", [(0, 0)] * FRAMES)
            write_wav(Path(directory) / "three.wav", probe())
            result, report, _ = self.invoke(directory, ["one.wav", "silent.wav", "three.wav"])
            self.assertEqual(result.returncode, 1)
            self.assertIn("capture is silent", " ".join(report["qualification"]["failures"]))

    def test_frame_count_mismatch_fails_qualification(self):
        with tempfile.TemporaryDirectory() as directory:
            write_wav(Path(directory) / "one.wav", probe())
            write_wav(Path(directory) / "short.wav", probe()[:-12])
            write_wav(Path(directory) / "three.wav", probe())
            result, report, _ = self.invoke(directory, ["one.wav", "short.wav", "three.wav"])
            self.assertEqual(result.returncode, 1)
            self.assertIn("format or frame count differs", " ".join(report["qualification"]["failures"]))

    def test_clipped_capture_fails_qualification(self):
        with tempfile.TemporaryDirectory() as directory:
            write_wav(Path(directory) / "one.wav", probe())
            clipped = probe()
            clipped[415] = (32767, 32767)
            write_wav(Path(directory) / "clipped.wav", clipped)
            write_wav(Path(directory) / "three.wav", probe())
            result, report, _ = self.invoke(directory, ["one.wav", "clipped.wav", "three.wav"])
            self.assertEqual(result.returncode, 1)
            self.assertIn("clipped channel samples", " ".join(report["qualification"]["failures"]))
            self.assertEqual(report["alignment"]["runs"], [])

    def test_peak_and_rms_variance_exceeding_limits_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            write_wav(Path(directory) / "one.wav", probe())
            write_wav(Path(directory) / "louder.wav", probe(gain=1.10))
            write_wav(Path(directory) / "three.wav", probe())
            result, report, _ = self.invoke(directory, ["one.wav", "louder.wav", "three.wav"])
            self.assertEqual(result.returncode, 1)
            failures = " ".join(report["qualification"]["failures"])
            self.assertIn("peak spread", failures)
            self.assertIn("RMS spread", failures)

    def test_correlation_and_opt_in_jitter_are_gated(self):
        with tempfile.TemporaryDirectory() as directory:
            write_wav(Path(directory) / "one.wav", probe())
            write_wav(Path(directory) / "late.wav", probe(shift=20))
            write_wav(Path(directory) / "three.wav", probe())
            result, report, _ = self.invoke(
                directory,
                ["one.wav", "late.wav", "three.wav"],
                ["--max-relative-jitter-ms", "0.5"],
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("relative jitter", " ".join(report["qualification"]["failures"]))
            write_wav(Path(directory) / "different.wav", probe(alternate=True))
            result, report, _ = self.invoke(
                directory,
                ["one.wav", "different.wav", "three.wav"],
                ["--max-relative-jitter-ms", "0.5"],
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("aligned correlation", " ".join(report["qualification"]["failures"]))
            self.assertFalse(report["alignment"]["relative_jitter"]["qualified"])

    def test_at_least_three_captures_are_required(self):
        with tempfile.TemporaryDirectory() as directory:
            write_wav(Path(directory) / "one.wav", probe())
            write_wav(Path(directory) / "two.wav", probe())
            result = subprocess.run(
                [
                    sys.executable,
                    str(QUALIFIER),
                    str(Path(directory) / "one.wav"),
                    str(Path(directory) / "two.wav"),
                    *POLICY,
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn("at least three", result.stderr)


if __name__ == "__main__":
    unittest.main()
