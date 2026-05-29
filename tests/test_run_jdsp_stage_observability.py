"""Tests for same-render Axiom stage observability tooling."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import run_jdsp_stage_observability as observability


def source_text() -> str:
    return (
        "@init\n"
        "outputGain = headroomGain;\n"
        "@sample\n"
        + observability.SPATIAL_RECOMBINE_BLOCK + "\n"
        + observability.BASS_INJECTION_BLOCK + "\n"
        + observability.FINAL_OUTPUT_BLOCK
    )


class StageObservabilityTests(unittest.TestCase):
    def test_spatial_to_bass_fixture_routes_taps_without_changing_final_writeback(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "accepted.eel"
            fixture = Path(directory) / "spatial_to_bass.eel"
            source.write_text(source_text(), encoding="ascii")
            observability.stage_observability_fixture(source, fixture, "spatial_to_bass")
            altered = fixture.read_text(encoding="ascii")
            self.assertIn("axiomDiagRef = 0.0;", altered)
            self.assertIn("axiomDiagRef = (out_L + out_R) * 0.5;", altered)
            self.assertIn("axiomDiagCand = (out_L + out_R) * 0.5;", altered)
            self.assertIn("out_L = axiomDiagRef;\nout_R = axiomDiagCand;", altered)
            executable = [line for line in altered.splitlines() if line.strip() and not line.strip().startswith("//")]
            self.assertEqual(executable[-2:], ["spl0 = out_L;", "spl1 = out_R;"])

    def test_reserve_fixture_outputs_pre_and_post_reserve_paths(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "accepted.eel"
            fixture = Path(directory) / "reserve.eel"
            source.write_text(source_text(), encoding="ascii")
            observability.stage_observability_fixture(source, fixture, "reserve_pre_to_post")
            altered = fixture.read_text(encoding="ascii")
            self.assertIn("axiomDiagRef = (out_L + out_R) * 0.5;", altered)
            self.assertIn("axiomDiagCand = axiomDiagRef * outputGain;", altered)
            self.assertIn("out_L = axiomDiagRef;\nout_R = axiomDiagCand;", altered)
            self.assertNotIn("out_L *= outputGain;", altered)
            executable = [line for line in altered.splitlines() if line.strip() and not line.strip().startswith("//")]
            self.assertEqual(executable[-2:], ["spl0 = out_L;", "spl1 = out_R;"])

    def test_diagnostic_metrics_report_candidate_minus_reference_delta(self) -> None:
        capture = SimpleNamespace(
            left=[0.10] * 200,
            right=[0.20] * 200,
            sample_rate=1000,
            clip_level=0.999,
            integrity={"valid_stereo_pcm": True, "sample_rate_hz": 1000, "decoded_frames": 200},
        )
        metrics = observability.diagnostic_capture_metrics(capture)
        self.assertAlmostEqual(metrics["stage_delta"]["candidate_minus_reference"]["rms_db"], 6.0206, places=3)
        self.assertGreater(
            metrics["stage_delta"]["band_rms_candidate_minus_reference_db"]["upper_bass"],
            5.0,
        )

    def test_evaluation_distinguishes_failures_from_observation_pressure(self) -> None:
        base_metrics = {
            "silent": False,
            "clipped_samples": 0,
            "peak_dbfs": -3.0,
        }
        pairings = {
            "spatial_to_bass": {
                "stimuli": {
                    "bass_burst": {
                        "metrics": {
                            "reference": dict(base_metrics),
                            "candidate": {**base_metrics, "peak_dbfs": -0.25},
                        }
                    }
                }
            }
        }
        evaluation = observability.evaluate_pairings(pairings, -0.50)
        self.assertEqual(evaluation["status"], "measurement_complete_with_investigation")
        pairings["spatial_to_bass"]["stimuli"]["bass_burst"]["metrics"]["candidate"]["clipped_samples"] = 1
        evaluation = observability.evaluate_pairings(pairings, -0.50)
        self.assertEqual(evaluation["status"], "fail")


if __name__ == "__main__":
    unittest.main()
