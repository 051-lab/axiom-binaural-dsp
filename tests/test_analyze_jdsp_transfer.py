#!/usr/bin/env python3
"""Deterministic self-tests for the offline end-to-end host-path analyzer."""

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
import analyze_jdsp_transfer as analyzer


SAMPLE_RATE = 48000
FREQUENCIES = (1000.0, 4000.0)


def pcm16(value: float) -> int:
    return int(round(max(-1.0, min(1.0, value)) * 32767))


def write_wav(path: Path, frames: list[tuple[float, float]]) -> None:
    with wave.open(str(path), "wb") as output:
        output.setnchannels(2)
        output.setsampwidth(2)
        output.setframerate(SAMPLE_RATE)
        output.writeframes(b"".join(struct.pack("<hh", pcm16(left), pcm16(right)) for left, right in frames))


def matrix_output(
    stimulus: list[tuple[float, float]],
    pre_roll: int,
    delay: int,
    mm: float = 0.0,
    ms: float = 0.0,
    sm: float = 0.0,
    ss: float = 0.0,
) -> list[tuple[float, float]]:
    output = [(0.0, 0.0)] * (pre_roll + len(stimulus) + delay + 8)
    for index, (left, right) in enumerate(stimulus):
        mid = (left + right) * 0.5
        side = (left - right) * 0.5
        output_mid = mm * mid + sm * side
        output_side = ms * mid + ss * side
        output[pre_roll + delay + index] = (
            output_mid + output_side,
            output_mid - output_side,
        )
    return output


class TransferAnalyzerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.directory = tempfile.TemporaryDirectory()
        self.root = Path(self.directory.name)

    def tearDown(self) -> None:
        self.directory.cleanup()

    def report_for(
        self, stimulus: list[tuple[float, float]], output: list[tuple[float, float]], pre_roll: int = 0
    ) -> dict:
        input_path = self.root / "stimulus.wav"
        output_path = self.root / "processed.wav"
        write_wav(input_path, stimulus)
        write_wav(output_path, output)
        return analyzer.create_report(
            analyzer.read_stereo_wav(input_path),
            analyzer.read_stereo_wav(output_path),
            label="fixture",
            capture_pre_roll_ms=pre_roll * 1000.0 / SAMPLE_RATE,
            frequencies_hz=FREQUENCIES,
        )

    def test_low_level_impulse_retains_delay_and_gain_without_phase_alignment(self) -> None:
        stimulus = [(0.0, 0.0)] * 128
        stimulus[24] = (0.2, 0.2)
        pre_roll = 20
        delay = 12
        gain = 10.0 ** (-1.0 / 20.0)
        report = self.report_for(stimulus, matrix_output(stimulus, pre_roll, delay, mm=gain), pre_roll)

        self.assertEqual(report["path_under_measurement"], "end_to_end_host_path")
        self.assertTrue(report["qualification"]["qualified"])
        self.assertEqual(
            report["format"]["phase_alignment"],
            "no data-driven or correlation alignment; timing includes any caller-supplied "
            "known playback lead-in",
        )
        self.assertIn("not measured host latency", report["format"]["capture_pre_roll_semantics"])
        for point in report["mid_side_transfer_matrix"]["M_to_M"]["points"]:
            self.assertTrue(point["valid"])
            self.assertAlmostEqual(point["magnitude_db"], -1.0, delta=0.01)
            self.assertTrue(point["group_delay_valid"])
            self.assertAlmostEqual(point["group_delay_ms"], delay * 1000.0 / SAMPLE_RATE, delta=0.001)
        self.assertTrue(report["mid_side_transfer_matrix"]["M_to_S"]["column_identifiable"])
        self.assertEqual(report["mid_side_transfer_matrix"]["S_to_S"]["valid_bin_count"], 0)

    def test_mono_probe_reports_mid_to_side_leakage(self) -> None:
        stimulus = [(0.0, 0.0)] * 128
        stimulus[17] = (0.18, 0.18)
        report = self.report_for(stimulus, matrix_output(stimulus, 0, 3, mm=0.5, ms=0.125))

        self.assertTrue(report["mid_side_transfer_matrix"]["M_to_S"]["column_identifiable"])
        self.assertFalse(report["mid_side_transfer_matrix"]["S_to_M"]["column_identifiable"])
        for point in report["mid_side_transfer_matrix"]["M_to_S"]["points"]:
            self.assertTrue(point["valid"])
            self.assertAlmostEqual(point["magnitude_db"], 20.0 * math.log10(0.125), delta=0.02)

    def test_side_probe_reports_side_to_mid_leakage(self) -> None:
        stimulus = [(0.0, 0.0)] * 128
        stimulus[17] = (0.18, -0.18)
        report = self.report_for(stimulus, matrix_output(stimulus, 0, 3, sm=0.25, ss=0.5))

        self.assertFalse(report["mid_side_transfer_matrix"]["M_to_M"]["column_identifiable"])
        self.assertTrue(report["mid_side_transfer_matrix"]["S_to_M"]["column_identifiable"])
        for point in report["mid_side_transfer_matrix"]["S_to_M"]["points"]:
            self.assertTrue(point["valid"])
            self.assertAlmostEqual(point["magnitude_db"], 20.0 * math.log10(0.25), delta=0.02)

    def test_general_stereo_probe_has_no_identifiable_matrix_column(self) -> None:
        stimulus = [(0.0, 0.0)] * 128
        stimulus[17] = (0.18, 0.08)
        report = self.report_for(stimulus, matrix_output(stimulus, 0, 0, mm=0.5, ss=0.5))

        for response in report["mid_side_transfer_matrix"].values():
            self.assertFalse(response["column_identifiable"])
            self.assertEqual(response["valid_bin_count"], 0)

    def test_output_above_minus_six_dbfs_is_unqualified(self) -> None:
        stimulus = [(0.0, 0.0)] * 64
        stimulus[5] = (0.2, 0.2)
        output = [(0.0, 0.0)] * 64
        output[5] = (0.55, 0.55)
        report = self.report_for(stimulus, output)

        self.assertFalse(report["qualification"]["qualified"])
        self.assertEqual(report["qualification"]["status"], "unqualified")
        self.assertTrue(any("exceeds" in reason for reason in report["qualification"]["reasons"]))
        self.assertFalse(report["measurement_level"]["post_jdsp_processed_output"]["clipped"])

    def test_silent_processed_output_is_unqualified_at_configurable_threshold(self) -> None:
        stimulus = [(0.0, 0.0)] * 64
        stimulus[5] = (0.2, 0.2)
        output = [(0.0, 0.0)] * 64
        input_path = self.root / "silence_input.wav"
        output_path = self.root / "silence_output.wav"
        write_wav(input_path, stimulus)
        write_wav(output_path, output)
        report = analyzer.create_report(
            analyzer.read_stereo_wav(input_path),
            analyzer.read_stereo_wav(output_path),
            frequencies_hz=FREQUENCIES,
            silence_dbfs=-80.0,
        )

        self.assertFalse(report["qualification"]["qualified"])
        self.assertEqual(report["qualification"]["processed_output_silence_threshold_dbfs"], -80.0)
        self.assertTrue(any("silence threshold" in reason for reason in report["qualification"]["reasons"]))
        self.assertIsNone(report["measurement_level"]["post_jdsp_processed_output"]["peak_dbfs"])

    def test_cli_emits_reports_and_returns_nonzero_for_clipping(self) -> None:
        stimulus_path = self.root / "cli_input.wav"
        output_path = self.root / "cli_output.wav"
        json_path = self.root / "result.json"
        markdown_path = self.root / "result.md"
        stimulus = [(0.0, 0.0)] * 64
        stimulus[9] = (0.1, 0.1)
        output = [(0.0, 0.0)] * 64
        output[9] = (1.0, 1.0)
        write_wav(stimulus_path, stimulus)
        write_wav(output_path, output)
        command = [
            sys.executable,
            str(Path(analyzer.__file__)),
            str(stimulus_path),
            str(output_path),
            "--json",
            str(json_path),
            "--markdown",
            str(markdown_path),
            "--frequencies-hz",
            "1000",
        ]
        result = subprocess.run(command, text=True, capture_output=True, check=False)

        self.assertEqual(result.returncode, 2)
        generated = json.loads(json_path.read_text(encoding="ascii"))
        self.assertTrue(generated["measurement_level"]["post_jdsp_processed_output"]["clipped"])
        markdown = markdown_path.read_text(encoding="ascii")
        self.assertIn("end_to_end_host_path", markdown)
        self.assertIn("No data-driven or correlation alignment", markdown)


if __name__ == "__main__":
    unittest.main()
