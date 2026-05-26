"""Tests for accepted-baseline width and mono compatibility audit tooling."""

from __future__ import annotations

import sys
import tempfile
import unittest
import wave
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import run_jdsp_width_mono_audit as audit


def path_report(path_name: str, values: dict[float, float | None]) -> dict:
    points = [
        {"requested_frequency_hz": frequency, "valid": True, "magnitude_db": value}
        for frequency, value in values.items()
    ]
    return {"mid_side_transfer_matrix": {path_name: {"points": points}}}


def probe_report(source_path: str, leakage_value: float | None = None, peak: float = -20.0) -> dict:
    report = {
        "qualification": {"qualified": True, "reasons": []},
        "measurement_level": {
            "post_jdsp_processed_output": {"clipped_samples": 0, "peak_dbfs": peak}
        },
        "mid_side_transfer_matrix": {
            "M_to_M": {"points": []},
            "M_to_S": {"points": []},
            "S_to_M": {"points": []},
            "S_to_S": {"points": []},
        },
    }
    report["mid_side_transfer_matrix"][source_path]["points"] = [
        {"requested_frequency_hz": frequency, "valid": True, "magnitude_db": leakage_value}
        for frequency in audit.FREQUENCIES_HZ
    ]
    return report


def modes(leakage_value: float | None = None) -> dict:
    result = {}
    for name in ("unity_width", "accepted_width"):
        mid = probe_report("M_to_S", leakage_value)
        side = probe_report("S_to_M", leakage_value)
        mid["mid_side_transfer_matrix"]["M_to_M"]["points"] = [
            {"requested_frequency_hz": frequency, "valid": True, "magnitude_db": -1.0}
            for frequency in audit.FREQUENCIES_HZ
        ]
        side["mid_side_transfer_matrix"]["S_to_S"]["points"] = [
            {"requested_frequency_hz": frequency, "valid": True, "magnitude_db": -1.0}
            for frequency in audit.FREQUENCIES_HZ
        ]
        result[name] = {"pure_mid": mid, "pure_side": side}
    return result


class WidthMonoAuditTests(unittest.TestCase):
    def test_unity_fixture_changes_only_width_defaults(self) -> None:
        text = (
            "slider2:135<0,200,5>Global\nslider5:140<0,200,5>Mid\nslider6:110<0,150,5>High\n"
            "@init\nslider2 = 135; slider5 = 140; slider6 = 110;\n"
        )
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "accepted.eel"
            fixture = Path(directory) / "unity.eel"
            source.write_text(text, encoding="ascii")
            audit.unity_width_fixture(source, fixture)
            altered = fixture.read_text(encoding="ascii")
            self.assertIn("slider2:100<", altered)
            self.assertIn("slider5:100<", altered)
            self.assertIn("slider6:100<", altered)
            self.assertIn("slider2 = 100; slider5 = 100; slider6 = 100;", altered)

    def test_probe_generator_writes_pure_mid_and_pure_side_pcm(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            mid = Path(directory) / "mid.wav"
            side = Path(directory) / "side.wav"
            audit.write_probe(mid, "pure_mid")
            audit.write_probe(side, "pure_side")
            for path, opposite in ((mid, False), (side, True)):
                with wave.open(str(path), "rb") as source:
                    data = source.readframes(source.getnframes())
                nonzero = False
                for index in range(0, len(data), 4):
                    left = int.from_bytes(data[index:index + 2], "little", signed=True)
                    right = int.from_bytes(data[index + 2:index + 4], "little", signed=True)
                    if left:
                        nonzero = True
                        self.assertEqual(right, -left if opposite else left)
                self.assertTrue(nonzero)

    def test_clean_low_leakage_is_measurement_complete(self) -> None:
        evaluation = audit.evaluate_modes(modes(-90.0), -70.0)
        self.assertEqual(evaluation["status"], "measurement_complete")
        self.assertTrue(all(check["status"] == "pass" for check in evaluation["checks"]))

    def test_leakage_requests_investigation_and_clipping_fails(self) -> None:
        observed = modes(-45.0)
        evaluation = audit.evaluate_modes(observed, -70.0)
        self.assertEqual(evaluation["status"], "measurement_complete_with_investigation")
        observed["accepted_width"]["pure_side"]["measurement_level"]["post_jdsp_processed_output"]["clipped_samples"] = 1
        evaluation = audit.evaluate_modes(observed, -70.0)
        self.assertEqual(evaluation["status"], "fail")

    def test_width_map_reports_accepted_minus_unity(self) -> None:
        result = modes()
        for point in result["accepted_width"]["pure_side"]["mid_side_transfer_matrix"]["S_to_S"]["points"]:
            point["magnitude_db"] = 4.5
        mapped = audit.width_map(result)
        self.assertAlmostEqual(mapped[0]["accepted_minus_unity_db"], 5.5)


if __name__ == "__main__":
    unittest.main()
