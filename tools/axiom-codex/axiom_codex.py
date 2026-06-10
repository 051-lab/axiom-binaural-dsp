#!/usr/bin/env python3
"""Safe Codex-side helper commands for Axiom-DSP orchestration."""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import shlex
import subprocess
import sys
from dataclasses import dataclass
from typing import Any


REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
POLICY_PATH = REPO_ROOT / "tools" / "axiom-team" / "policy.json"
SYSTEM_STATUS = REPO_ROOT / "docs" / "system-status.md"
KNOWLEDGE_ROOT = REPO_ROOT / "docs" / "knowledge"
DEFAULT_LOCAL_INDEX = pathlib.Path.home() / ".local" / "share" / "axiom-knowledge" / "source-index.json"
ROLE_ROOT = REPO_ROOT / "tools" / "axiom-team" / "roles"
CODEX_ROOT = REPO_ROOT / "tools" / "axiom-codex"
COMMAND_SURFACE = CODEX_ROOT / "command_surface.json"
TASK_STATE = CODEX_ROOT / "task_state.json"
CODEX_AGENT_PROFILE_ROOT = CODEX_ROOT / "agent_profiles"
SKILL_EVAL_CASES = CODEX_ROOT / "skill_eval_cases.json"
SKILL_SOURCE = REPO_ROOT / "tools" / "codex-skills" / "axiom-engineering"
INSTALLED_SKILL = pathlib.Path.home() / ".codex" / "skills" / "axiom-engineering"
DEFAULT_SUB_GAIN_RUN = "20260603T004349-post-acceptance-v4-1-4-1-0d309b"
DEFAULT_SUB_GAIN_LABEL_REGEX = "electronic|hip hop|bass|flawed"
DEFAULT_SUB_GAIN_SLIDERS = [4, 10, 12]

DEFAULT_REVIEW_ROLES = [
    "dsp-architect",
    "eel-engineer",
    "measurement-engineer",
    "safety-auditor",
    "release-steward",
]

PRIVATE_AUDIO_EXTENSIONS = {
    ".aif",
    ".aiff",
    ".cue",
    ".flac",
    ".m4a",
    ".mp3",
    ".ogg",
    ".pcm",
    ".raw",
    ".wav",
    ".wave",
}

PRIVATE_PATH_PARTS = {
    "capture",
    "captures",
    "decoded",
    "local-material",
    "local_material",
    "processed",
    "rendered",
    "renders",
    "source-audio",
    "source_audio",
}

SECRET_PATH_PARTS = {
    ".env",
    "credential",
    "credentials",
    "secret",
    "secrets",
    "token",
    "tokens",
}

PRIVATE_CONTENT_PATTERNS = [
    re.compile(r"\b[A-Za-z]:\\Users\\[A-Za-z0-9._ -]+\\", re.IGNORECASE),
    re.compile(r"/home/[A-Za-z0-9._-]+/", re.IGNORECASE),
    re.compile(r"/mnt/c/Users/[A-Za-z0-9._ -]+/", re.IGNORECASE),
    re.compile(r'"localPath"\s*:', re.IGNORECASE),
]

SOURCE_REQUIRED_FIELDS = {"id", "title", "type", "topics", "axiomUse", "status"}
SOURCE_TYPES = {"book", "paper", "article", "documentation", "video", "other"}
SOURCE_STATUSES = {"unread", "reading", "summarized", "rejected"}
TASK_REQUIRED_FIELDS = {"id", "status", "title", "area", "phase", "requiresApproval", "blockedBy", "nextAction"}


@dataclass
class Check:
    name: str
    status: str
    detail: str


def run(command: list[str], timeout: int = 30) -> subprocess.CompletedProcess[str]:
    return run_in(REPO_ROOT, command, timeout)


def run_in(cwd: pathlib.Path, command: list[str], timeout: int = 30) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=cwd,
        text=True,
        capture_output=True,
        check=False,
        timeout=timeout,
    )


def load_policy() -> dict[str, Any]:
    return json.loads(POLICY_PATH.read_text(encoding="utf-8"))


def load_json(path: pathlib.Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def git_status() -> str:
    result = run(["git", "status", "-sb"])
    return result.stdout.strip() or result.stderr.strip()


def git_diff_name_only(*paths: str) -> list[str]:
    result = run(["git", "diff", "--name-only", "--", *paths])
    return [line for line in result.stdout.splitlines() if line.strip()]


def git_changed_paths(include_untracked: bool = True) -> list[str]:
    commands = [
        ["git", "diff", "--name-only"],
        ["git", "diff", "--cached", "--name-only"],
    ]
    if include_untracked:
        commands.append(["git", "ls-files", "--others", "--exclude-standard"])
    changed: set[str] = set()
    for command in commands:
        result = run(command)
        changed.update(line.strip() for line in result.stdout.splitlines() if line.strip())
    return sorted(changed)


def git_added_lines(path: str) -> str:
    result = run(["git", "diff", "--unified=0", "--", path])
    lines: list[str] = []
    for line in result.stdout.splitlines():
        if line.startswith("+") and not line.startswith("+++"):
            lines.append(line[1:])
    return "\n".join(lines)


def section(text: str, heading: str) -> str:
    pattern = rf"^## {re.escape(heading)}\n(.*?)(?=^## |\Z)"
    match = re.search(pattern, text, flags=re.MULTILINE | re.DOTALL)
    return match.group(1).strip() if match else ""


def command_status(result: subprocess.CompletedProcess[str]) -> str:
    return "pass" if result.returncode == 0 else "fail"


def command_payload(name: str, command: list[str], timeout: int = 120, cwd: pathlib.Path = REPO_ROOT) -> dict[str, Any]:
    try:
        result = run_in(cwd, command, timeout)
        return {
            "name": name,
            "command": command,
            "status": command_status(result),
            "returnCode": result.returncode,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "name": name,
            "command": command,
            "status": "fail",
            "returnCode": None,
            "stdout": (exc.stdout or "").strip() if isinstance(exc.stdout, str) else "",
            "stderr": f"timed out after {timeout} seconds",
        }


def parse_best_next_actions(system_text: str) -> list[str]:
    current = section(system_text, "Current Best Next Actions")
    actions: list[str] = []
    for line in current.splitlines():
        match = re.match(r"\d+\.\s+(.*)", line.strip())
        if match:
            actions.append(match.group(1).strip())
    return actions


def load_command_surface() -> dict[str, Any]:
    data = load_json(COMMAND_SURFACE)
    if not isinstance(data, dict) or not isinstance(data.get("commands"), list):
        raise SystemExit(f"invalid command surface: {COMMAND_SURFACE}")
    return data


def load_task_state() -> dict[str, Any]:
    data = load_json(TASK_STATE)
    if not isinstance(data, dict) or data.get("schemaVersion") != 1 or not isinstance(data.get("tasks"), list):
        raise SystemExit(f"invalid task state: {TASK_STATE}")
    return data


def validate_task_state_data(data: dict[str, Any]) -> list[Check]:
    checks: list[Check] = []
    seen: set[str] = set()
    tasks = data.get("tasks", [])
    if not isinstance(tasks, list):
        return [Check("tasks list", "fail", "`tasks` must be an array")]
    for task in tasks:
        if not isinstance(task, dict):
            checks.append(Check("task entry", "fail", "task entry must be an object"))
            continue
        task_id = str(task.get("id", "missing-id"))
        missing = sorted(TASK_REQUIRED_FIELDS - set(task))
        if missing:
            checks.append(Check("task required fields", "fail", f"{task_id}: missing {', '.join(missing)}"))
        if task_id in seen:
            checks.append(Check("duplicate task id", "fail", task_id))
        seen.add(task_id)
        if not re.match(r"^AX-TASK-\d{3}$", task_id):
            checks.append(Check("task id format", "fail", task_id))
        if not isinstance(task.get("blockedBy", []), list):
            checks.append(Check("task blockedBy", "fail", f"{task_id}: blockedBy must be an array"))
        if not isinstance(task.get("requiresApproval"), bool):
            checks.append(Check("task requiresApproval", "fail", f"{task_id}: requiresApproval must be boolean"))
    if not checks:
        checks.append(Check("task state", "pass", f"{len(tasks)} task(s) checked"))
    return checks


def task_priority(task: dict[str, Any]) -> tuple[int, str]:
    phase = str(task.get("phase", ""))
    if phase == "in-progress":
        return (0, str(task.get("id", "")))
    if phase == "ready":
        return (1, str(task.get("id", "")))
    if phase == "blocked-on-listening":
        return (2, str(task.get("id", "")))
    if phase == "requires-approval":
        return (3, str(task.get("id", "")))
    if phase == "initial":
        return (4, str(task.get("id", "")))
    if phase == "seeded":
        return (5, str(task.get("id", "")))
    return (9, str(task.get("id", "")))


def open_tasks(tasks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [task for task in tasks if str(task.get("phase")) != "done"]


def actionable_tasks(tasks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    blocked_phases = {"done", "blocked-on-listening", "requires-approval", "initial", "seeded"}
    return [
        task for task in tasks
        if str(task.get("phase")) not in blocked_phases
        and not task.get("blockedBy")
        and not task.get("requiresApproval")
    ]


def next_action_payload() -> dict[str, Any]:
    data = load_task_state()
    checks = validate_task_state_data(data)
    changed_paths = git_changed_paths()
    tasks = data["tasks"]
    actionable = sorted(actionable_tasks(tasks), key=task_priority)
    blocked = sorted(
        [task for task in open_tasks(tasks) if task.get("blockedBy") or task.get("requiresApproval")],
        key=task_priority,
    )
    if changed_paths:
        action = "Finish validating and reviewing the current local change batch before starting new work."
        reason = "working tree has local changes"
        task = actionable[0] if actionable else None
    elif actionable:
        task = actionable[0]
        action = f"{task['id']}: {task['nextAction']}"
        reason = f"{task['id']} is the highest-priority unblocked task"
    else:
        task = None
        action = "No unblocked task is available; inspect blocked or approval-gated tasks."
        reason = "all open tasks are blocked, approval-gated, initial-maintenance, or seeded"
    return {
        "status": "fail" if any(check.status == "fail" for check in checks) else "pass",
        "recommendedAction": action,
        "reason": reason,
        "selectedTask": task,
        "changedPaths": changed_paths,
        "blockedTasks": blocked,
        "checks": [check.__dict__ for check in checks],
        "boundaries": [
            "next-action is planning guidance only",
            "does not approve publication, merge, listening acceptance, or accepted-baseline promotion",
            "does not run JDSP",
        ],
    }


def task_state(args: argparse.Namespace) -> int:
    data = load_task_state()
    checks = validate_task_state_data(data)
    failed = any(check.status == "fail" for check in checks)
    tasks = data["tasks"]
    open_task_list = sorted(open_tasks(tasks), key=task_priority)
    if args.json:
        print(json.dumps({"taskState": data, "checks": [check.__dict__ for check in checks]}, indent=2, sort_keys=True))
        return 1 if failed else 0
    print("# Axiom Task State\n")
    print(f"- source: `{data.get('source', '')}`")
    print(f"- last updated: `{data.get('lastUpdated', '')}`")
    print(f"- task count: `{len(tasks)}`")
    print("\n## Checks\n")
    for check in checks:
        print(f"- {check.status}: {check.name} - {check.detail}")
    print("\n## Open Tasks\n")
    if not open_task_list:
        print("- none")
    else:
        print("| Task | Area | Phase | Approval | Blocked By | Next Action |")
        print("| --- | --- | --- | --- | --- | --- |")
        for task in open_task_list:
            blocked = ", ".join(task.get("blockedBy", [])) or "-"
            print(
                f"| {task['id']} {task['title']} | {task['area']} | {task['phase']} | "
                f"{markdown_bool(bool(task['requiresApproval']))} | {blocked} | {str(task['nextAction']).replace('|', '/')} |"
            )
    print("\nBoundary: task-state is planning metadata. It does not approve DSP, publication, merge, or listening decisions.")
    return 1 if failed else 0


def next_action(args: argparse.Namespace) -> int:
    payload = next_action_payload()
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 1 if payload["status"] == "fail" else 0
    print("# Axiom Next Action\n")
    print(f"Status: **{payload['status'].upper()}**\n")
    print(f"Recommended action: {payload['recommendedAction']}")
    print(f"Reason: {payload['reason']}\n")
    selected = payload.get("selectedTask")
    if selected:
        print("## Selected Task\n")
        print(f"- id: `{selected['id']}`")
        print(f"- title: {selected['title']}")
        print(f"- area: {selected['area']}")
        print(f"- phase: {selected['phase']}")
    if payload["changedPaths"]:
        print("\n## Current Change Batch\n")
        for path in payload["changedPaths"]:
            print(f"- `{path}`")
    if payload["blockedTasks"]:
        print("\n## Blocked Or Approval-Gated Tasks\n")
        for task in payload["blockedTasks"]:
            blocked = ", ".join(task.get("blockedBy", [])) or "approval required"
            print(f"- `{task['id']}` {task['title']}: {blocked}")
    print("\nBoundary: next-action is planning guidance. It does not approve DSP, publication, merge, listening, or baseline changes.")
    return 1 if payload["status"] == "fail" else 0


def command_surface_lookup() -> dict[str, dict[str, Any]]:
    return {
        str(command["name"]): command
        for command in load_command_surface()["commands"]
        if isinstance(command, dict) and command.get("name")
    }


def markdown_bool(value: bool) -> str:
    return "yes" if value else "no"


def command_surface(args: argparse.Namespace) -> int:
    data = load_command_surface()
    if args.json:
        print(json.dumps(data, indent=2, sort_keys=True))
        return 0
    print("# Axiom Codex Command Surface\n")
    print("| Command | Helper | JDSP | Approval | Purpose |")
    print("| --- | --- | --- | --- | --- |")
    for command in data["commands"]:
        helper = command.get("helperCommand") or command.get("piCommand") or "manual"
        print(
            "| {name} | `{helper}` | {jdsp} | {approval} | {purpose} |".format(
                name=command["name"],
                helper=helper,
                jdsp=markdown_bool(bool(command.get("touchesJDSP"))),
                approval=markdown_bool(bool(command.get("requiresApproval"))),
                purpose=str(command.get("purpose", "")).replace("|", "/"),
            )
        )
    print("\nBoundary: this registry is the repo-tracked command plan. Native Codex slash aliases should only wrap these safe helpers.")
    return 0


def status_summary(_: argparse.Namespace) -> int:
    policy = load_policy()
    accepted = policy["acceptedBaseline"]
    system_text = SYSTEM_STATUS.read_text(encoding="utf-8") if SYSTEM_STATUS.exists() else ""
    active_candidate = section(system_text, "Active Candidate") or "Unknown."
    open_investigation = section(system_text, "Current Open Investigation") or "Unknown."
    dsp_diffs = git_diff_name_only("src", "scripts")
    print("# Axiom Codex Status Summary\n")
    print(f"- accepted baseline: {accepted['version']}")
    print(f"- accepted script: {accepted['path']}")
    print(f"- accepted SHA-256: {accepted['sha256']}")
    print(f"- qualification: {accepted['qualificationDocument']}")
    print(f"- git status: {git_status()}")
    print(f"- DSP/script diff files: {len(dsp_diffs)}")
    if dsp_diffs:
        for item in dsp_diffs:
            print(f"  - {item}")
    print("\n## Active Candidate\n")
    print(active_candidate)
    print("\n## Current Open Investigation\n")
    print(open_investigation)
    print("\n## Safe Next Step\n")
    print("Use Codex for docs/tooling orchestration. Use Pi/harness for real-JDSP, candidate, publication, and merge workflows.")
    return 0


def ready_check(_: argparse.Namespace) -> int:
    checks: list[Check] = []
    diff_check = run(["git", "diff", "--check"])
    checks.append(Check("git diff --check", command_status(diff_check), diff_check.stdout.strip() or diff_check.stderr.strip() or "clean"))

    compile_targets = [
        "tools/axiom-codex/axiom_codex.py",
        "tools/install_axiom_codex_skill.py",
        "tools/generate_agentic_blueprint_pdf.py",
        "tools/generate_session_cover_art.py",
        "tools/generate_session_work_log_pdf.py",
    ]
    existing = [target for target in compile_targets if (REPO_ROOT / target).exists()]
    compile_result = run(["python3", "-m", "py_compile", *existing])
    checks.append(Check("python helper compile", command_status(compile_result), compile_result.stdout.strip() or compile_result.stderr.strip() or "compiled"))

    dsp_diffs = git_diff_name_only("src", "scripts")
    checks.append(Check("DSP/script diff guard", "pass" if not dsp_diffs else "warn", "no src/scripts diffs" if not dsp_diffs else "\n".join(dsp_diffs)))

    policy = load_policy()
    baseline = REPO_ROOT / policy["acceptedBaseline"]["path"]
    checks.append(Check("accepted baseline exists", "pass" if baseline.exists() else "fail", str(baseline.relative_to(REPO_ROOT)) if baseline.exists() else str(baseline)))

    surface = load_command_surface()
    checks.append(Check("Codex command surface", "pass" if surface.get("commands") else "fail", f"{len(surface.get('commands', []))} commands"))

    profile_files = sorted(CODEX_AGENT_PROFILE_ROOT.glob("*.md"))
    checks.append(Check("Codex agent profiles", "pass" if profile_files else "fail", f"{len(profile_files)} profiles"))

    eval_cases = load_skill_eval_cases()
    checks.append(Check("Axiom skill eval cases", "pass" if eval_cases.get("cases") else "fail", f"{len(eval_cases.get('cases', []))} cases"))

    print("# Axiom Codex Ready Check\n")
    failed = False
    for check in checks:
        print(f"- {check.status}: {check.name} - {check.detail}")
        failed = failed or check.status == "fail"
    return 1 if failed else 0


def local_review_payload(args: argparse.Namespace) -> dict[str, Any]:
    policy = load_policy()
    accepted = policy["acceptedBaseline"]
    system_text = SYSTEM_STATUS.read_text(encoding="utf-8") if SYSTEM_STATUS.exists() else ""
    changed_paths = git_changed_paths(include_untracked=not args.no_untracked)
    commands: list[dict[str, Any]] = [
        command_payload("git diff --check", ["git", "diff", "--check"], timeout=30),
        command_payload("guard-check", [sys.executable, str(pathlib.Path(__file__).resolve()), "guard-check", "--json"], timeout=60),
        command_payload("ready-check", [sys.executable, str(pathlib.Path(__file__).resolve()), "ready-check"], timeout=120),
        command_payload("task-state", [sys.executable, str(pathlib.Path(__file__).resolve()), "task-state", "--json"], timeout=60),
        command_payload("next-action", [sys.executable, str(pathlib.Path(__file__).resolve()), "next-action", "--json"], timeout=60),
    ]
    if not args.skip_knowledge:
        commands.append(
            command_payload(
                "knowledge-sources",
                [sys.executable, str(pathlib.Path(__file__).resolve()), "knowledge-sources", "--json"],
                timeout=60,
            )
        )
    if not args.skip_tests:
        commands.extend(
            [
                command_payload(
                    "python tests",
                    ["python3", "-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py"],
                    timeout=args.test_timeout,
                ),
                command_payload(
                    "node harness tests",
                    ["npm", "test"],
                    timeout=args.test_timeout,
                    cwd=REPO_ROOT / "tools" / "axiom-team",
                ),
            ]
        )
    best_next_actions = parse_best_next_actions(system_text)
    if changed_paths:
        recommended = "Finish validating and reviewing the current local change batch before starting a new DSP or publication step."
    elif best_next_actions:
        recommended = best_next_actions[0]
    else:
        recommended = "Run status-summary and inspect docs/system-status.md before choosing work."
    return {
        "acceptedBaseline": {
            "version": accepted["version"],
            "path": accepted["path"],
            "sha256": accepted["sha256"],
            "qualificationDocument": accepted["qualificationDocument"],
        },
        "gitStatus": git_status(),
        "changedPaths": changed_paths,
        "activeCandidate": section(system_text, "Active Candidate") or "Unknown.",
        "currentOpenInvestigation": section(system_text, "Current Open Investigation") or "Unknown.",
        "bestNextActions": best_next_actions,
        "recommendedNextAction": recommended,
        "commands": commands,
        "status": "fail" if any(command["status"] == "fail" for command in commands) else "pass",
        "boundaries": [
            "local-review is non-JDSP and does not create candidates",
            "passing checks do not approve publication, merge, or accepted-baseline promotion",
            "private Knowledge paths remain hidden by default",
        ],
    }


def one_line(text: str, limit: int = 220) -> str:
    compact = " ".join(text.split())
    return compact if len(compact) <= limit else compact[: limit - 3] + "..."


def local_review_markdown(payload: dict[str, Any]) -> str:
    accepted = payload["acceptedBaseline"]
    lines = [
        "# Axiom Local Review",
        "",
        f"Status: **{payload['status'].upper()}**",
        "",
        "## Baseline",
        "",
        f"- accepted baseline: `{accepted['version']}`",
        f"- accepted script: `{accepted['path']}`",
        f"- accepted SHA-256: `{accepted['sha256']}`",
        f"- qualification: `{accepted['qualificationDocument']}`",
        "",
        "Git status:",
        "",
        "```text",
        payload["gitStatus"],
        "```",
        "",
        "## Active Candidate",
        "",
        one_line(payload["activeCandidate"], 500),
        "",
        "## Current Open Investigation",
        "",
        one_line(payload["currentOpenInvestigation"], 700),
        "",
        "## Changed Paths",
        "",
    ]
    if payload["changedPaths"]:
        lines.extend(f"- `{path}`" for path in payload["changedPaths"])
    else:
        lines.append("- none")
    lines.extend(["", "## Checks", "", "| Check | Status | Detail |", "| --- | --- | --- |"])
    for command in payload["commands"]:
        detail = command["stderr"] or command["stdout"] or f"return code {command['returnCode']}"
        lines.append(f"| {command['name']} | {command['status'].upper()} | {one_line(detail).replace('|', '/')} |")
    lines.extend(["", "## Recommended Next Action", "", payload["recommendedNextAction"], "", "## Boundaries", ""])
    lines.extend(f"- {boundary}" for boundary in payload["boundaries"])
    lines.append("")
    return "\n".join(lines)


def local_review(args: argparse.Namespace) -> int:
    payload = local_review_payload(args)
    if args.json_output:
        args.json_output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.markdown_output:
        args.markdown_output.write_text(local_review_markdown(payload), encoding="utf-8")
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(local_review_markdown(payload).rstrip())
    return 1 if payload["status"] == "fail" else 0


def role_summary(role: str) -> str:
    path = ROLE_ROOT / f"{role}.md"
    if not path.exists():
        return "Role prompt missing."
    lines = [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    return " ".join(lines[1:]) if lines and lines[0].startswith("# ") else " ".join(lines[:3])


def markdown_section(text: str, heading: str) -> str:
    pattern = rf"^## {re.escape(heading)}\n(.*?)(?=^## |\Z)"
    match = re.search(pattern, text, flags=re.MULTILINE | re.DOTALL)
    return " ".join(line.strip() for line in match.group(1).splitlines() if line.strip()) if match else ""


def load_agent_profiles() -> list[tuple[str, pathlib.Path, str, str]]:
    profiles: list[tuple[str, pathlib.Path, str, str]] = []
    for path in sorted(CODEX_AGENT_PROFILE_ROOT.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        title_match = re.search(r"^#\s+(.+)$", text, flags=re.MULTILINE)
        title = title_match.group(1).strip() if title_match else path.stem
        purpose = markdown_section(text, "Purpose")
        profiles.append((path.stem, path, title, purpose))
    return profiles


def agent_profiles(args: argparse.Namespace) -> int:
    profiles = load_agent_profiles()
    if args.role:
        selected = [profile for profile in profiles if profile[0] == args.role]
        if not selected:
            raise SystemExit(f"unknown Codex agent profile: {args.role}")
        path = selected[0][1]
        print(path.read_text(encoding="utf-8").rstrip())
        return 0
    print("# Axiom Codex Agent Profiles\n")
    print("| Profile | Source | Purpose |")
    print("| --- | --- | --- |")
    for slug, path, title, purpose in profiles:
        rel = path.relative_to(REPO_ROOT)
        print(f"| {title} | `{rel}` | {purpose or slug} |")
    print("\nBoundary: profiles scope Codex planning/review behavior. Pi role prompts remain the execution-layer source for harness consultations.")
    return 0


def agent_review(args: argparse.Namespace) -> int:
    topic = args.topic.strip()
    roles = args.roles or DEFAULT_REVIEW_ROLES
    print("# Axiom Multi-Role Review Scaffold\n")
    print(f"Topic: {topic}\n")
    print("Scope: Define the narrow work area before implementation.")
    print("Forbidden scope: No accepted-baseline edits, private artifacts, or unscoped DSP changes.\n")
    print("Instructions: complete each role section with concrete findings before using this as evidence.\n")
    print("## Role Findings\n")
    for role in roles:
        print(f"### {role}")
        print(role_summary(role))
        print("\nFindings:\n- Add role-specific findings here.\n")
        print("Evidence needed:\n- Add required measurements, docs, or user approvals here.\n")
    print("## Decision\n")
    print("- continue / stop / delegate-to-Pi / needs-user-approval")
    return 0


def normalize_terms(query: str) -> list[str]:
    return [term.lower() for term in re.findall(r"[a-zA-Z0-9][a-zA-Z0-9+.-]*", query) if len(term) > 1]


def score_text(text: str, terms: list[str]) -> int:
    lowered = text.lower()
    return sum(lowered.count(term) for term in terms)


def load_local_sources(index_path: pathlib.Path) -> list[dict[str, Any]]:
    if not index_path.exists():
        return []
    data = json.loads(index_path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        return list(data.get("sources", []))
    return []


def repo_knowledge_source_ids() -> set[str]:
    ids: set[str] = set()
    for path in sorted(KNOWLEDGE_ROOT.rglob("*.md")):
        if "templates" in path.parts:
            continue
        text = path.read_text(encoding="utf-8")
        match = re.search(r"^Source ID:\s*(\S+)\s*$", text, flags=re.MULTILINE)
        if match:
            ids.add(match.group(1))
    return ids


def audit_knowledge_sources(index_path: pathlib.Path) -> tuple[list[dict[str, Any]], list[Check]]:
    checks: list[Check] = []
    expanded = index_path.expanduser()
    if not expanded.exists():
        return [], [Check("source index exists", "fail", str(expanded))]
    try:
        data = json.loads(expanded.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [], [Check("source index JSON", "fail", str(exc))]

    if not isinstance(data, dict):
        return [], [Check("source index shape", "fail", "top-level value must be an object")]
    checks.append(Check("schema version", "pass" if data.get("schemaVersion") == 1 else "fail", str(data.get("schemaVersion"))))
    raw_sources = data.get("sources")
    if not isinstance(raw_sources, list):
        return [], checks + [Check("sources list", "fail", "`sources` must be an array")]

    note_ids = repo_knowledge_source_ids()
    seen: set[str] = set()
    audited: list[dict[str, Any]] = []
    for source in raw_sources:
        if not isinstance(source, dict):
            checks.append(Check("source entry", "fail", "source entry must be an object"))
            continue
        source_id = str(source.get("id", "missing-id"))
        missing = sorted(SOURCE_REQUIRED_FIELDS - set(source))
        if missing:
            checks.append(Check("required fields", "fail", f"{source_id}: missing {', '.join(missing)}"))
        if source_id in seen:
            checks.append(Check("duplicate source id", "fail", source_id))
        seen.add(source_id)
        if source.get("type") not in SOURCE_TYPES:
            checks.append(Check("source type", "fail", f"{source_id}: {source.get('type')}"))
        if source.get("status") not in SOURCE_STATUSES:
            checks.append(Check("source status", "fail", f"{source_id}: {source.get('status')}"))
        if not isinstance(source.get("topics"), list):
            checks.append(Check("source topics", "fail", f"{source_id}: topics must be an array"))

        local_path = source.get("localPath")
        local_exists: bool | None = None
        if isinstance(local_path, str) and local_path:
            local_exists = pathlib.Path(local_path).expanduser().exists()
            if not local_exists:
                checks.append(Check("local source file", "fail", f"{source_id}: registered localPath does not exist"))

        note_exists = source_id in note_ids
        if not note_exists:
            checks.append(Check("repo-safe note", "warn", f"{source_id}: no repo note with matching Source ID"))
        audited.append(
            {
                "id": source_id,
                "title": source.get("title", ""),
                "type": source.get("type", ""),
                "status": source.get("status", ""),
                "topics": source.get("topics", []),
                "localPath": local_path,
                "localExists": local_exists,
                "repoNoteExists": note_exists,
            }
        )

    if not any(check.status == "fail" for check in checks):
        checks.append(Check("source index audit", "pass", f"{len(audited)} source(s) checked"))
    return audited, checks


def knowledge_query(args: argparse.Namespace) -> int:
    terms = normalize_terms(args.query)
    if not terms:
        raise SystemExit("query must include at least one searchable term")
    matches: list[tuple[int, str, str]] = []
    for path in sorted(KNOWLEDGE_ROOT.rglob("*.md")):
        if "templates" in path.parts:
            continue
        text = path.read_text(encoding="utf-8")
        score = score_text(text, terms)
        if score:
            excerpt = next((line.strip() for line in text.splitlines() if score_text(line, terms)), text.splitlines()[0] if text else "")
            matches.append((score, str(path.relative_to(REPO_ROOT)), excerpt[:240]))

    local_sources = load_local_sources(args.index.expanduser())
    source_matches: list[tuple[int, dict[str, Any]]] = []
    for source in local_sources:
        public_fields = {key: value for key, value in source.items() if args.show_private_paths or key != "localPath"}
        score = score_text(json.dumps(public_fields, sort_keys=True), terms)
        if score:
            source_matches.append((score, public_fields))

    print("# Axiom Knowledge Query\n")
    print(f"query: {args.query}\n")
    print("## Repo-Safe Notes\n")
    if matches:
        for score, path, excerpt in sorted(matches, reverse=True)[: args.limit]:
            print(f"- score {score}: {path} :: {excerpt}")
    else:
        print("- no repo-safe note matches")
    print("\n## Local Source Index\n")
    if not args.index.expanduser().exists():
        print(f"- local index not found: {args.index.expanduser()}")
    elif source_matches:
        for score, source in sorted(source_matches, key=lambda item: item[0], reverse=True)[: args.limit]:
            title = source.get("title", "untitled")
            source_id = source.get("id", "no-id")
            topics = ", ".join(source.get("topics", [])) if isinstance(source.get("topics"), list) else source.get("topics", "")
            print(f"- score {score}: {source_id} :: {title} :: {topics}")
            if source.get("axiomUse"):
                print(f"  axiomUse: {source['axiomUse']}")
            if args.show_private_paths and source.get("localPath"):
                print(f"  localPath: {source['localPath']}")
    else:
        print("- no local source matches")
    print("\nBoundary: Knowledge can inform tests; it is not proof of Axiom behavior.")
    return 0


def knowledge_sources(args: argparse.Namespace) -> int:
    sources, checks = audit_knowledge_sources(args.index)
    failed = any(check.status == "fail" for check in checks)
    if args.json:
        payload_sources = []
        for source in sources:
            visible = dict(source)
            if not args.show_private_paths:
                visible.pop("localPath", None)
            payload_sources.append(visible)
        print(json.dumps({"sources": payload_sources, "checks": [check.__dict__ for check in checks]}, indent=2, sort_keys=True))
        return 1 if failed else 0

    print("# Axiom Knowledge Sources\n")
    print(f"index: {args.index.expanduser() if args.show_private_paths else 'local source index'}\n")
    print("## Checks\n")
    for check in checks:
        print(f"- {check.status}: {check.name} - {check.detail}")
    print("\n## Sources\n")
    if not sources:
        print("- no sources found")
    else:
        print("| Source ID | Type | Status | Local File | Repo Note | Topics |")
        print("| --- | --- | --- | --- | --- | --- |")
        for source in sources:
            local_status = "exists" if source["localExists"] else "missing" if source["localExists"] is False else "not set"
            note_status = "yes" if source["repoNoteExists"] else "no"
            topics = ", ".join(source["topics"]) if isinstance(source["topics"], list) else ""
            print(f"| {source['id']} | {source['type']} | {source['status']} | {local_status} | {note_status} | {topics} |")
            if args.show_private_paths and source.get("localPath"):
                print(f"  localPath: {source['localPath']}")
    print("\nBoundary: this audits local Knowledge source registration. It does not copy PDFs into git or turn research into Axiom evidence.")
    return 1 if failed else 0


def pi_handoff_command(args: argparse.Namespace) -> list[str]:
    command = [
        "node",
        "tools/axiom-team/bin/axiom-team.mjs",
        "map-sub-gain",
        args.run_id,
    ]
    for slider_db in normalized_sub_gain_sliders(args.slider_db):
        command.extend(["--slider-db", str(slider_db)])
    if args.label_regex:
        command.extend(["--label-regex", args.label_regex])
    if args.repetitions is not None:
        command.extend(["--repetitions", str(args.repetitions)])
    return command


def normalized_sub_gain_sliders(slider_values: list[int] | None) -> list[int]:
    values = slider_values or DEFAULT_SUB_GAIN_SLIDERS
    normalized: list[int] = []
    for value in [4, *values]:
        if value not in normalized:
            normalized.append(value)
    return normalized


def shell_command(command: list[str]) -> str:
    return " ".join(shlex.quote(part) for part in command)


def pi_handoff(args: argparse.Namespace) -> int:
    policy = load_policy()
    accepted = policy["acceptedBaseline"]
    command = pi_handoff_command(args)
    if args.json:
        print(
            json.dumps(
                {
                    "mission": args.mission,
                    "runId": args.run_id,
                    "acceptedBaseline": accepted,
                    "command": command,
                    "requiresUserApprovalBeforeExecution": True,
                    "touchesJDSP": True,
                    "artifactPolicy": "raw captures, rendered audio, manifests, and generated reports remain local",
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 0

    print("# Axiom Pi Handoff\n")
    print(f"- mission: {args.mission}")
    print(f"- run id: {args.run_id}")
    print(f"- accepted baseline: {accepted['version']} ({accepted['path']})")
    print(f"- accepted SHA-256: {accepted['sha256']}")
    print("- status: draft handoff only; command not executed\n")
    print("## Pi Command\n")
    print("```bash")
    print(shell_command(command))
    print("```\n")
    print("## Preconditions\n")
    print("- User approval is required before running this real-JDSP command.")
    print("- Confirm the JDSP route is available and no other real-host measurement is active.")
    print("- Keep accepted and historical EEL files immutable.")
    print("- Keep raw captures, rendered audio, manifests, and generated reports outside git.\n")
    print("## Expected Evidence\n")
    print("- Targeted Sub Harmonics map for default +4 dB plus +10 dB and +12 dB dense/flawed material.")
    print("- Updated investigation gate or local evidence summary from the Pi harness.")
    print("- No candidate creation unless the evidence supports a scoped hypothesis and listening target.\n")
    print("Boundary: Codex generated this handoff; Pi/harness owns execution.")
    return 0


def path_parts(path: str) -> set[str]:
    return {part.lower() for part in pathlib.PurePosixPath(path.replace("\\", "/")).parts}


def is_docs_safe_schema(path: str) -> bool:
    lowered = path.lower().replace("\\", "/")
    return lowered.endswith("source-index.schema.json") or lowered.startswith("docs/knowledge/templates/")


def is_guard_fixture_path(path: str) -> bool:
    return path in {
        "tools/axiom-codex/axiom_codex.py",
        "tests/test_axiom_codex_helper.py",
    }


def classify_guard_paths(
    paths: list[str],
    text_by_path: dict[str, str] | None = None,
    policy: dict[str, Any] | None = None,
) -> list[Check]:
    policy = policy or load_policy()
    accepted_path = str(policy["acceptedBaseline"]["path"])
    text_by_path = text_by_path or {}
    findings: list[Check] = []
    seen: set[tuple[str, str]] = set()

    def add(status: str, name: str, detail: str) -> None:
        key = (name, detail)
        if key not in seen:
            findings.append(Check(name, status, detail))
            seen.add(key)

    for raw_path in paths:
        path = raw_path.replace("\\", "/").strip()
        if not path:
            continue
        lowered = path.lower()
        suffix = pathlib.PurePosixPath(lowered).suffix
        parts = path_parts(path)
        name = pathlib.PurePosixPath(lowered).name

        if path == accepted_path:
            add("fail", "accepted baseline immutability", f"{path} is the accepted baseline; do not edit it in place.")
        if lowered.startswith("src/") and suffix == ".eel":
            add("fail", "EEL script change gate", f"{path} touches Axiom DSP script scope; use scoped candidate/Pi gates before changing EEL.")
        if path == "tools/axiom-team/policy.json":
            add("fail", "policy approval gate", f"{path} changes accepted-baseline or harness policy; explicit user approval is required.")
        if suffix in PRIVATE_AUDIO_EXTENSIONS:
            add("fail", "private audio artifact", f"{path} looks like audio/cue material and must remain outside git.")
        if parts & PRIVATE_PATH_PARTS:
            add("fail", "private render/capture path", f"{path} looks like a local capture, decode, render, or source-material path.")
        if parts & SECRET_PATH_PARTS or name.startswith(".env"):
            add("fail", "credential path", f"{path} looks like a credential, token, or secret path.")
        if "manifest" in name and suffix in {".json", ".yaml", ".yml"} and not is_docs_safe_schema(path):
            add("fail", "local manifest path", f"{path} looks like a local material manifest; commit only sanitized summaries.")

        if not is_guard_fixture_path(path):
            text = text_by_path.get(raw_path) or text_by_path.get(path) or ""
            for pattern in PRIVATE_CONTENT_PATTERNS:
                if pattern.search(text):
                    add("fail", "private path content", f"{path} contains a private path or localPath field.")
                    break

    return findings


def guard_check(args: argparse.Namespace) -> int:
    paths = args.paths or git_changed_paths(include_untracked=not args.no_untracked)
    text_by_path = {path: git_added_lines(path) for path in paths if (REPO_ROOT / path).is_file()}
    findings = classify_guard_paths(paths, text_by_path=text_by_path)
    failed = any(finding.status == "fail" for finding in findings)
    if args.json:
        print(json.dumps([finding.__dict__ for finding in findings], indent=2, sort_keys=True))
        return 1 if failed else 0
    print("# Axiom Codex Guard Check\n")
    if not paths:
        print("- pass: no changed paths detected")
    elif not findings:
        print(f"- pass: {len(paths)} changed path(s) are clear of known Axiom guardrails")
    else:
        for finding in findings:
            print(f"- {finding.status}: {finding.name} - {finding.detail}")
    print("\nBoundary: this is a preflight guard. It does not approve publication, merge, candidate creation, or accepted-baseline promotion.")
    return 1 if failed else 0


def load_skill_eval_cases() -> dict[str, Any]:
    data = load_json(SKILL_EVAL_CASES)
    if not isinstance(data, dict) or not isinstance(data.get("cases"), list):
        raise SystemExit(f"invalid skill eval cases: {SKILL_EVAL_CASES}")
    return data


def skill_eval_corpus() -> str:
    sources: list[str] = []
    for path in [SKILL_SOURCE / "SKILL.md", *sorted((SKILL_SOURCE / "references").glob("*.md")), COMMAND_SURFACE]:
        if path.exists():
            sources.append(path.read_text(encoding="utf-8"))
    for path in sorted(CODEX_AGENT_PROFILE_ROOT.glob("*.md")):
        sources.append(path.read_text(encoding="utf-8"))
    return "\n".join(sources).lower()


def skill_eval(args: argparse.Namespace) -> int:
    data = load_skill_eval_cases()
    commands = command_surface_lookup()
    corpus = skill_eval_corpus()
    checks: list[Check] = []

    for case in data["cases"]:
        case_id = str(case.get("id", "unnamed"))
        prompt = str(case.get("prompt", "")).strip()
        expected = case.get("expected", {})
        if not prompt:
            checks.append(Check(case_id, "fail", "missing prompt"))
            continue
        helper_commands = expected.get("helperCommands", []) if isinstance(expected, dict) else []
        missing_commands = [name for name in helper_commands if name not in commands]
        if missing_commands:
            checks.append(Check(case_id, "fail", f"missing command surface entries: {', '.join(missing_commands)}"))
            continue
        required_terms = expected.get("requiredTerms", []) if isinstance(expected, dict) else []
        missing_terms = [term for term in required_terms if str(term).lower() not in corpus]
        if missing_terms:
            checks.append(Check(case_id, "fail", f"missing required behavior terms: {', '.join(missing_terms)}"))
            continue
        checks.append(Check(case_id, "pass", "fixture terms and helper command mappings present"))

    failed = any(check.status == "fail" for check in checks)
    if args.json:
        print(json.dumps([check.__dict__ for check in checks], indent=2, sort_keys=True))
        return 1 if failed else 0
    print("# Axiom Skill Behavior Eval\n")
    for check in checks:
        print(f"- {check.status}: {check.name} - {check.detail}")
    print("\nBoundary: this deterministic eval verifies skill fixtures and command mappings. It is not an LLM-quality score.")
    return 1 if failed else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("status-summary").set_defaults(func=status_summary)
    sub.add_parser("ready-check").set_defaults(func=ready_check)

    local = sub.add_parser("local-review")
    local.add_argument("--json", action="store_true")
    local.add_argument("--json-output", type=pathlib.Path)
    local.add_argument("--markdown-output", type=pathlib.Path)
    local.add_argument("--skip-tests", action="store_true")
    local.add_argument("--skip-knowledge", action="store_true")
    local.add_argument("--no-untracked", action="store_true")
    local.add_argument("--test-timeout", type=int, default=180)
    local.set_defaults(func=local_review)

    surface = sub.add_parser("command-surface")
    surface.add_argument("--json", action="store_true")
    surface.set_defaults(func=command_surface)

    tasks = sub.add_parser("task-state")
    tasks.add_argument("--json", action="store_true")
    tasks.set_defaults(func=task_state)

    next_parser = sub.add_parser("next-action")
    next_parser.add_argument("--json", action="store_true")
    next_parser.set_defaults(func=next_action)

    profiles = sub.add_parser("agent-profiles")
    profiles.add_argument("--role")
    profiles.set_defaults(func=agent_profiles)

    guard = sub.add_parser("guard-check")
    guard.add_argument("paths", nargs="*")
    guard.add_argument("--json", action="store_true")
    guard.add_argument("--no-untracked", action="store_true")
    guard.set_defaults(func=guard_check)

    evals = sub.add_parser("skill-eval")
    evals.add_argument("--json", action="store_true")
    evals.set_defaults(func=skill_eval)

    handoff = sub.add_parser("pi-handoff")
    handoff.add_argument("--mission", choices=["map-sub-gain"], default="map-sub-gain")
    handoff.add_argument("--run-id", default=DEFAULT_SUB_GAIN_RUN)
    handoff.add_argument("--slider-db", action="append", type=int)
    handoff.add_argument("--label-regex", default=DEFAULT_SUB_GAIN_LABEL_REGEX)
    handoff.add_argument("--repetitions", type=int)
    handoff.add_argument("--json", action="store_true")
    handoff.set_defaults(func=pi_handoff)

    review = sub.add_parser("agent-review")
    review.add_argument("--topic", required=True)
    review.add_argument("--roles", nargs="*", choices=[
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
    ])
    review.set_defaults(func=agent_review)

    knowledge = sub.add_parser("knowledge-query")
    knowledge.add_argument("query")
    knowledge.add_argument("--index", type=pathlib.Path, default=DEFAULT_LOCAL_INDEX)
    knowledge.add_argument("--limit", type=int, default=8)
    knowledge.add_argument("--show-private-paths", action="store_true")
    knowledge.set_defaults(func=knowledge_query)

    sources = sub.add_parser("knowledge-sources")
    sources.add_argument("--index", type=pathlib.Path, default=DEFAULT_LOCAL_INDEX)
    sources.add_argument("--json", action="store_true")
    sources.add_argument("--show-private-paths", action="store_true")
    sources.set_defaults(func=knowledge_sources)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
