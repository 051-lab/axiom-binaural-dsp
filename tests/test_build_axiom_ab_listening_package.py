"""Tests for local A/B listening package generation."""

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

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import build_axiom_ab_listening_package as ab_package


def write_wav(path: Path, amplitude: float, frequency: float = 440.0, frames: int = 4800) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as output:
        output.setnchannels(2)
        output.setsampwidth(2)
        output.setframerate(48000)
        data = bytearray()
        for frame in range(frames):
            value = amplitude * math.sin(2.0 * math.pi * frequency * frame / 48000.0)
            sample = int(max(-1.0, min(1.0, value)) * 32767)
            data.extend(struct.pack("<hh", sample, sample))
        output.writeframes(data)


class BuildAxiomAbListeningPackageTests(unittest.TestCase):
    def test_build_package_recommends_candidate_gain_for_louder_candidate(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            reference = root / "reference"
            candidate = root / "candidate"
            write_wav(reference / "tone.wav", 0.1)
            write_wav(candidate / "tone.wav", 0.2)
            report = ab_package.build_package(reference, candidate, root / "package", seed=1)
            pair = report["pairs"][0]
            self.assertEqual(report["status"], "pass_with_warnings")
            self.assertLess(pair["candidate_gain_to_match_reference_db"], -5.5)
            self.assertTrue((root / "package" / "audio" / "tone.wav" / "A.wav").is_file())

    def test_missing_matched_file_fails_package(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            reference = root / "reference"
            candidate = root / "candidate"
            write_wav(reference / "only-reference.wav", 0.1)
            candidate.mkdir()
            report = ab_package.build_package(reference, candidate, root / "package")
        self.assertEqual(report["status"], "fail")
        self.assertTrue(any("missing candidate WAVs" in error for error in report["errors"]))

    def test_safety_trim_is_applied_when_matched_candidate_would_exceed_ceiling(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            reference = root / "reference"
            candidate = root / "candidate"
            write_wav(reference / "tone.wav", 0.9)
            write_wav(candidate / "tone.wav", 0.45)
            report = ab_package.build_package(reference, candidate, root / "package", true_peak_ceiling_dbfs=-3.0)
        pair = report["pairs"][0]
        self.assertLess(pair["shared_safety_trim_db"], 0.0)
        self.assertTrue(any("safety trim" in warning for warning in pair["warnings"]))

    def test_markdown_contains_blinded_assignments_and_listening_rules(self) -> None:
        report = {
            "label": "test",
            "status": "pass",
            "pairs": [
                {
                    "name": "tone.wav",
                    "status": "pass",
                    "assignments": {
                        "A": {"role": "reference", "recommended_gain_db": 0.0},
                        "B": {"role": "candidate", "recommended_gain_db": -1.0},
                    },
                    "candidate_gain_to_match_reference_db": -1.0,
                    "perceptual_metrics": {
                        "candidate_minus_reference": {
                            "loudness": {"ungated_loudness_proxy_lufs_delta": 1.0}
                        }
                    },
                }
            ],
            "errors": [],
            "warnings": [],
        }
        text = ab_package.markdown(report)
        self.assertIn("Axiom A/B Listening Package", text)
        self.assertIn("Keep A/B slot identity hidden", text)

    def test_cli_writes_package_reports(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            reference = root / "reference"
            candidate = root / "candidate"
            output = root / "package"
            write_wav(reference / "tone.wav", 0.1)
            write_wav(candidate / "tone.wav", 0.1)
            result = subprocess.run(
                [
                    sys.executable,
                    str(Path(__file__).resolve().parents[1] / "scripts" / "build_axiom_ab_listening_package.py"),
                    str(reference),
                    str(candidate),
                    str(output),
                    "--seed",
                    "7",
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            report = json.loads((output / "ab-listening-package.json").read_text(encoding="utf-8"))
            self.assertEqual(result.returncode, 0)
            self.assertEqual(report["pair_count"], 1)
            self.assertTrue((output / "ab-listening-package.md").is_file())


if __name__ == "__main__":
    unittest.main()
