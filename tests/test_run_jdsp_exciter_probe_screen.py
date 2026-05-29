"""Tests for generated low-level exciter probe screening."""

from __future__ import annotations

import sys
import tempfile
import unittest
import wave
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import run_jdsp_exciter_probe_screen as probe_screen


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
