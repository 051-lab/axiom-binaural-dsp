"""Tests for the Axiom Codex-side helper surface."""

from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
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
    def test_command_surface_has_required_safe_workflows(self) -> None:
        commands = axiom_codex.command_surface_lookup()
        for name in [
            "status-summary",
            "ready-check",
            "local-review",
            "guard-check",
            "command-surface",
            "task-state",
            "next-action",
            "agent-profiles",
            "agent-review",
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

    def test_task_state_validates_machine_readable_backlog(self) -> None:
        data = axiom_codex.load_task_state()
        checks = axiom_codex.validate_task_state_data(data)
        task_ids = {task["id"] for task in data["tasks"]}
        self.assertIn("AX-TASK-022", task_ids)
        self.assertIn("AX-TASK-027", task_ids)
        self.assertIn("AX-TASK-028", task_ids)
        self.assertFalse(any(check.status == "fail" for check in checks))
        self.assertTrue(any(task["phase"] == "blocked-on-listening" for task in data["tasks"]))

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
        self.assertIn("AX-TASK-022", result.stdout)
        self.assertIn("AX-TASK-027", result.stdout)

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
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(payload["acceptedBaseline"]["version"], "v4.1.4.11")
        self.assertTrue(any(command["name"] == "guard-check" for command in payload["commands"]))
        self.assertFalse(any(command["name"] == "python tests" for command in payload["commands"]))
        self.assertIn("Axiom Local Review", markdown)
        self.assertIn("non-JDSP", "\n".join(payload["boundaries"]))


if __name__ == "__main__":
    unittest.main()
