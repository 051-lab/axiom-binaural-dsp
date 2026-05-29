"""Tests for Axiom candidate-readiness evaluation."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import evaluate_axiom_candidate_readiness as readiness
import validate_axiom_device_matrix as device_matrix
import validate_axiom_material_manifest as material_manifest


def write_policy(root: Path, digest: str) -> Path:
    policy = root / "policy.json"
    policy.write_text(
        json.dumps(
            {
                "acceptedBaseline": {
                    "version": "v4.1.4.10",
                    "path": "accepted.eel",
                    "sha256": digest,
                }
            }
        ),
        encoding="utf-8",
    )
    return policy


def material_manifest_data(root: Path) -> dict:
    tracks = []
    modes = list(material_manifest.FAILURE_MODES)
    for index, material_class in enumerate(material_manifest.MATERIAL_CLASSES):
        source = root / f"track-{index}.wav"
        source.write_bytes(b"placeholder")
        tracks.append(
            {
                "label": f"Track {index}",
                "path": str(source),
                "start_seconds": 0.0,
                "duration_seconds": 10.0,
                "material_class": material_class,
                "failure_modes": [modes[index % len(modes)]],
                "license_scope": "test fixture",
                "provenance": "unit test",
                "role": "coverage fixture",
            }
        )
    for index, mode in enumerate(modes[len(tracks):], start=len(tracks)):
        source = root / f"mode-{index}.wav"
        source.write_bytes(b"placeholder")
        tracks.append(
            {
                "label": f"Mode {index}",
                "path": str(source),
                "start_seconds": 0.0,
                "duration_seconds": 10.0,
                "material_class": "dense_pop_edm",
                "failure_modes": [mode],
                "license_scope": "test fixture",
                "provenance": "unit test",
                "role": "coverage fixture",
            }
        )
    return {"tracks": tracks}


def device(label: str, device_class: str) -> dict:
    return {
        "label": label,
        "device_class": device_class,
        "platform": "test",
        "route": "test route",
        "output_device": "test output",
        "validation_role": "test role",
        "available": True,
        "qualification_allowed": True,
        "crossfeed_policy": "off_for_qualification",
        "checks": {
            "active_script_hash_verified": True,
            "host_settings_verified": True,
            "route_stability_checked": True,
            "reboot_persistence_checked": True,
        },
    }


def full_device_matrix() -> dict:
    return {
        "schema_version": 1,
        "devices": [device(name, name) for name in device_matrix.DEVICE_CLASSES],
    }


class CandidateReadinessTests(unittest.TestCase):
    def test_ready_when_baseline_corpus_and_device_matrix_are_strict_clean(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            accepted = root / "accepted.eel"
            accepted.write_text("desc: accepted\n", encoding="ascii")
            policy = write_policy(root, readiness.sha256(accepted))
            material = root / "material.json"
            material.write_text(json.dumps(material_manifest_data(root)), encoding="utf-8")
            matrix = root / "device-matrix.json"
            matrix.write_text(json.dumps(full_device_matrix()), encoding="utf-8")
            report = readiness.evaluate_readiness(root, policy, material, matrix)
        self.assertEqual(report["status"], "ready")

    def test_blocked_when_baseline_hash_mismatches(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            accepted = root / "accepted.eel"
            accepted.write_text("desc: accepted\n", encoding="ascii")
            policy = write_policy(root, "bad")
            material = root / "material.json"
            material.write_text(json.dumps(material_manifest_data(root)), encoding="utf-8")
            matrix = root / "device-matrix.json"
            matrix.write_text(json.dumps(full_device_matrix()), encoding="utf-8")
            report = readiness.evaluate_readiness(root, policy, material, matrix)
        self.assertEqual(report["status"], "blocked")
        self.assertTrue(
            any("accepted_baseline_hash" in blocker for blocker in report["blockers"])
        )

    def test_blocked_when_material_manifest_lacks_strict_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            accepted = root / "accepted.eel"
            accepted.write_text("desc: accepted\n", encoding="ascii")
            policy = write_policy(root, readiness.sha256(accepted))
            source = root / "track.wav"
            source.write_bytes(b"placeholder")
            material = root / "material.json"
            material.write_text(
                json.dumps(
                    {
                        "tracks": [
                            {
                                "label": "Track",
                                "path": str(source),
                                "start_seconds": 0,
                                "duration_seconds": 5,
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            matrix = root / "device-matrix.json"
            matrix.write_text(json.dumps(full_device_matrix()), encoding="utf-8")
            report = readiness.evaluate_readiness(root, policy, material, matrix)
        self.assertEqual(report["status"], "blocked")
        self.assertTrue(any("corpus_manifest_strict" in blocker for blocker in report["blockers"]))

    def test_cli_writes_blocked_reports(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            accepted = root / "accepted.eel"
            accepted.write_text("desc: accepted\n", encoding="ascii")
            policy = write_policy(root, "bad")
            material = root / "material.json"
            material.write_text(json.dumps({"tracks": []}), encoding="utf-8")
            matrix = root / "device-matrix.json"
            matrix.write_text(json.dumps({"schema_version": 1, "devices": []}), encoding="utf-8")
            report_json = root / "readiness.json"
            report_md = root / "readiness.md"
            result = subprocess.run(
                [
                    sys.executable,
                    str(
                        Path(__file__).resolve().parents[1]
                        / "scripts"
                        / "evaluate_axiom_candidate_readiness.py"
                    ),
                    "--repository-root",
                    str(root),
                    "--policy",
                    str(policy),
                    "--material-manifest",
                    str(material),
                    "--device-matrix",
                    str(matrix),
                    "--json",
                    str(report_json),
                    "--markdown",
                    str(report_md),
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("blocked", report_json.read_text(encoding="utf-8"))
            self.assertIn("Candidate Readiness", report_md.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
