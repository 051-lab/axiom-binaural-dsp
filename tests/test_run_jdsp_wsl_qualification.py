#!/usr/bin/env python3
"""Tests for managed real-host qualification report logic."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
import sys
import os

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import run_jdsp_wsl_qualification as qualification


def suite_report(deltas: dict[str, float], clipping: int = 0) -> dict:
    stimuli = {}
    for stimulus, delta in deltas.items():
        stimuli[stimulus] = {
            "captures": {
                "reference": {"channels": {"combined": {"peak_dbfs": -1.0, "clipped_samples": 0}}},
                "candidate": {
                    "channels": {"combined": {"peak_dbfs": -1.0 + delta, "clipped_samples": clipping}}
                },
            }
        }
    return {"stimuli": stimuli}


def boundary_report(reference_peak: float, candidate_peak: float, clipping: int = 0) -> dict:
    return {
        "captures": {
            "reference": {"channels": {"combined": {"peak_dbfs": reference_peak, "clipped_samples": 0}}},
            "candidate": {"channels": {"combined": {"peak_dbfs": candidate_peak, "clipped_samples": clipping}}},
        }
    }


def local_material_report(status: str, check_status: str, clipping: int = 0, silent: bool = False) -> dict:
    return {
        "status": status,
        "checks": [{"name": "local_track_integrity", "status": check_status, "detail": ""}],
        "items": [
            {
                "report": {
                    "captures": {
                        "reference": {"channels": {"combined": {"clipped_samples": 0}}},
                        "candidate": {"channels": {"combined": {"clipped_samples": clipping, "silent": silent}}},
                    }
                }
            }
        ],
    }


class QualificationTests(unittest.TestCase):
    def test_ancestor_processes_are_protected_from_route_cleanup_matching(self) -> None:
        protected = qualification.ancestor_pids()
        self.assertIn(os.getpid(), protected)
        self.assertIn(os.getppid(), protected)

    def test_slider_fixture_changes_only_slider_default_sites(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "source.eel"
            target = Path(directory) / "target.eel"
            source.write_text("slider1:4<-12,12,0.5>Gain\n@init\nslider1 = 4;\n", encoding="ascii")
            qualification.slider_fixture(source, target, 8.0)
            self.assertEqual(
                target.read_text(encoding="ascii"),
                "slider1:8<-12,12,0.5>Gain\n@init\nslider1 = 8;\n",
            )

    def test_checks_accept_transparent_default_and_bass_reserve(self) -> None:
        default = suite_report({name: 0.0 for name in qualification.CONTINUOUS_PROBES})
        boosted = suite_report(
            {"bass_burst": -4.0, "correlated_mono": -4.0, "side_only": -4.0, "bass_pressure_90hz": -1.0}
        )
        boundary = boundary_report(-0.08, -6.38)
        checks = qualification.check_report(default, boosted, boundary, 0.15, 8.0, 0.10, 4.0, -0.50)
        self.assertTrue(all(check["status"] == "pass" for check in checks))
        self.assertEqual(qualification.report_status(checks), "pass")

    def test_checks_reject_missing_boundary_margin(self) -> None:
        default = suite_report({name: 0.0 for name in qualification.CONTINUOUS_PROBES})
        boosted = suite_report(
            {"bass_burst": -4.0, "correlated_mono": -4.0, "side_only": -4.0, "bass_pressure_90hz": -1.0}
        )
        checks = qualification.check_report(
            default, boosted, boundary_report(-0.08, -2.0), 0.15, 8.0, 0.10, 4.0, -0.50
        )
        self.assertEqual(checks[-1]["status"], "fail")
        self.assertEqual(qualification.report_status(checks), "fail")

    def test_reduced_reserve_candidate_checks_absolute_boundary_margin(self) -> None:
        default = suite_report({name: 0.0 for name in qualification.CONTINUOUS_PROBES})
        boosted = suite_report(
            {"bass_burst": 1.0, "correlated_mono": 1.0, "side_only": 1.0, "bass_pressure_90hz": -1.0}
        )
        checks = qualification.check_report(
            default,
            boosted,
            boundary_report(-6.38, -4.38),
            0.15,
            8.0,
            0.10,
            4.0,
            -0.50,
            1.0,
            "terminal_ceiling",
        )
        self.assertTrue(all(check["status"] == "pass" for check in checks))
        self.assertEqual(checks[-1]["name"], "maximum_bass_boundary_terminal_margin")

    def test_reduced_reserve_candidate_rejects_boundary_near_ceiling(self) -> None:
        default = suite_report({name: 0.0 for name in qualification.CONTINUOUS_PROBES})
        boosted = suite_report(
            {"bass_burst": 1.0, "correlated_mono": 1.0, "side_only": 1.0, "bass_pressure_90hz": -1.0}
        )
        checks = qualification.check_report(
            default,
            boosted,
            boundary_report(-2.40, -0.40),
            0.15,
            8.0,
            0.10,
            4.0,
            -0.50,
            1.0,
            "terminal_ceiling",
        )
        self.assertEqual(checks[-1]["status"], "fail")

    def test_local_material_integrity_only_failure_is_retryable_without_clipping(self) -> None:
        report = local_material_report("fail", "fail")
        self.assertTrue(qualification.local_material_retry_eligible(report))

    def test_local_material_clipping_failure_is_not_retryable(self) -> None:
        report = local_material_report("fail", "fail", clipping=1)
        self.assertFalse(qualification.local_material_retry_eligible(report))

    def test_default_pressure_near_ceiling_is_investigation_not_regression(self) -> None:
        default = suite_report({name: 0.0 for name in qualification.CONTINUOUS_PROBES})
        default["stimuli"]["bass_pressure_90hz"]["captures"]["reference"]["channels"]["combined"]["peak_dbfs"] = -0.08
        default["stimuli"]["bass_pressure_90hz"]["captures"]["candidate"]["channels"]["combined"]["peak_dbfs"] = -0.08
        boosted = suite_report(
            {"bass_burst": -4.0, "correlated_mono": -4.0, "side_only": -4.0, "bass_pressure_90hz": -1.0}
        )
        checks = qualification.check_report(
            default, boosted, boundary_report(-0.08, -6.38), 0.15, 8.0, 0.10, 4.0, -0.50
        )
        self.assertEqual(
            next(check["status"] for check in checks if "terminal_margin" in check["name"]),
            "investigate",
        )
        self.assertEqual(qualification.report_status(checks), "pass_with_investigation")

    def test_boosted_pressure_must_move_away_from_terminal_ceiling(self) -> None:
        default = suite_report({name: 0.0 for name in qualification.CONTINUOUS_PROBES})
        boosted = suite_report(
            {"bass_burst": -4.0, "correlated_mono": -4.0, "side_only": -4.0, "bass_pressure_90hz": 0.92}
        )
        checks = qualification.check_report(
            default, boosted, boundary_report(-0.08, -6.38), 0.15, 8.0, 0.10, 4.0, -0.50
        )
        self.assertEqual(
            next(check["status"] for check in checks if "boosted_bass_pressure" in check["name"]),
            "fail",
        )


if __name__ == "__main__":
    unittest.main()
