"""Tests for generated low-level exciter probe screening."""

from __future__ import annotations

import sys
import tempfile
import unittest
import wave
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import run_jdsp_exciter_probe_screen as probe_screen


def summary_item(
    name: str,
    air_bypass: float,
    air_reduced: float,
    presence_bypass: float = 0.0,
) -> dict[str, object]:
    bands = {}
    for band, _low, _high in probe_screen.exciter.EXCITER_BANDS_HZ:
        bypass = presence_bypass if band == "presence_edge" else air_bypass
        bands[band] = {
            "accepted_minus_bypass_rms_db": bypass,
            "accepted_minus_reduced_rms_db": air_reduced,
            "accepted_minus_bypass_side_to_mid_db": 0.0,
        }
    return {"name": name, "label": name, "bands": bands}


def wav_peak(path: Path) -> float:
    with wave.open(str(path), "rb") as source:
        raw = source.readframes(source.getnframes())
    peak = 0
    for index in range(0, len(raw), 2):
        peak = max(peak, abs(int.from_bytes(raw[index:index + 2], "little", signed=True)))
    return peak / 32768.0


class ExciterProbeScreenTests(unittest.TestCase):
    def test_generated_probes_are_deterministic_and_level_ordered(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            first = probe_screen.generate_probes(root / "a", tuple(probe_screen.PROBES), 48000, 1.0)
            second = probe_screen.generate_probes(root / "b", tuple(probe_screen.PROBES), 48000, 1.0)
            self.assertEqual([item["name"] for item in first], [item["name"] for item in second])
            for left, right in zip(first, second):
                self.assertEqual(
                    Path(left["source_path"]).read_bytes(),
                    Path(right["source_path"]).read_bytes(),
                )
            low_peak = wav_peak(Path(first[0]["source_path"]))
            high = next(item for item in first if item["name"] == "high_level_air_control")
            self.assertGreater(wav_peak(Path(high["source_path"])), low_peak * 4.0)

    def test_activation_summary_converts_variant_minus_accepted_to_accepted_minus_variant(self) -> None:
        items = [
            {
                "name": "probe",
                "label": "Probe",
                "bands": {
                    band: {
                        "bypass_minus_accepted_band_rms_db": -3.0,
                        "reduced_minus_accepted_band_rms_db": -1.0,
                        "bypass_minus_accepted_side_to_mid_db": 0.5,
                    }
                    for band, _low, _high in probe_screen.exciter.EXCITER_BANDS_HZ
                },
            }
        ]
        summary = probe_screen.activation_summary(items)
        values = summary[0]["bands"]["air"]
        self.assertEqual(values["accepted_minus_bypass_rms_db"], 3.0)
        self.assertEqual(values["accepted_minus_reduced_rms_db"], 1.0)
        self.assertEqual(values["accepted_minus_bypass_side_to_mid_db"], -0.5)

    def test_activation_evaluation_passes_intended_probe_pattern(self) -> None:
        summary = [
            summary_item("low_level_air_activation", air_bypass=0.25, air_reduced=0.10),
            summary_item("low_level_dull_control", air_bypass=0.03, air_reduced=0.02),
            summary_item("low_level_sibilance_texture", air_bypass=0.08, air_reduced=0.03, presence_bypass=0.20),
            summary_item("high_level_air_control", air_bypass=0.04, air_reduced=0.02),
        ]
        evaluation = probe_screen.evaluate_activation(summary)
        self.assertEqual(evaluation["status"], "measurement_complete")
        self.assertTrue(all(check["status"] == "pass" for check in evaluation["checks"]))

    def test_activation_evaluation_flags_weak_or_excessive_probe_behavior(self) -> None:
        summary = [
            summary_item("low_level_air_activation", air_bypass=0.01, air_reduced=0.03),
            summary_item("low_level_dull_control", air_bypass=0.35, air_reduced=0.05),
            summary_item("low_level_sibilance_texture", air_bypass=0.08, air_reduced=0.03, presence_bypass=0.80),
            summary_item("high_level_air_control", air_bypass=0.31, air_reduced=0.06),
        ]
        evaluation = probe_screen.evaluate_activation(summary)
        self.assertEqual(evaluation["status"], "measurement_complete_with_investigation")
        investigate = [check["name"] for check in evaluation["checks"] if check["status"] == "investigate"]
        self.assertIn("low_level_air_activation_lift", investigate)
        self.assertIn("low_level_air_activation_depth_order", investigate)
        self.assertIn("low_level_dull_control_restraint", investigate)
        self.assertIn("low_level_sibilance_texture_restraint", investigate)
        self.assertIn("high_level_air_control_restraint", investigate)

    def test_combined_evaluation_keeps_integrity_fail_as_failure(self) -> None:
        integrity = {"status": "fail", "checks": [{"name": "clip", "status": "fail", "detail": "clipped"}]}
        activation = {"status": "measurement_complete", "checks": [{"name": "lift", "status": "pass", "detail": "ok"}]}
        combined = probe_screen.combine_evaluations(integrity, activation)
        self.assertEqual(combined["status"], "fail")
        self.assertEqual(combined["checks"][0]["category"], "integrity")
        self.assertEqual(combined["checks"][1]["category"], "activation")

    def test_markdown_reports_generated_probe_scope(self) -> None:
        report = {
            "evaluation": {"status": "measurement_complete", "checks": []},
            "master_limiter_threshold_db": -1.0,
            "ceiling_dbfs": -6.0,
            "activation_summary": [
                {
                    "label": "Low-level air activation",
                    "bands": {
                        band: {
                            "accepted_minus_bypass_rms_db": 1.0,
                            "accepted_minus_reduced_rms_db": 0.5,
                            "accepted_minus_bypass_side_to_mid_db": 0.0,
                        }
                        for band, _low, _high in probe_screen.exciter.EXCITER_BANDS_HZ
                    },
                }
            ],
            "probes": [{"label": "Probe", "description": "Generated"}],
        }
        text = probe_screen.markdown(report)
        self.assertIn("Low-Level Exciter Probe Screen", text)
        self.assertIn("Generated", text)


if __name__ == "__main__":
    unittest.main()
