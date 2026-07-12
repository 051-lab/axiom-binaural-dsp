"""Tests for the Axiom Codex-side helper surface."""

from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
HELPER_PATH = REPO_ROOT / "tools" / "axiom-codex" / "axiom_codex.py"


def load_helper():
    spec = importlib.util.spec_from_file_location("axiom_codex_helper", HELPER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load helper from {HELPER_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


axiom_codex = load_helper()


class AxiomCodexHelperTests(unittest.TestCase):
    def test_authoritative_project_state_is_valid_and_consistent(self) -> None:
        state = axiom_codex.load_project_state()
        checks = axiom_codex.validate_project_state_consistency()
        self.assertEqual(state["accepted"]["label"], "Axiom Clean R011")
        self.assertEqual(state["candidate"]["label"], "Axiom Clean R012")
        self.assertEqual(state["candidate"]["sha256"], "774e3d601b471f98b1818ee4ba424abf9e71a494f4a5a228d45c3d6af3ce070d")
        self.assertEqual(state["candidate"]["status"], "active_unqualified_listening_candidate")
        self.assertEqual(state["candidate"]["qualificationPlan"], "complete")
        self.assertEqual(state["candidate"]["qualificationPlanDocument"], "docs/qualification-r012-plan.md")
        self.assertEqual(state["candidate"]["qualificationExecution"], "requires_investigation")
        self.assertEqual(state["candidate"]["qualificationRecord"], "docs/qualification-r012.md")
        self.assertEqual(state["candidate"]["listening"], "pending")
        self.assertFalse(any(check.status == "fail" for check in checks))

    def test_project_state_validation_rejects_false_candidate_progress(self) -> None:
        state = json.loads(json.dumps(axiom_codex.load_project_state()))
        state["candidate"]["qualificationExecution"] = "passed"
        state["candidate"]["listening"] = "accepted"
        checks = axiom_codex.validate_project_state_data(state)
        details = "\n".join(check.detail for check in checks)
        self.assertTrue(any(check.status == "fail" for check in checks))
        self.assertIn("candidate.qualificationExecution must be requires_investigation", details)
        self.assertIn("candidate.listening must be pending", details)

    def test_project_state_consistency_rejects_stale_active_status_doc(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            stale_status = Path(directory) / "system-status.md"
            stale_status.write_text("## Active Candidate\n\nNone.\n", encoding="utf-8")
            with patch.object(axiom_codex, "SYSTEM_STATUS", stale_status):
                checks = axiom_codex.validate_project_state_consistency()
        self.assertTrue(
            any(check.status == "fail" and check.name == "active state document system-status.md" for check in checks)
        )

    def test_project_state_consistency_rejects_candidate_as_accepted(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            wrong_status = Path(directory) / "system-status.md"
            wrong_status.write_text(
                axiom_codex.SYSTEM_STATUS.read_text(encoding="utf-8")
                + "\nR012 is the accepted baseline.\n",
                encoding="utf-8",
            )
            with patch.object(axiom_codex, "SYSTEM_STATUS", wrong_status):
                checks = axiom_codex.validate_project_state_consistency()
        self.assertTrue(
            any(check.status == "fail" and check.name == "active state document system-status.md" for check in checks)
        )

    def test_project_state_consistency_rejects_policy_baseline_drift(self) -> None:
        policy = axiom_codex.load_policy()
        policy["acceptedBaseline"]["path"] = "src/wrong.eel"
        with patch.object(axiom_codex, "load_policy", return_value=policy):
            checks = axiom_codex.validate_project_state_consistency()
        self.assertTrue(any(check.status == "fail" and check.name == "accepted policy alignment" for check in checks))

    def test_cli_status_summary_reports_authoritative_candidate_state(self) -> None:
        result = subprocess.run(
            [sys.executable, str(HELPER_PATH), "status-summary", "--no-evidence"],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Axiom Clean R011", result.stdout)
        self.assertIn("Axiom Clean R012", result.stdout)
        self.assertIn("active_unqualified_listening_candidate", result.stdout)
        self.assertIn("qualification plan: `complete`", result.stdout)
        self.assertIn("qualification execution: `requires_investigation`", result.stdout)
        self.assertIn("qualification record: `docs/qualification-r012.md`", result.stdout)
        self.assertIn("listening: `pending`", result.stdout)
        self.assertIn("accepted baseline replacement: `not_approved`", result.stdout)

    def test_command_surface_has_required_safe_workflows(self) -> None:
        commands = axiom_codex.command_surface_lookup()
        for name in [
            "status-summary",
            "ready-check",
            "local-review",
            "guard-check",
            "command-surface",
            "agentic-audit",
            "task-state",
            "next-action",
            "evidence-ingest",
            "evidence-status",
            "evidence-catalog",
            "agent-profiles",
            "agent-review",
            "agent-review-status",
            "airwindows-audit",
            "airwindows-index",
            "knowledge-query",
            "knowledge-sources",
            "pi-handoff",
            "session-log-update",
            "skill-eval",
        ]:
            self.assertIn(name, commands)
        self.assertTrue(commands["pi-handoff"]["touchesJDSP"])
        self.assertTrue(commands["pi-handoff"]["requiresApproval"])
        self.assertFalse(commands["guard-check"]["touchesJDSP"])
        self.assertFalse(commands["local-review"]["touchesJDSP"])
        self.assertFalse(commands["task-state"]["touchesJDSP"])
        self.assertFalse(commands["next-action"]["touchesJDSP"])
        self.assertFalse(commands["evidence-ingest"]["touchesJDSP"])
        self.assertFalse(commands["evidence-status"]["touchesJDSP"])
        self.assertFalse(commands["evidence-catalog"]["touchesJDSP"])

    def test_agentic_contracts_validate(self) -> None:
        checks = [
            *axiom_codex.validate_command_surface_data(axiom_codex.load_command_surface()),
            *axiom_codex.validate_agent_profiles(),
            *axiom_codex.validate_skill_eval_data(axiom_codex.load_skill_eval_cases()),
        ]
        self.assertFalse(
            any(check.status == "fail" for check in checks),
            "\n".join(f"{check.name}: {check.detail}" for check in checks),
        )

    def test_command_surface_contract_rejects_drift_and_unsafe_jdsp_mapping(self) -> None:
        command = {
            "name": "fixture",
            "trigger": "fixture trigger",
            "nativeAlias": "/axiom-fixture",
            "layer": "Codex helper",
            "helperCommand": "python3 tools/axiom-codex/axiom_codex.py missing-runtime",
            "touchesJDSP": True,
            "requiresApproval": False,
            "purpose": "Fixture.",
            "inputs": [],
            "outputs": ["result"],
            "boundaries": ["fixture only"],
        }
        duplicate = dict(command, name="fixture-two")
        checks = axiom_codex.validate_command_surface_data(
            {"schemaVersion": 1, "commands": [command, duplicate]},
            runtime_commands={"fixture"},
        )
        names = {check.name for check in checks if check.status == "fail"}
        self.assertIn("duplicate native alias", names)
        self.assertIn("JDSP approval boundary", names)
        self.assertIn("helper command mapping", names)
        self.assertIn("helper runtime command", names)

    def test_agent_profile_contract_rejects_missing_sections(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            profile = Path(directory) / "fixture.md"
            profile.write_text(
                "# Fixture\n\nRole source: `tools/axiom-team/roles/fixture.md`\n\n## Purpose\n\nTest.\n",
                encoding="utf-8",
            )
            checks = axiom_codex.validate_agent_profiles(Path(directory))
        self.assertTrue(any(check.name == "profile required sections" for check in checks))

    def test_agent_review_record_validates_default_roles(self) -> None:
        record = axiom_codex.build_agent_review_record("Agentic review contract")
        checks = axiom_codex.validate_agent_review_record(record)
        self.assertFalse(
            any(check.status == "fail" for check in checks),
            "\n".join(f"{check.name}: {check.detail}" for check in checks),
        )
        self.assertEqual(record["recordType"], "axiom-agent-review")
        self.assertEqual(record["decision"], "draft")
        self.assertEqual(record["evidenceStatus"], "not_evidence_until_completed")
        self.assertGreaterEqual(len(record["roles"]), 5)

    def test_agent_review_record_rejects_unknown_role_and_bad_decision(self) -> None:
        record = axiom_codex.build_agent_review_record("Bad record", ["coordinator"])
        record["decision"] = "approve-release"
        record["roles"].append(
            {
                "role": "unknown-role",
                "profileSource": "missing.md",
                "roleSource": "missing.md",
                "purpose": "",
                "findings": [],
                "evidenceNeeded": [],
                "evidenceReferences": [],
                "decision": "draft",
            }
        )
        checks = axiom_codex.validate_agent_review_record(record)
        names = {check.name for check in checks if check.status == "fail"}
        self.assertIn("review decision", names)
        self.assertIn("unknown review role", names)

    def test_completed_agent_review_requires_findings_and_references(self) -> None:
        record = axiom_codex.build_agent_review_record("Incomplete completed review", ["coordinator"])
        record["status"] = "complete"
        record["scope"] = "Agentic tooling review."
        record["decision"] = "continue"
        record["evidenceStatus"] = "completed_review_not_authority"
        record["roles"][0]["decision"] = "continue"
        checks = axiom_codex.validate_agent_review_record(record)
        names = {check.name for check in checks if check.status == "fail"}
        self.assertIn("completed role findings", names)
        self.assertIn("completed role evidenceReferences", names)

    def test_completed_agent_review_validates_and_rejects_private_paths(self) -> None:
        record = self._completed_agent_review()
        checks = axiom_codex.validate_agent_review_record(record)
        self.assertFalse(any(check.status == "fail" for check in checks))
        record["roles"][0]["evidenceReferences"] = [r"C:\Users\private\report.json"]
        checks = axiom_codex.validate_agent_review_record(record)
        self.assertTrue(any(check.name == "completed review private path" for check in checks))

    def test_agent_review_accepts_optional_subagent_metadata(self) -> None:
        record = self._completed_agent_review()
        record["reviewRun"] = {
            "runId": "subagent-review-fixture",
            "createdAtUtc": "2026-07-06T12:00:00Z",
            "orchestrator": "codex",
            "runtime": "multi_agent_v1",
            "inputRefs": ["docs/axiom-subagent-operating-model.md"],
            "contextSha256": "a" * 64,
        }
        record["roles"][0]["subagent"] = {
            "status": "completed",
            "startedAtUtc": "2026-07-06T12:00:01Z",
            "completedAtUtc": "2026-07-06T12:00:30Z",
            "runtime": "multi_agent_v1.explorer",
            "promptSha256": "b" * 64,
            "resultSha256": "c" * 64,
            "transcriptRef": "agent-transcript-001",
        }
        checks = axiom_codex.validate_agent_review_record(record)
        with tempfile.TemporaryDirectory() as directory:
            payload_path = Path(directory) / "review.json"
            payload_path.write_text(json.dumps(record), encoding="utf-8")
            payload = axiom_codex.agent_review_status_payload(payload_path)
        self.assertFalse(any(check.status == "fail" for check in checks))
        self.assertEqual(payload["provenance"], "mixed")
        self.assertEqual(payload["subagentRoleCount"], 1)
        self.assertEqual(payload["completedSubagentCount"], 1)

    def test_agent_review_rejects_raw_or_private_subagent_metadata(self) -> None:
        record = self._completed_agent_review()
        record["reviewRun"] = {
            "runId": "bad-review",
            "inputRefs": [r"C:\Users\private\source.json"],
        }
        record["roles"][0]["subagent"] = {
            "status": "completed",
            "transcriptRef": "/tmp/raw-transcript.json",
            "rawTranscript": "do not store raw transcript text",
        }
        checks = axiom_codex.validate_agent_review_record(record)
        names = {check.name for check in checks if check.status == "fail"}
        self.assertIn("review run inputRefs", names)
        self.assertIn("review subagent fields", names)
        self.assertIn("review subagent transcriptRef", names)

    def test_skill_eval_contract_rejects_duplicate_and_unknown_command(self) -> None:
        case = {
            "id": "fixture",
            "prompt": "Run fixture.",
            "expected": {
                "helperCommands": ["missing-command"],
                "requiredTerms": [],
            },
        }
        checks = axiom_codex.validate_skill_eval_data(
            {"schemaVersion": 1, "cases": [case, dict(case)]},
            known_commands={"status-summary"},
        )
        names = {check.name for check in checks if check.status == "fail"}
        self.assertIn("duplicate skill eval id", names)
        self.assertIn("skill eval command mapping", names)
        self.assertIn("skill eval required terms", names)

    def test_agent_profiles_mirror_team_roles(self) -> None:
        profiles = {profile[0] for profile in axiom_codex.load_agent_profiles()}
        self.assertEqual(
            profiles,
            {
                "coordinator",
                "dsp-architect",
                "eel-engineer",
                "implementation-lead",
                "measurement-engineer",
                "qualification-lead",
                "release-steward",
                "safety-auditor",
                "signal-researcher",
                "tooling-engineer",
            },
        )

    def test_guard_flags_accepted_eel_policy_and_private_artifacts(self) -> None:
        policy = {
            "acceptedBaseline": {
                "path": "src/axiom_binaural_dsp_v4.1.4.11.eel",
            }
        }
        findings = axiom_codex.classify_guard_paths(
            [
                "src/axiom_binaural_dsp_v4.1.4.11.eel",
                "tools/axiom-team/policy.json",
                "captures/song.wav",
                "local-material/material-manifest.json",
                ".env",
            ],
            policy=policy,
        )
        details = "\n".join(finding.detail for finding in findings)
        self.assertTrue(any(finding.status == "fail" for finding in findings))
        self.assertIn("accepted baseline", details)
        self.assertIn("policy", details)
        self.assertIn("audio", details)
        self.assertIn("manifest", details)
        self.assertIn("credential", details)

    def test_guard_warns_for_labs_eel_fixture(self) -> None:
        findings = axiom_codex.classify_guard_paths(
            ["src/labs/axiom_binaural_dsp_v4.1.4.11_width_profile_lab.eel"],
            policy={"acceptedBaseline": {"path": "src/axiom_binaural_dsp_v4.1.4.11.eel"}},
        )
        self.assertTrue(any(finding.status == "warn" and finding.name == "Labs EEL fixture gate" for finding in findings))
        self.assertFalse(any(finding.status == "fail" for finding in findings))

    def test_guard_flags_private_paths_in_added_text(self) -> None:
        findings = axiom_codex.classify_guard_paths(
            ["docs/example.md"],
            text_by_path={"docs/example.md": "local render path: /home/tester/material/track.wav"},
            policy={"acceptedBaseline": {"path": "src/accepted.eel"}},
        )
        self.assertTrue(any(finding.name == "private path content" for finding in findings))

    def test_skill_eval_cases_reference_known_commands(self) -> None:
        commands = axiom_codex.command_surface_lookup()
        cases = axiom_codex.load_skill_eval_cases()["cases"]
        self.assertGreaterEqual(len(cases), 5)
        for case in cases:
            for helper_command in case["expected"]["helperCommands"]:
                self.assertIn(helper_command, commands)

    def test_knowledge_source_audit_flags_missing_local_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            index = root / "source-index.json"
            index.write_text(
                json.dumps(
                    {
                        "schemaVersion": 1,
                        "sources": [
                            {
                                "id": "missing-source",
                                "title": "Missing Source",
                                "type": "book",
                                "topics": ["DSP"],
                                "localPath": str(root / "missing.pdf"),
                                "axiomUse": "test fixture",
                                "status": "unread",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            _, checks = axiom_codex.audit_knowledge_sources(index)
        self.assertTrue(any(check.status == "fail" and check.name == "local source file" for check in checks))

    def test_cli_knowledge_sources_hides_private_paths_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source.pdf"
            source.write_bytes(b"placeholder")
            index = root / "source-index.json"
            index.write_text(
                json.dumps(
                    {
                        "schemaVersion": 1,
                        "sources": [
                            {
                                "id": "fixture-source",
                                "title": "Fixture Source",
                                "type": "book",
                                "topics": ["DSP"],
                                "localPath": str(source),
                                "axiomUse": "test fixture",
                                "status": "unread",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            result = subprocess.run(
                [sys.executable, str(HELPER_PATH), "knowledge-sources", "--index", str(index)],
                cwd=REPO_ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("fixture-source", result.stdout)
        self.assertNotIn(str(source), result.stdout)

    def test_airwindows_index_is_metadata_only(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repo = root / "airwindows"
            plugin = repo / "plugins" / "WinVST" / "BassDrive"
            linux_plugin = repo / "plugins" / "LinuxVST" / "src" / "BassDrive"
            mac_plugin = repo / "plugins" / "MacSignedVST" / "BassDrive" / "source"
            plugin.mkdir(parents=True)
            linux_plugin.mkdir(parents=True)
            mac_plugin.mkdir(parents=True)
            (repo / "LICENSE").write_text("MIT License\n", encoding="utf-8")
            (repo / "Airwindopedia.txt").write_text("Airwindows public effect list\n", encoding="utf-8")
            (plugin / "BassDriveProc.cpp").write_text(
                "double secretConstant = 0.12345; // source code must not be copied\n",
                encoding="utf-8",
            )
            (linux_plugin / "BassDriveProc.cpp").write_text("platform duplicate\n", encoding="utf-8")
            (mac_plugin / "BassDrive.cpp").write_text("platform duplicate\n", encoding="utf-8")
            subprocess.run(["git", "init"], cwd=repo, text=True, capture_output=True, check=True)
            subprocess.run(["git", "add", "."], cwd=repo, text=True, capture_output=True, check=True)
            subprocess.run(
                [
                    "git",
                    "-c",
                    "user.name=Axiom Test",
                    "-c",
                    "user.email=axiom@example.invalid",
                    "commit",
                    "-m",
                    "fixture",
                ],
                cwd=repo,
                text=True,
                capture_output=True,
                check=True,
            )
            output = root / "index.json"
            result = subprocess.run(
                [sys.executable, str(HELPER_PATH), "airwindows-index", "--repo", str(repo), "--output", str(output)],
                cwd=REPO_ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            payload = json.loads(output.read_text(encoding="utf-8"))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        rendered = json.dumps(payload, sort_keys=True)
        self.assertEqual(payload["schemaVersion"], 2)
        self.assertEqual(payload["sourceId"], "airwindows-open-source-dsp")
        self.assertRegex(payload["pinnedCommit"], r"^[0-9a-f]{40}$")
        bass_drive = [effect for effect in payload["effects"] if effect["name"] == "BassDrive"]
        self.assertEqual(len(bass_drive), 1)
        self.assertEqual(len(bass_drive[0]["sourcePaths"]), 3)
        self.assertFalse(any(effect["name"] == "source" for effect in payload["effects"]))
        self.assertIn("bass", rendered)
        self.assertNotIn("secretConstant", rendered)
        self.assertNotIn("0.12345", rendered)
        self.assertNotIn(str(repo), rendered)

    def test_knowledge_query_searches_airwindows_index_without_private_path(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            index = root / "airwindows-index.json"
            index.write_text(
                json.dumps(
                    {
                        "schemaVersion": 1,
                        "sourceId": "airwindows-open-source-dsp",
                        "repoUrl": "https://github.com/airwindows/airwindows",
                        "pinnedCommit": "1" * 40,
                        "effects": [
                            {
                                "name": "BassDrive",
                                "relativePath": "plugins/WinVST/BassDrive/BassDriveProc.cpp",
                                "tags": ["bass", "nonlinear"],
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            result = subprocess.run(
                [
                    sys.executable,
                    str(HELPER_PATH),
                    "knowledge-query",
                    "bass nonlinear",
                    "--airwindows-index",
                    str(index),
                ],
                cwd=REPO_ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Airwindows Local Index", result.stdout)
        self.assertIn("BassDrive", result.stdout)
        self.assertNotIn(str(index), result.stdout)

    def test_knowledge_query_auto_discovers_standard_airwindows_index(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            index = Path(directory) / "index.json"
            index.write_text(
                json.dumps(
                    {
                        "schemaVersion": 2,
                        "sourceId": "airwindows-open-source-dsp",
                        "title": "Airwindows Open Source DSP",
                        "repoUrl": "https://github.com/airwindows/airwindows",
                        "license": "MIT",
                        "pinnedCommit": "1" * 40,
                        "generatedBy": "test",
                        "boundary": "metadata-only",
                        "effects": [
                            {
                                "name": "BassDrive",
                                "sourcePaths": ["plugins/WinVST/BassDrive/BassDriveProc.cpp"],
                                "tags": ["bass", "nonlinear"],
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            with patch.object(axiom_codex, "DEFAULT_AIRWINDOWS_INDEX", index):
                resolved = axiom_codex.resolve_airwindows_index(None)
        self.assertEqual(resolved, index)

    def test_airwindows_index_can_be_explicitly_disabled(self) -> None:
        self.assertIsNone(axiom_codex.resolve_airwindows_index(Path("/tmp/index.json"), disabled=True))

    def test_airwindows_audit_rejects_noncanonical_or_unsafe_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            index = Path(directory) / "index.json"
            index.write_text(
                json.dumps(
                    {
                        "schemaVersion": 2,
                        "sourceId": "airwindows-open-source-dsp",
                        "pinnedCommit": "1" * 40,
                        "effects": [
                            {
                                "name": "Unsafe",
                                "tags": ["nonlinear"],
                                "sourcePaths": ["/private/Unsafe.cpp"],
                                "snippet": "copied source",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            checks = axiom_codex.audit_airwindows_index(index)
        self.assertTrue(any(check.status == "fail" and check.name == "Airwindows relative path" for check in checks))
        self.assertTrue(any(check.status == "fail" and check.name == "Airwindows metadata fields" for check in checks))

    def test_airwindows_audit_rejects_unsafe_top_level_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            index = Path(directory) / "index.json"
            index.write_text(
                json.dumps(
                    {
                        "schemaVersion": 2,
                        "sourceId": "airwindows-open-source-dsp",
                        "title": "Airwindows Open Source DSP",
                        "repoUrl": "https://example.invalid/fork",
                        "license": "unknown",
                        "pinnedCommit": "1" * 40,
                        "generatedBy": "test",
                        "boundary": "metadata-only",
                        "localPath": "/private/checkout",
                        "effects": [
                            {
                                "name": "Fixture",
                                "tags": ["uncategorized"],
                                "sourcePaths": ["plugins/Fixture.cpp"],
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            checks = axiom_codex.audit_airwindows_index(index)
        names = {check.name for check in checks if check.status == "fail"}
        self.assertIn("Airwindows repository URL", names)
        self.assertIn("Airwindows license", names)
        self.assertIn("Airwindows top-level fields", names)

    def test_airwindows_audit_reports_checkout_drift(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repo = root / "repo"
            repo.mkdir()
            subprocess.run(["git", "init"], cwd=repo, text=True, capture_output=True, check=True)
            (repo / "README.md").write_text("fixture\n", encoding="utf-8")
            subprocess.run(["git", "add", "."], cwd=repo, text=True, capture_output=True, check=True)
            subprocess.run(
                ["git", "-c", "user.name=Axiom Test", "-c", "user.email=axiom@example.invalid", "commit", "-m", "fixture"],
                cwd=repo,
                text=True,
                capture_output=True,
                check=True,
            )
            index = root / "index.json"
            index.write_text(
                json.dumps(
                    {
                        "schemaVersion": 2,
                        "sourceId": "airwindows-open-source-dsp",
                        "pinnedCommit": "1" * 40,
                        "effects": [{"name": "Fixture", "tags": ["uncategorized"], "sourcePaths": ["plugins/Fixture.cpp"]}],
                    }
                ),
                encoding="utf-8",
            )
            checks = axiom_codex.audit_airwindows_index(index, repo)
        self.assertTrue(any(check.status == "warn" and check.name == "Airwindows checkout drift" for check in checks))

    def test_evidence_ingest_normalizes_soak_environment_warning(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            report = Path(directory) / "soak-report.json"
            report.write_text(
                "\ufeff" + json.dumps(
                    {
                        "schemaVersion": 1,
                        "result": "fail",
                        "startedAt": "2026-06-20T09:00:00Z",
                        "endedAt": "2026-06-20T10:00:00Z",
                        "route": {
                            "capture": {"name": "CABLE Input", "id": "private-capture-id"},
                            "output": {"name": "Headphones", "id": "private-output-id"},
                        },
                        "power": {"sourceChanges": [{"message": "Power source change."}]},
                        "metrics": {
                            "processedFrames": 1000,
                            "packets": 10,
                            "droppedFrames": 0,
                            "conversionErrors": 0,
                            "discontinuities": 3,
                            "renderStarvations": 0,
                            "renderErrors": 0,
                            "dspCriticalStalls": 0,
                        },
                        "gates": [
                            {"name": "no dropped frames", "passed": True, "detail": "dropped=0"},
                            {"name": "bounded discontinuities", "passed": False, "detail": "discontinuities=3"},
                            {"name": "power source remained stable", "passed": False, "detail": "changes=1"},
                        ],
                        "artifacts": {"runRoot": r"C:\Users\private\Axiom"},
                    }
                ),
                encoding="utf-8",
            )
            payload = axiom_codex.build_evidence_bundle([report])
        rendered = json.dumps(payload, sort_keys=True)
        self.assertEqual(payload["aggregateDecision"], "pass_with_environment_warning")
        self.assertEqual(payload["records"][0]["sourceResult"], "fail")
        self.assertEqual(payload["records"][0]["decision"], "pass_with_environment_warning")
        self.assertNotIn("private-capture-id", rendered)
        self.assertNotIn(r"C:\Users\private", rendered)
        self.assertNotIn(str(report), rendered)

    def test_evidence_ingest_normalizes_partial_soak_investigate(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            report = Path(directory) / "soak-report.json"
            report.write_text(
                json.dumps(
                    {
                        "schemaVersion": 1,
                        "result": "error",
                        "error": "Stream was not readable.",
                        "startedAt": "2026-06-23T06:37:28Z",
                        "endedAt": "2026-06-23T11:06:38Z",
                        "requestedDurationMinutes": 480,
                        "route": {
                            "capture": {"name": "CABLE Input", "id": "private-capture-id"},
                            "output": {"name": "EarPods", "id": "private-output-id"},
                        },
                        "classification": {
                            "evidenceDecision": "investigate",
                            "failureCategory": "harness_error",
                            "completedFullDuration": False,
                            "completedDurationMinutes": 269.1,
                            "requestedDurationMinutes": 480,
                            "audioIntegrityPassed": False,
                            "harnessError": True,
                        },
                        "metrics": {
                            "processedFrames": 774858701,
                            "packets": 1614381,
                            "droppedFrames": 46,
                            "conversionErrors": 0,
                            "discontinuities": 105,
                            "renderStarvations": 0,
                            "renderErrors": 0,
                            "dspCalls": 1614381,
                            "dspDeadlineMisses": 86,
                            "dspDeadlineMissRate": 0.000053,
                            "dspCriticalStalls": 0,
                            "configReloads": 13,
                        },
                        "healthAnalysis": {
                            "sampleCount": 3229,
                            "dropEvents": [{"timestamp": "2026-06-23T09:43:43Z", "dropDelta": 46}],
                            "discontinuityEvents": [{"timestamp": "2026-06-23T10:34:59Z", "discontinuityDelta": 68}],
                            "deadlineEvents": [{"timestamp": "2026-06-23T10:34:59Z", "deadlineMissDelta": 84}],
                        },
                        "environmentEvents": [
                            {
                                "reason": "drop",
                                "count": 2,
                                "events": [
                                    {
                                        "provider": "Microsoft-Windows-Hyper-V-VmSwitch",
                                        "message": r"C:\Users\private should not escape",
                                    }
                                ],
                            }
                        ],
                        "healthReadWarnings": [{"message": "private warning detail"}],
                        "gates": [
                            {"name": "no dropped frames", "passed": False, "detail": "dropped=46"},
                            {"name": "no render errors", "passed": True, "detail": "errors=0"},
                            {"name": "no render starvations", "passed": True, "detail": "starvations=0"},
                        ],
                    }
                ),
                encoding="utf-8",
            )
            payload = axiom_codex.build_evidence_bundle([report])
        rendered = json.dumps(payload, sort_keys=True)
        record = payload["records"][0]
        self.assertEqual(payload["aggregateDecision"], "investigate")
        self.assertEqual(record["sourceResult"], "error")
        self.assertEqual(record["decision"], "investigate")
        self.assertEqual(record["classification"]["failureCategory"], "harness_error")
        self.assertFalse(record["classification"]["completedFullDuration"])
        self.assertEqual(record["healthAnalysis"]["dropEventCount"], 1)
        self.assertEqual(record["environmentEventWindows"][0]["reason"], "drop")
        self.assertIn("harness error", "\n".join(record["warnings"]))
        self.assertIn("incomplete duration", "\n".join(record["warnings"]))
        self.assertNotIn(r"C:\Users\private", rendered)
        self.assertNotIn("private warning detail", rendered)

    def test_evidence_ingest_normalizes_manual_recovery_and_writes_bundle(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            report = root / "qualification-decision.json"
            output = root / "bundle.json"
            report.write_text(
                json.dumps(
                    {
                        "schemaVersion": 1,
                        "result": "pass",
                        "qualifiedRoute": {
                            "captureName": "CABLE Input",
                            "captureId": "private-capture-id",
                            "outputName": "EarPods",
                            "outputId": "private-output-id",
                            "bufferMs": 200,
                        },
                        "gates": {
                            "disconnectDetected": True,
                            "automaticReconnect": True,
                            "postRecoveryDroppedFrames": 0,
                        },
                        "modernStandby": {"enteredEventId": 506, "exitedEventId": 507},
                    }
                ),
                encoding="utf-8",
            )
            result = subprocess.run(
                [
                    sys.executable,
                    str(HELPER_PATH),
                    "evidence-ingest",
                    str(report),
                    "--output",
                    str(output),
                    "--json",
                ],
                cwd=REPO_ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            payload = json.loads(output.read_text(encoding="utf-8"))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(payload["aggregateDecision"], "pass")
        self.assertEqual(payload["records"][0]["kind"], "windows-manual-recovery")
        self.assertTrue(payload["records"][0]["modernStandbyObserved"])
        self.assertNotIn("sourcePath", payload["records"][0])
        self.assertIn("not listening acceptance", "\n".join(payload["boundaries"]))

    def test_evidence_ingest_rejects_unknown_schema(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            report = Path(directory) / "unknown.json"
            report.write_text('{"schemaVersion": 1}', encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(HELPER_PATH), "evidence-ingest", str(report)],
                cwd=REPO_ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
        self.assertEqual(result.returncode, 2)
        self.assertIn("unsupported qualification evidence schema", result.stderr)

    def test_evidence_status_validates_and_summarizes_bundle(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            bundle = Path(directory) / "bundle.json"
            bundle.write_text(
                json.dumps(
                    {
                        "schemaVersion": 1,
                        "recordType": "axiom-qualification-evidence-bundle",
                        "generatedAtUtc": "2026-06-20T12:00:00Z",
                        "aggregateDecision": "pass_with_environment_warning",
                        "records": [
                            {
                                "kind": "windows-host-soak",
                                "scope": "windows-host-endurance",
                                "sourceName": "soak-report.json",
                                "sourceSha256": "a" * 64,
                                "sourceResult": "fail",
                                "decision": "pass_with_environment_warning",
                                "gates": [],
                                "warnings": ["power source changed"],
                                "criticalFailures": [],
                            },
                            {
                                "kind": "windows-manual-recovery",
                                "scope": "windows-route-and-sleep-recovery",
                                "sourceName": "qualification-decision.json",
                                "sourceSha256": "b" * 64,
                                "sourceResult": "pass",
                                "decision": "pass",
                                "gates": [],
                                "warnings": [],
                                "criticalFailures": [],
                            },
                        ],
                        "boundaries": axiom_codex.EVIDENCE_BOUNDARIES,
                    }
                ),
                encoding="utf-8",
            )
            payload = axiom_codex.evidence_status_payload(bundle)
        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["aggregateDecision"], "pass_with_environment_warning")
        self.assertEqual(payload["recordCount"], 2)
        self.assertEqual(payload["warningCount"], 1)
        self.assertEqual(payload["criticalFailureCount"], 0)

    def test_evidence_status_rejects_invalid_bundle(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            bundle = Path(directory) / "bundle.json"
            bundle.write_text(
                json.dumps(
                    {
                        "schemaVersion": 1,
                        "recordType": "axiom-qualification-evidence-bundle",
                        "aggregateDecision": "pass",
                        "records": [
                            {
                                "kind": "fixture",
                                "scope": "fixture",
                                "sourceName": "fixture.json",
                                "sourceSha256": "not-a-hash",
                                "sourceResult": "pass",
                                "decision": "pass",
                                "gates": [],
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            payload = axiom_codex.evidence_status_payload(bundle)
        self.assertEqual(payload["status"], "fail")
        self.assertTrue(any(check["name"] == "evidence source hash" for check in payload["checks"]))

    def test_next_action_includes_qualification_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            bundle = Path(directory) / "bundle.json"
            bundle.write_text(
                json.dumps(
                    {
                        "schemaVersion": 1,
                        "recordType": "axiom-qualification-evidence-bundle",
                        "aggregateDecision": "investigate",
                        "records": [
                            {
                                "kind": "fixture",
                                "scope": "fixture",
                                "sourceName": "fixture.json",
                                "sourceSha256": "c" * 64,
                                "sourceResult": "fail",
                                "decision": "investigate",
                                "gates": [],
                                "warnings": [],
                                "criticalFailures": ["fixture gate"],
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            payload = axiom_codex.next_action_payload(bundle)
        self.assertEqual(payload["qualificationEvidence"]["aggregateDecision"], "investigate")
        self.assertIn("Review the qualification evidence failures", payload["recommendedAction"])

    def test_evidence_catalog_selects_latest_valid_bundle(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name, generated, decision in [
                ("older.json", "2026-06-19T12:00:00Z", "pass"),
                ("newer.json", "2026-06-20T12:00:00Z", "pass_with_environment_warning"),
            ]:
                (root / name).write_text(
                    json.dumps(
                        {
                            "schemaVersion": 1,
                            "recordType": "axiom-qualification-evidence-bundle",
                            "generatedAtUtc": generated,
                            "aggregateDecision": decision,
                            "records": [
                                {
                                    "kind": "fixture",
                                    "scope": "fixture",
                                    "sourceName": "fixture.json",
                                    "sourceSha256": "d" * 64,
                                    "sourceResult": "pass",
                                    "decision": decision,
                                    "gates": [],
                                    "warnings": [],
                                    "criticalFailures": [],
                                }
                            ],
                        }
                    ),
                    encoding="utf-8",
                )
            (root / "invalid.json").write_text('{"schemaVersion": 1}', encoding="utf-8")
            payload = axiom_codex.evidence_catalog_payload(root)
        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["bundleCount"], 3)
        self.assertEqual(payload["validBundleCount"], 2)
        self.assertEqual(payload["latestBundleName"], "newer.json")

    def test_configured_evidence_path_prefers_explicit_and_can_disable(self) -> None:
        explicit = Path("/tmp/explicit-evidence.json")
        self.assertEqual(axiom_codex.configured_evidence_path(explicit), explicit)
        self.assertIsNone(axiom_codex.configured_evidence_path(explicit, disabled=True))

    def test_evidence_directory_reports_existing_default_configuration(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config = root / "evidence-config.json"
            config.write_text(
                json.dumps(
                    {
                        "schemaVersion": 1,
                        "directory": str(root),
                        "boundary": "local-only configuration; do not commit",
                    }
                ),
                encoding="utf-8",
            )
            with patch.object(axiom_codex, "DEFAULT_EVIDENCE_CONFIG", config):
                self.assertTrue(axiom_codex.evidence_directory_is_default(root))
                self.assertFalse(axiom_codex.evidence_directory_is_default(root / "other"))

    def test_pi_handoff_command_defaults_to_targeted_sub_gain_follow_up(self) -> None:
        command = axiom_codex.pi_handoff_command(
            argparse.Namespace(
                run_id=axiom_codex.DEFAULT_SUB_GAIN_RUN,
                slider_db=None,
                label_regex=axiom_codex.DEFAULT_SUB_GAIN_LABEL_REGEX,
                repetitions=None,
            )
        )
        self.assertEqual(command[:4], ["node", "tools/axiom-team/bin/axiom-team.mjs", "map-sub-gain", axiom_codex.DEFAULT_SUB_GAIN_RUN])
        self.assertIn("--slider-db", command)
        self.assertIn("4", command)
        self.assertIn("10", command)
        self.assertIn("12", command)
        self.assertIn("--label-regex", command)

    def test_pi_handoff_command_allows_custom_slider_list(self) -> None:
        command = axiom_codex.pi_handoff_command(
            argparse.Namespace(
                run_id="run-1",
                slider_db=[8],
                label_regex="bass",
                repetitions=2,
            )
        )
        self.assertEqual(
            command,
            [
                "node",
                "tools/axiom-team/bin/axiom-team.mjs",
                "map-sub-gain",
                "run-1",
                "--slider-db",
                "4",
                "--slider-db",
                "8",
                "--label-regex",
                "bass",
                "--repetitions",
                "2",
            ],
        )

    def test_cli_skill_eval_passes(self) -> None:
        result = subprocess.run(
            [sys.executable, str(HELPER_PATH), "skill-eval"],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("status-inspection", result.stdout)

    def test_cli_agentic_audit_passes(self) -> None:
        result = subprocess.run(
            [sys.executable, str(HELPER_PATH), "agentic-audit"],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("command surface contract", result.stdout)
        self.assertIn("agent profile contract", result.stdout)
        self.assertIn("skill eval contract", result.stdout)

    def test_cli_agent_review_json_outputs_valid_record(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(HELPER_PATH),
                "agent-review",
                "--topic",
                "Agentic review contract",
                "--json",
            ],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        payload = json.loads(result.stdout)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(payload["record"]["recordType"], "axiom-agent-review")
        self.assertTrue(any(check["name"] == "agent review record" for check in payload["checks"]))
        self.assertIn("dsp-architect", {entry["role"] for entry in payload["record"]["roles"]})

    def test_cli_agent_review_writes_output_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "review.json"
            result = subprocess.run(
                [
                    sys.executable,
                    str(HELPER_PATH),
                    "agent-review",
                    "--topic",
                    "Agentic review file",
                    "--roles",
                    "coordinator",
                    "safety-auditor",
                    "--output",
                    str(output),
                ],
                cwd=REPO_ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            payload = json.loads(output.read_text(encoding="utf-8"))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual([entry["role"] for entry in payload["roles"]], ["coordinator", "safety-auditor"])
        self.assertIn("Axiom Multi-Role Review Record", result.stdout)

    def test_cli_agent_review_status_summarizes_completed_record(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            review = Path(directory) / "review.json"
            review.write_text(json.dumps(self._completed_agent_review()), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(HELPER_PATH), "agent-review-status", str(review), "--json"],
                cwd=REPO_ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
        payload = json.loads(result.stdout)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(payload["validation"], "pass")
        self.assertEqual(payload["lifecycleStatus"], "complete")
        self.assertEqual(payload["decision"], "continue")
        self.assertEqual(payload["completedRoleCount"], payload["roleCount"])

    def test_next_action_honors_completed_review_stop_decision(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            review = Path(directory) / "review.json"
            record = self._completed_agent_review()
            record["decision"] = "stop"
            review.write_text(json.dumps(record), encoding="utf-8")
            with patch.object(axiom_codex, "git_changed_paths", return_value=[]):
                payload = axiom_codex.next_action_payload(review_path=review)
        self.assertIsNone(payload["selectedTask"])
        self.assertEqual(payload["agentReview"]["decision"], "stop")
        self.assertIn("Stop the reviewed work", payload["recommendedAction"])

    def test_task_state_validates_machine_readable_backlog(self) -> None:
        data = axiom_codex.load_task_state()
        checks = axiom_codex.validate_task_state_data(data)
        task_ids = {task["id"] for task in data["tasks"]}
        self.assertIn("AX-TASK-022", task_ids)
        self.assertIn("AX-TASK-027", task_ids)
        self.assertIn("AX-TASK-028", task_ids)
        self.assertIn("AX-TASK-029", task_ids)
        self.assertIn("AX-TASK-030", task_ids)
        self.assertIn("AX-TASK-031", task_ids)
        self.assertIn("AX-TASK-032", task_ids)
        self.assertIn("AX-TASK-047", task_ids)
        self.assertFalse(any(check.status == "fail" for check in checks))
        listening_task = next(task for task in data["tasks"] if task["id"] == "AX-TASK-022")
        self.assertEqual(listening_task["status"], "complete-watch-item")
        self.assertEqual(listening_task["phase"], "done")

    def test_cli_task_state_lists_open_tasks(self) -> None:
        result = subprocess.run(
            [sys.executable, str(HELPER_PATH), "task-state"],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Axiom Task State", result.stdout)
        self.assertNotIn("AX-TASK-022", result.stdout)
        self.assertNotIn("AX-TASK-027", result.stdout)
        self.assertNotIn("AX-TASK-029", result.stdout)
        self.assertNotIn("AX-TASK-030", result.stdout)
        self.assertNotIn("AX-TASK-003", result.stdout)
        self.assertNotIn("AX-TASK-043", result.stdout)
        self.assertNotIn("AX-TASK-044", result.stdout)
        self.assertNotIn("AX-TASK-046", result.stdout)
        self.assertNotIn("AX-TASK-047", result.stdout)

    def test_cli_next_action_reports_planning_guidance(self) -> None:
        result = subprocess.run(
            [sys.executable, str(HELPER_PATH), "next-action", "--json"],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        payload = json.loads(result.stdout)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("recommendedAction", payload)
        self.assertIn("planning guidance", "\n".join(payload["boundaries"]))
        self.assertIsNone(payload["selectedTask"])
        self.assertIn("current local change batch", payload["recommendedAction"])
        self.assertTrue(payload["changedPaths"])
        self.assertFalse(payload["includeMaintenance"])

    def test_cli_next_action_can_select_initial_maintenance(self) -> None:
        task_state = self._initial_maintenance_task_state()
        with (
            patch.object(axiom_codex, "git_changed_paths", return_value=[]),
            patch.object(axiom_codex, "load_task_state", return_value=task_state),
        ):
            payload = axiom_codex.next_action_payload(evidence_path=None, include_maintenance=True)
        self.assertTrue(payload["includeMaintenance"])
        self.assertIsNotNone(payload["selectedTask"])
        self.assertEqual(payload["selectedTask"]["phase"], "initial")
        self.assertIn("maintenance task", payload["reason"])

    def test_next_action_dirty_tree_still_blocks_maintenance_recommendation(self) -> None:
        task_state = self._initial_maintenance_task_state()
        with (
            patch.object(axiom_codex, "git_changed_paths", return_value=["tools/fixture.py"]),
            patch.object(axiom_codex, "load_task_state", return_value=task_state),
        ):
            payload = axiom_codex.next_action_payload(evidence_path=None, include_maintenance=True)
        self.assertEqual(payload["reason"], "working tree has local changes")
        self.assertIsNotNone(payload["selectedTask"])
        self.assertEqual(payload["selectedTask"]["phase"], "initial")

    @staticmethod
    def _initial_maintenance_task_state() -> dict:
        return {
            "schemaVersion": 1,
            "lastUpdated": "2026-06-21",
            "source": "fixture",
            "tasks": [
                {
                    "id": "AX-TASK-999",
                    "status": "initial-implementation-complete",
                    "title": "Fixture maintenance",
                    "area": "Agentic Layer",
                    "phase": "initial",
                    "requiresApproval": False,
                    "blockedBy": [],
                    "nextAction": "Continue fixture maintenance.",
                }
            ],
        }

    @staticmethod
    def _completed_agent_review() -> dict:
        record = axiom_codex.build_agent_review_record("Completed fixture review", ["coordinator", "safety-auditor"])
        record["status"] = "complete"
        record["scope"] = "Review Agentic tooling changes."
        record["decision"] = "continue"
        record["evidenceStatus"] = "completed_review_not_authority"
        for entry in record["roles"]:
            entry["decision"] = "continue"
            entry["findings"] = ["No blocking issue found in the reviewed tooling scope."]
            entry["evidenceReferences"] = ["tests/test_axiom_codex_helper.py"]
        return record

    def test_cli_pi_handoff_prints_draft_without_execution(self) -> None:
        result = subprocess.run(
            [sys.executable, str(HELPER_PATH), "pi-handoff"],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("draft handoff only", result.stdout)
        self.assertIn("map-sub-gain", result.stdout)

    def test_cli_local_review_writes_reports_without_jdsp(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            json_output = root / "local-review.json"
            markdown_output = root / "local-review.md"
            result = subprocess.run(
                [
                    sys.executable,
                    str(HELPER_PATH),
                    "local-review",
                    "--skip-tests",
                    "--skip-knowledge",
                    "--json",
                    "--json-output",
                    str(json_output),
                    "--markdown-output",
                    str(markdown_output),
                ],
                cwd=REPO_ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            payload = json.loads(json_output.read_text(encoding="utf-8"))
            markdown = markdown_output.read_text(encoding="utf-8")
        expected_returncode = 1 if payload["status"] == "fail" else 0
        self.assertEqual(result.returncode, expected_returncode, result.stdout + result.stderr)
        self.assertEqual(payload["acceptedBaseline"]["version"], "v4.1.4.11")
        self.assertTrue(any(command["name"] == "guard-check" for command in payload["commands"]))
        self.assertFalse(any(command["name"] == "python tests" for command in payload["commands"]))
        self.assertIn("Axiom Local Review", markdown)
        self.assertIn("non-JDSP", "\n".join(payload["boundaries"]))


if __name__ == "__main__":
    unittest.main()
