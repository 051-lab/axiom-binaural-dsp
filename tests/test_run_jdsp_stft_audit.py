"""Tests for non-production same-render STFT stage audit tooling."""

from __future__ import annotations

import sys
import struct
import tempfile
import unittest
import wave
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import run_jdsp_stft_audit as audit


def mode_report(*, clipped: int = 0, silent: bool = False) -> dict:
    report = {}
    for stimulus in audit.MONO_STIMULUS_NAMES:
        report[stimulus] = {
            "captures": {
                "reference": {"channels": {"combined": {"silent": False, "clipped_samples": 0}}},
                "candidate": {"channels": {"combined": {"silent": silent, "clipped_samples": clipped}}},
            }
        }
    return report


class StftAuditTests(unittest.TestCase):
    def test_fixtures_create_same_render_unity_and_active_audits(self) -> None:
        source_text = (
            "slider7:50<0,100,5>STFT\n@init\nslider7 = 50;\n"
            + audit.STFT_STAGE_HEADER
            + "out_L = stftOutL[stftBufPos];\n"
            + audit.FINAL_STAGE_HEADER
            + "spl0 = out_L;\nspl1 = out_R;\n"
        )
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "accepted.eel"
            unity = Path(directory) / "unity.eel"
            active = Path(directory) / "active.eel"
            source.write_text(source_text, encoding="ascii")
            audit.stft_fixture(source, unity, 0.0)
            audit.stft_fixture(source, active, 50.0)
            unity_text = unity.read_text(encoding="ascii")
            active_text = active.read_text(encoding="ascii")
            self.assertIn("slider7:0<", unity_text)
            self.assertIn("slider7 = 0;", unity_text)
            self.assertIn("out_L = stftOutL[stftBufPos];", unity_text)
            self.assertIn("stftDiagnosticDry = out_L;", unity_text)
            self.assertIn("out_L = stftDiagnosticDry;", unity_text)
            self.assertIn("slider7:50<", active_text)
            self.assertIn("out_L = stftDiagnosticDry;", active_text)

    def test_integrity_only_is_gated_without_claiming_residual_quality(self) -> None:
        checks = audit.evaluate_modes({"unity_round_trip": mode_report(), "accepted_suppression": mode_report()})
        self.assertEqual(audit.report_status(checks), "measurement_complete")
        self.assertTrue(all(check["status"] == "pass" for check in checks))

    def test_clipping_or_silence_fails_audit_integrity(self) -> None:
        checks = audit.evaluate_modes(
            {"unity_round_trip": mode_report(clipped=1), "accepted_suppression": mode_report(silent=True)}
        )
        self.assertEqual(audit.report_status(checks), "fail")

    def test_transient_metrics_report_added_latency_and_energy_spread(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            dry = Path(directory) / "dry.wav"
            processed = Path(directory) / "processed.wav"
            frames = 128
            dry_values = [0.0] * frames
            processed_values = [0.0] * frames
            dry_values[20] = 0.5
            processed_values[30] = 0.35
            processed_values[31] = 0.20
            processed_values[32] = 0.15
            for path, values in ((dry, dry_values), (processed, processed_values)):
                with wave.open(str(path), "wb") as output:
                    output.setnchannels(2)
                    output.setsampwidth(2)
                    output.setframerate(48000)
                    output.writeframes(
                        b"".join(
                            struct.pack("<hh", int(value * 32767), int(value * 32767))
                            for value in values
                        )
                    )
            metrics = audit.transient_metrics(dry, processed)
            self.assertEqual(metrics["peak_arrival_delta_frames"], 10)
            self.assertAlmostEqual(metrics["peak_arrival_delta_ms"], 10 * 1000.0 / 48000, places=6)
            self.assertGreater(metrics["energy_span_delta_ms"], 0.0)


if __name__ == "__main__":
    unittest.main()
