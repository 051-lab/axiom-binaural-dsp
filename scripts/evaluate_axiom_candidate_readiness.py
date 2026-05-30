#!/usr/bin/env python3
"""Evaluate whether Axiom is ready to propose another sound-changing candidate."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import validate_axiom_device_matrix as device_matrix
import validate_axiom_material_manifest as material_manifest


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_POLICY = REPO_ROOT / "tools" / "axiom-team" / "policy.json"
DEFAULT_MATERIAL_MANIFEST = (
    Path.home()
    / ".local"
    / "share"
    / "axiom-test-material"
    / "cc0-opengameart"
    / "axiom-external-cc0-manifest.json"
)
DEFAULT_DEVICE_MATRIX = (
    Path.home() / ".local" / "state" / "axiom-engineering" / "device-matrix.json"
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def status_text(status: str) -> str:
    return "PASS" if status == "pass" else status.upper()


def baseline_check(repository_root: Path, policy_path: Path) -> dict[str, Any]:
    try:
        policy = json.loads(policy_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {
            "name": "accepted_baseline_hash",
            "status": "fail",
            "ready": False,
            "detail": f"cannot read policy: {exc}",
        }
    accepted = policy.get("acceptedBaseline", {})
    script = repository_root / str(accepted.get("path", ""))
    expected = accepted.get("sha256")
    if not script.is_file():
        return {
            "name": "accepted_baseline_hash",
            "status": "fail",
            "ready": False,
            "detail": f"accepted script missing: {script}",
        }
    actual = sha256(script)
    ready = bool(expected) and actual == expected
    return {
        "name": "accepted_baseline_hash",
        "status": "pass" if ready else "fail",
        "ready": ready,
        "detail": f"{accepted.get('version', 'unknown')} {actual} expected {expected}",
        "path": str(script),
    }


def material_check(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {
            "name": "corpus_manifest_strict",
            "status": "fail",
            "ready": False,
            "detail": f"material manifest missing: {path}",
        }
    try:
        data = material_manifest.load_manifest(path)
        report = material_manifest.validate_manifest(
            data,
            manifest_path=path,
            strict_metadata=True,
        )
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        return {
            "name": "corpus_manifest_strict",
            "status": "fail",
            "ready": False,
            "detail": f"cannot validate material manifest: {exc}",
        }
    ready = report["status"] == "pass"
    detail = (
        f"{report.get('track_count', 0)} tracks; "
        f"{len(report.get('errors', []))} errors; "
        f"{len(report.get('warnings', []))} warnings"
    )
    return {
        "name": "corpus_manifest_strict",
        "status": report["status"],
        "ready": ready,
        "detail": detail,
        "path": str(path),
        "report": report,
    }


def device_check(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {
            "name": "device_matrix_strict",
            "status": "fail",
            "ready": False,
            "detail": f"device matrix missing: {path}",
        }
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        report = device_matrix.validate_matrix(
            data,
            strict_coverage=True,
            strict_setup=True,
        )
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        return {
            "name": "device_matrix_strict",
            "status": "fail",
            "ready": False,
            "detail": f"cannot validate device matrix: {exc}",
        }
    ready = report["status"] == "pass"
    detail = (
        f"{report.get('device_count', 0)} devices; "
        f"{len(report.get('errors', []))} errors; "
        f"{len(report.get('warnings', []))} warnings"
    )
    return {
        "name": "device_matrix_strict",
        "status": report["status"],
        "ready": ready,
        "detail": detail,
        "path": str(path),
        "report": report,
    }


def evaluate_readiness(
    repository_root: Path,
    policy_path: Path,
    material_path: Path,
    device_matrix_path: Path,
) -> dict[str, Any]:
    checks = [
        baseline_check(repository_root, policy_path),
        material_check(material_path),
        device_check(device_matrix_path),
    ]
    blockers = [
        f"{check['name']}: {check['detail']}"
        for check in checks
        if not check["ready"]
    ]
    return {
        "status": "ready" if not blockers else "blocked",
        "scope": "candidate-readiness gate; no DSP files are modified",
        "checks": checks,
        "blockers": blockers,
        "decision": (
            "A new sound-changing candidate may be proposed only with a scoped hypothesis and listening target."
            if not blockers
            else "Do not create a new sound-changing candidate until blockers are resolved."
        ),
    }


def evaluate(
    policy_path: Path,
    material_path: Path,
    device_matrix_path: Path,
) -> dict[str, Any]:
    return evaluate_readiness(REPO_ROOT, policy_path, material_path, device_matrix_path)


def markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Axiom Candidate Readiness",
        "",
        f"Status: **{report['status'].upper()}**",
        "",
        report["decision"],
        "",
        "| Check | Status | Ready | Detail |",
        "| --- | --- | --- | --- |",
    ]
    for check in report["checks"]:
        ready = "yes" if check["ready"] else "no"
        lines.append(
            f"| {check['name']} | {status_text(check['status'])} | "
            f"{ready} | {check['detail']} |"
        )
    if report["blockers"]:
        lines.extend(["", "## Blockers", ""])
        lines.extend(f"- {blocker}" for blocker in report["blockers"])
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "This report checks readiness to consider a candidate. It does not "
            "create a candidate, approve a DSP change, or replace listening acceptance.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--policy", type=Path, default=DEFAULT_POLICY)
    parser.add_argument("--material-manifest", type=Path, default=DEFAULT_MATERIAL_MANIFEST)
    parser.add_argument("--device-matrix", type=Path, default=DEFAULT_DEVICE_MATRIX)
    parser.add_argument("--json", type=Path)
    parser.add_argument("--markdown", type=Path)
    args = parser.parse_args()

    report = evaluate_readiness(
        args.repository_root.expanduser().resolve(),
        args.policy.expanduser().resolve(),
        args.material_manifest.expanduser().resolve(),
        args.device_matrix.expanduser().resolve(),
    )
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    if args.markdown:
        args.markdown.parent.mkdir(parents=True, exist_ok=True)
        args.markdown.write_text(markdown(report), encoding="utf-8")
    if not args.json and not args.markdown:
        print(json.dumps(report, indent=2))
    else:
        if args.json:
            print(args.json)
        if args.markdown:
            print(args.markdown)
    return 0 if report["status"] == "ready" else 1


if __name__ == "__main__":
    raise SystemExit(main())
