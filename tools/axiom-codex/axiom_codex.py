#!/usr/bin/env python3
"""Safe Codex-side helper commands for Axiom-DSP orchestration."""

from __future__ import annotations

import argparse
import datetime
import hashlib
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
DEFAULT_AIRWINDOWS_INDEX = pathlib.Path.home() / ".local" / "share" / "axiom-knowledge" / "sources" / "airwindows" / "index.json"
DEFAULT_EVIDENCE_CONFIG = pathlib.Path.home() / ".local" / "share" / "axiom" / "evidence-config.json"
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
REVIEW_DECISIONS = {"draft", "continue", "stop", "delegate-to-Pi", "needs-user-approval"}
REVIEW_STATUSES = {"draft", "complete"}
REVIEW_EVIDENCE_STATUSES = {
    "not_evidence_until_completed",
    "completed_review_not_authority",
}
REVIEW_RECORD_REQUIRED_FIELDS = {
    "schemaVersion",
    "recordType",
    "status",
    "topic",
    "scope",
    "forbiddenScope",
    "roles",
    "decision",
    "evidenceStatus",
    "boundaries",
}
REVIEW_ROLE_REQUIRED_FIELDS = {
    "role",
    "profileSource",
    "roleSource",
    "purpose",
    "findings",
    "evidenceNeeded",
    "evidenceReferences",
    "decision",
}

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
COMMAND_REQUIRED_FIELDS = {
    "name",
    "trigger",
    "nativeAlias",
    "layer",
    "helperCommand",
    "touchesJDSP",
    "requiresApproval",
    "purpose",
    "inputs",
    "outputs",
    "boundaries",
}
PROFILE_REQUIRED_SECTIONS = {"Purpose", "May Do", "Must Not Do", "Required Output"}
SKILL_EVAL_REQUIRED_FIELDS = {"id", "prompt", "expected"}
AIRWINDOWS_SOURCE_ID = "airwindows-open-source-dsp"
AIRWINDOWS_REPO_URL = "https://github.com/airwindows/airwindows"
AIRWINDOWS_INDEX_FIELDS = {
    "schemaVersion",
    "sourceId",
    "title",
    "repoUrl",
    "license",
    "pinnedCommit",
    "generatedBy",
    "boundary",
    "effects",
}
EVIDENCE_BOUNDARIES = [
    "ingested automation evidence is not listening acceptance",
    "ingestion does not create or promote a candidate, release, or accepted baseline",
    "raw reports and private paths remain local",
]
EVIDENCE_DECISIONS = {"pass", "pass_with_environment_warning", "investigate", "fail"}

AIRWINDOWS_TAG_RULES = [
    ("bass", ("bass", "sub", "low")),
    ("dynamics", ("compress", "comp", "limit", "gate", "density", "pressure", "transient")),
    ("filtering", ("filter", "eq", "tone", "capacitor", "slew", "biquad")),
    ("high-frequency", ("air", "desk", "deess", "de-ess", "treble", "high", "hiss")),
    ("nonlinear", ("nonlinear", "drive", "clip", "saturat", "distort", "tube", "console", "grit", "crunch")),
    ("spatial", ("stereo", "mid", "side", "width", "binaural", "distance", "space")),
    ("dither-noise-shaping", ("dither", "noise", "bit", "floating")),
]


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


def write_json(path: pathlib.Path, payload: Any) -> None:
    path.expanduser().parent.mkdir(parents=True, exist_ok=True)
    path.expanduser().write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def file_sha256(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


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


def parser_subcommands(parser: argparse.ArgumentParser) -> set[str]:
    for action in parser._actions:
        if isinstance(action, argparse._SubParsersAction):
            return set(action.choices)
    return set()


def validate_command_surface_data(
    data: dict[str, Any],
    runtime_commands: set[str] | None = None,
) -> list[Check]:
    checks: list[Check] = []
    commands = data.get("commands", [])
    if data.get("schemaVersion") != 1:
        checks.append(Check("command surface schema", "fail", "schemaVersion must be 1"))
    if not isinstance(commands, list):
        return [Check("command surface commands", "fail", "`commands` must be an array")]

    seen_names: set[str] = set()
    seen_aliases: set[str] = set()
    runtime_commands = runtime_commands if runtime_commands is not None else parser_subcommands(build_parser())
    for command in commands:
        if not isinstance(command, dict):
            checks.append(Check("command surface entry", "fail", "command entry must be an object"))
            continue
        name = str(command.get("name", "missing-name"))
        missing = sorted(COMMAND_REQUIRED_FIELDS - set(command))
        if missing:
            checks.append(Check("command required fields", "fail", f"{name}: missing {', '.join(missing)}"))
        if name in seen_names:
            checks.append(Check("duplicate command name", "fail", name))
        seen_names.add(name)
        if not re.fullmatch(r"[a-z][a-z0-9-]*", name):
            checks.append(Check("command name format", "fail", name))

        alias = str(command.get("nativeAlias", ""))
        if alias in seen_aliases:
            checks.append(Check("duplicate native alias", "fail", alias))
        seen_aliases.add(alias)
        if not re.fullmatch(r"/axiom-[a-z0-9-]+", alias):
            checks.append(Check("native alias format", "fail", f"{name}: {alias or 'missing'}"))

        for field in ("touchesJDSP", "requiresApproval"):
            if not isinstance(command.get(field), bool):
                checks.append(Check(f"command {field}", "fail", f"{name}: {field} must be boolean"))
        if command.get("touchesJDSP") and not command.get("requiresApproval"):
            checks.append(Check("JDSP approval boundary", "fail", f"{name}: JDSP commands must require approval"))
        for field in ("inputs", "outputs", "boundaries"):
            value = command.get(field)
            if not isinstance(value, list) or not all(isinstance(item, str) and item.strip() for item in value):
                checks.append(Check(f"command {field}", "fail", f"{name}: {field} must be a non-empty string array"))
        for field in ("trigger", "layer", "helperCommand", "purpose"):
            if not isinstance(command.get(field), str) or not command[field].strip():
                checks.append(Check(f"command {field}", "fail", f"{name}: {field} must be non-empty text"))

        helper = str(command.get("helperCommand", ""))
        try:
            helper_parts = shlex.split(helper)
        except ValueError as exc:
            checks.append(Check("helper command syntax", "fail", f"{name}: {exc}"))
            helper_parts = []
        if "tools/axiom-codex/axiom_codex.py" in helper_parts:
            script_index = helper_parts.index("tools/axiom-codex/axiom_codex.py")
            mapped = helper_parts[script_index + 1] if len(helper_parts) > script_index + 1 else ""
            if mapped != name:
                checks.append(Check("helper command mapping", "fail", f"{name}: maps to {mapped or 'no subcommand'}"))
            if mapped not in runtime_commands:
                checks.append(Check("helper runtime command", "fail", f"{name}: runtime subcommand is missing"))

    missing_registry = sorted(runtime_commands - seen_names)
    if missing_registry:
        checks.append(Check("unregistered runtime command", "fail", ", ".join(missing_registry)))
    if not checks:
        checks.append(Check("command surface contract", "pass", f"{len(commands)} command(s) checked"))
    return checks


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


def actionable_tasks(tasks: list[dict[str, Any]], include_maintenance: bool = False) -> list[dict[str, Any]]:
    blocked_phases = {"done", "blocked-on-listening", "requires-approval", "seeded"}
    if not include_maintenance:
        blocked_phases.add("initial")
    return [
        task for task in tasks
        if str(task.get("phase")) not in blocked_phases
        and not task.get("blockedBy")
        and not task.get("requiresApproval")
    ]


def next_action_payload(
    evidence_path: pathlib.Path | None = None,
    include_maintenance: bool = False,
    review_path: pathlib.Path | None = None,
) -> dict[str, Any]:
    data = load_task_state()
    checks = validate_task_state_data(data)
    changed_paths = git_changed_paths()
    evidence = evidence_status_payload(evidence_path) if evidence_path else None
    review = agent_review_status_payload(review_path) if review_path else None
    tasks = data["tasks"]
    actionable = sorted(actionable_tasks(tasks, include_maintenance=include_maintenance), key=task_priority)
    blocked = sorted(
        [task for task in open_tasks(tasks) if task.get("blockedBy") or task.get("requiresApproval")],
        key=task_priority,
    )
    if evidence and evidence["status"] == "fail":
        action = "Repair or replace the invalid qualification evidence bundle before using it for planning."
        reason = "qualification evidence bundle validation failed"
        task = None
    elif evidence and evidence["aggregateDecision"] in {"fail", "investigate"}:
        action = "Review the qualification evidence failures before starting dependent product or release work."
        reason = f"qualification evidence decision is {evidence['aggregateDecision']}"
        task = None
    elif review and review["validation"] == "fail":
        action = "Repair the invalid Agentic review record before using its decision for planning."
        reason = "Agentic review record validation failed"
        task = None
    elif review and review["lifecycleStatus"] == "draft":
        action = "Complete the Agentic review findings and evidence references before dependent work."
        reason = "Agentic review record is still draft"
        task = None
    elif review and review["decision"] == "stop":
        action = "Stop the reviewed work and resolve the recorded findings before continuing."
        reason = "completed Agentic review decision is stop"
        task = None
    elif review and review["decision"] == "delegate-to-Pi":
        action = "Prepare a bounded Pi handoff for the reviewed work; do not run JDSP from next-action."
        reason = "completed Agentic review decision is delegate-to-Pi"
        task = None
    elif review and review["decision"] == "needs-user-approval":
        action = "Request explicit user approval for the reviewed action before continuing."
        reason = "completed Agentic review decision requires user approval"
        task = None
    elif changed_paths:
        action = "Finish validating and reviewing the current local change batch before starting new work."
        reason = "working tree has local changes"
        task = actionable[0] if actionable else None
    elif actionable:
        task = actionable[0]
        action = f"{task['id']}: {task['nextAction']}"
        reason = (
            f"{task['id']} is the highest-priority unblocked maintenance task"
            if str(task.get("phase")) == "initial"
            else f"{task['id']} is the highest-priority unblocked task"
        )
    else:
        task = None
        action = "No unblocked task is available; inspect blocked or approval-gated tasks."
        reason = "all open tasks are blocked, approval-gated, initial-maintenance, or seeded"
    return {
        "status": "fail" if any(check.status == "fail" for check in checks) else "pass",
        "recommendedAction": action,
        "reason": reason,
        "selectedTask": task,
        "qualificationEvidence": evidence,
        "agentReview": review,
        "changedPaths": changed_paths,
        "blockedTasks": blocked,
        "includeMaintenance": include_maintenance,
        "checks": [check.__dict__ for check in checks],
        "boundaries": [
            "next-action is planning guidance only",
            "does not approve publication, merge, listening acceptance, or accepted-baseline promotion",
            "does not run JDSP",
            "initial-maintenance tasks are selected only when explicitly requested",
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
    evidence_path = configured_evidence_path(args.evidence, args.no_evidence)
    payload = next_action_payload(
        evidence_path,
        include_maintenance=args.include_maintenance,
        review_path=args.review,
    )
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
    evidence = payload.get("qualificationEvidence")
    if evidence:
        print("\n## Qualification Evidence\n")
        print(f"- status: `{evidence['status']}`")
        print(f"- aggregate decision: `{evidence.get('aggregateDecision', 'unknown')}`")
        print(f"- records: `{evidence.get('recordCount', 0)}`")
        print(f"- warnings: `{evidence.get('warningCount', 0)}`")
        print(f"- critical failures: `{evidence.get('criticalFailureCount', 0)}`")
    review = payload.get("agentReview")
    if review:
        print("\n## Agent Review\n")
        print(f"- validation: `{review['validation']}`")
        print(f"- lifecycle status: `{review['lifecycleStatus']}`")
        print(f"- decision: `{review['decision']}`")
        print(f"- roles completed: `{review['completedRoleCount']}/{review['roleCount']}`")
    if payload["blockedTasks"]:
        print("\n## Blocked Or Approval-Gated Tasks\n")
        for task in payload["blockedTasks"]:
            blocked = ", ".join(task.get("blockedBy", [])) or "approval required"
            print(f"- `{task['id']}` {task['title']}: {blocked}")
    print("\n## Boundaries\n")
    for boundary in payload["boundaries"]:
        print(f"- {boundary}")
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


def evidence_source_fields(path: pathlib.Path, show_private_paths: bool) -> dict[str, Any]:
    fields: dict[str, Any] = {
        "sourceName": path.name,
        "sourceSha256": file_sha256(path),
    }
    if show_private_paths:
        fields["sourcePath"] = str(path.resolve())
    return fields


def normalized_gate(name: str, passed: bool, detail: str = "") -> dict[str, Any]:
    gate = {"name": name, "passed": passed}
    if detail:
        gate["detail"] = detail
    return gate


def normalize_soak_evidence(
    path: pathlib.Path,
    data: dict[str, Any],
    show_private_paths: bool,
) -> dict[str, Any]:
    raw_gates = data.get("gates")
    metrics = data.get("metrics")
    if not isinstance(raw_gates, list) or not isinstance(metrics, dict):
        raise ValueError("soak report requires `gates` array and `metrics` object")

    gates = [
        normalized_gate(
            str(gate.get("name", "unnamed gate")),
            bool(gate.get("passed")),
            str(gate.get("detail", "")),
        )
        for gate in raw_gates
        if isinstance(gate, dict)
    ]
    failed_names = {gate["name"] for gate in gates if not gate["passed"]}
    power = data.get("power") if isinstance(data.get("power"), dict) else {}
    source_changes = power.get("sourceChanges") if isinstance(power.get("sourceChanges"), list) else []
    integrity_metric_names = [
        "processedFrames",
        "packets",
        "droppedFrames",
        "conversionErrors",
        "discontinuities",
        "renderStarvations",
        "renderErrors",
        "dspCalls",
        "dspDeadlineMisses",
        "dspDeadlineMissRate",
        "dspCriticalStalls",
        "maximumDspUs",
        "maximumRenderPadding",
        "renderBufferFrames",
        "maximumRenderPaddingRate",
        "crashRecoveries",
        "configReloads",
    ]
    selected_metrics = {name: metrics[name] for name in integrity_metric_names if name in metrics}
    zero_loss = all(
        metrics.get(name) == 0
        for name in [
            "droppedFrames",
            "conversionErrors",
            "renderStarvations",
            "renderErrors",
            "dspCriticalStalls",
        ]
    )
    environment_gate_names = {"power source remained stable"}
    coupled_discontinuity = (
        "bounded discontinuities" in failed_names
        and bool(source_changes)
        and zero_loss
    )
    ignored_for_integrity = set(environment_gate_names)
    if coupled_discontinuity:
        ignored_for_integrity.add("bounded discontinuities")
    critical_failures = sorted(failed_names - ignored_for_integrity)
    warnings: list[str] = []
    if failed_names & environment_gate_names:
        warnings.append(f"power source changed {len(source_changes)} time(s) during the run")
    if coupled_discontinuity:
        warnings.append(
            "discontinuity gate failed during a recorded power transition with zero dropped frames, "
            "starvation, conversion errors, render errors, or critical stalls"
        )

    source_result = str(data.get("result", "unknown"))
    if critical_failures:
        decision = "fail"
    elif source_result == "pass" and not warnings:
        decision = "pass"
    elif warnings and not critical_failures:
        decision = "pass_with_environment_warning"
    else:
        decision = "investigate"

    route = data.get("route") if isinstance(data.get("route"), dict) else {}
    capture = route.get("capture") if isinstance(route.get("capture"), dict) else {}
    output = route.get("output") if isinstance(route.get("output"), dict) else {}
    return {
        **evidence_source_fields(path, show_private_paths),
        "kind": "windows-host-soak",
        "scope": "windows-host-endurance",
        "sourceResult": source_result,
        "decision": decision,
        "startedAt": data.get("startedAt"),
        "endedAt": data.get("endedAt"),
        "route": {
            "captureName": capture.get("name"),
            "outputName": output.get("name"),
        },
        "metrics": selected_metrics,
        "gates": gates,
        "criticalFailures": critical_failures,
        "warnings": warnings,
    }


def normalize_manual_recovery_evidence(
    path: pathlib.Path,
    data: dict[str, Any],
    show_private_paths: bool,
) -> dict[str, Any]:
    raw_gates = data.get("gates")
    if not isinstance(raw_gates, dict):
        raise ValueError("manual recovery report requires `gates` object")
    gates: list[dict[str, Any]] = []
    for name, value in raw_gates.items():
        if isinstance(value, bool):
            gates.append(normalized_gate(name, value))
        elif isinstance(value, (int, float)):
            gates.append(normalized_gate(name, value == 0, str(value)))
        else:
            gates.append(normalized_gate(name, False, f"unsupported value: {value!r}"))
    failed = sorted(gate["name"] for gate in gates if not gate["passed"])
    source_result = str(data.get("result", "unknown"))
    if failed or source_result == "fail":
        decision = "fail"
    elif source_result == "pass":
        decision = "pass"
    else:
        decision = "investigate"

    route = data.get("qualifiedRoute") if isinstance(data.get("qualifiedRoute"), dict) else {}
    standby = data.get("modernStandby") if isinstance(data.get("modernStandby"), dict) else {}
    return {
        **evidence_source_fields(path, show_private_paths),
        "kind": "windows-manual-recovery",
        "scope": "windows-route-and-sleep-recovery",
        "sourceResult": source_result,
        "decision": decision,
        "route": {
            "captureName": route.get("captureName"),
            "outputName": route.get("outputName"),
            "bufferMs": route.get("bufferMs"),
        },
        "modernStandbyObserved": bool(standby.get("enteredEventId") and standby.get("exitedEventId")),
        "gates": gates,
        "criticalFailures": failed,
        "warnings": [],
    }


def normalize_evidence_file(path: pathlib.Path, show_private_paths: bool = False) -> dict[str, Any]:
    expanded = path.expanduser()
    if not expanded.is_file():
        raise ValueError(f"evidence file does not exist: {path}")
    try:
        data = json.loads(expanded.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON in {path.name}: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError(f"evidence file must contain a JSON object: {path.name}")
    if isinstance(data.get("gates"), list) and isinstance(data.get("metrics"), dict):
        return normalize_soak_evidence(expanded, data, show_private_paths)
    if isinstance(data.get("gates"), dict) and isinstance(data.get("qualifiedRoute"), dict):
        return normalize_manual_recovery_evidence(expanded, data, show_private_paths)
    raise ValueError(f"unsupported qualification evidence schema: {path.name}")


def aggregate_evidence_decision(records: list[dict[str, Any]]) -> str:
    decisions = {str(record.get("decision")) for record in records}
    for decision in ["fail", "investigate", "pass_with_environment_warning", "pass"]:
        if decision in decisions:
            return decision
    return "investigate"


def build_evidence_bundle(paths: list[pathlib.Path], show_private_paths: bool = False) -> dict[str, Any]:
    records = [normalize_evidence_file(path, show_private_paths) for path in paths]
    return {
        "schemaVersion": 1,
        "recordType": "axiom-qualification-evidence-bundle",
        "generatedAtUtc": datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z"),
        "aggregateDecision": aggregate_evidence_decision(records),
        "records": records,
        "boundaries": EVIDENCE_BOUNDARIES,
    }


def validate_evidence_bundle(data: Any) -> list[Check]:
    if not isinstance(data, dict):
        return [Check("evidence bundle shape", "fail", "top-level value must be an object")]
    checks: list[Check] = []
    if data.get("schemaVersion") != 1:
        checks.append(Check("evidence schema version", "fail", str(data.get("schemaVersion"))))
    if data.get("recordType") != "axiom-qualification-evidence-bundle":
        checks.append(Check("evidence record type", "fail", str(data.get("recordType"))))
    decision = data.get("aggregateDecision")
    if decision not in EVIDENCE_DECISIONS:
        checks.append(Check("evidence aggregate decision", "fail", str(decision)))
    records = data.get("records")
    if not isinstance(records, list) or not records:
        checks.append(Check("evidence records", "fail", "records must be a non-empty array"))
        return checks
    for index, record in enumerate(records):
        if not isinstance(record, dict):
            checks.append(Check("evidence record shape", "fail", f"record {index} must be an object"))
            continue
        missing = [
            field
            for field in ["kind", "scope", "sourceName", "sourceSha256", "sourceResult", "decision", "gates"]
            if field not in record
        ]
        if missing:
            checks.append(Check("evidence record fields", "fail", f"record {index}: missing {', '.join(missing)}"))
        if record.get("decision") not in EVIDENCE_DECISIONS:
            checks.append(Check("evidence record decision", "fail", f"record {index}: {record.get('decision')}"))
        source_hash = record.get("sourceSha256")
        if not isinstance(source_hash, str) or re.fullmatch(r"[0-9a-f]{64}", source_hash) is None:
            checks.append(Check("evidence source hash", "fail", f"record {index}: invalid SHA-256"))
        if "sourcePath" in record:
            checks.append(Check("evidence private path", "warn", f"record {index} contains sourcePath"))
    if not any(check.status == "fail" for check in checks):
        checks.append(Check("evidence bundle", "pass", f"{len(records)} record(s) checked"))
    return checks


def evidence_status_payload(path: pathlib.Path) -> dict[str, Any]:
    expanded = path.expanduser()
    if not expanded.is_file():
        return {
            "status": "fail",
            "aggregateDecision": "unknown",
            "recordCount": 0,
            "warningCount": 0,
            "criticalFailureCount": 0,
            "checks": [Check("evidence bundle exists", "fail", path.name).__dict__],
            "boundaries": EVIDENCE_BOUNDARIES,
        }
    try:
        data = json.loads(expanded.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as exc:
        return {
            "status": "fail",
            "aggregateDecision": "unknown",
            "recordCount": 0,
            "warningCount": 0,
            "criticalFailureCount": 0,
            "checks": [Check("evidence bundle JSON", "fail", str(exc)).__dict__],
            "boundaries": EVIDENCE_BOUNDARIES,
        }
    checks = validate_evidence_bundle(data)
    records = data.get("records", []) if isinstance(data, dict) else []
    valid_records = [record for record in records if isinstance(record, dict)]
    return {
        "status": "fail" if any(check.status == "fail" for check in checks) else "pass",
        "aggregateDecision": data.get("aggregateDecision", "unknown") if isinstance(data, dict) else "unknown",
        "generatedAtUtc": data.get("generatedAtUtc") if isinstance(data, dict) else None,
        "recordCount": len(valid_records),
        "warningCount": sum(len(record.get("warnings", [])) for record in valid_records if isinstance(record.get("warnings", []), list)),
        "criticalFailureCount": sum(
            len(record.get("criticalFailures", []))
            for record in valid_records
            if isinstance(record.get("criticalFailures", []), list)
        ),
        "records": [
            {
                "kind": record.get("kind"),
                "scope": record.get("scope"),
                "sourceName": record.get("sourceName"),
                "sourceResult": record.get("sourceResult"),
                "decision": record.get("decision"),
                "warningCount": len(record.get("warnings", [])) if isinstance(record.get("warnings", []), list) else 0,
                "criticalFailureCount": (
                    len(record.get("criticalFailures", []))
                    if isinstance(record.get("criticalFailures", []), list)
                    else 0
                ),
            }
            for record in valid_records
        ],
        "checks": [check.__dict__ for check in checks],
        "boundaries": EVIDENCE_BOUNDARIES,
    }


def evidence_status(args: argparse.Namespace) -> int:
    payload = evidence_status_payload(args.bundle)
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 1 if payload["status"] == "fail" else 0
    print("# Axiom Qualification Evidence Status\n")
    print(f"- validation: `{payload['status']}`")
    print(f"- aggregate decision: `{payload['aggregateDecision']}`")
    print(f"- records: `{payload['recordCount']}`")
    print(f"- warnings: `{payload['warningCount']}`")
    print(f"- critical failures: `{payload['criticalFailureCount']}`")
    print("\n## Records\n")
    for record in payload.get("records", []):
        print(
            f"- `{record['kind']}` `{record['sourceName']}`: decision={record['decision']}; "
            f"warnings={record['warningCount']}; critical failures={record['criticalFailureCount']}"
        )
    print("\n## Checks\n")
    for check in payload["checks"]:
        print(f"- {check['status']}: {check['name']} - {check['detail']}")
    print("\nBoundary: " + "; ".join(EVIDENCE_BOUNDARIES) + ".")
    return 1 if payload["status"] == "fail" else 0


def evidence_bundle_sort_key(path: pathlib.Path) -> tuple[str, int, str]:
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError):
        return ("", 0, path.name)
    generated = data.get("generatedAtUtc", "") if isinstance(data, dict) else ""
    try:
        modified = path.stat().st_mtime_ns
    except OSError:
        modified = 0
    return (str(generated), modified, path.name)


def evidence_catalog_payload(directory: pathlib.Path) -> dict[str, Any]:
    expanded = directory.expanduser()
    if not expanded.is_dir():
        return {
            "status": "fail",
            "bundleCount": 0,
            "validBundleCount": 0,
            "latestBundleName": None,
            "latestBundle": None,
            "bundles": [],
            "checks": [Check("evidence directory", "fail", "directory does not exist").__dict__],
            "boundaries": EVIDENCE_BOUNDARIES,
        }
    bundles: list[dict[str, Any]] = []
    for path in sorted(expanded.glob("*.json")):
        status = evidence_status_payload(path)
        bundles.append(
            {
                "name": path.name,
                "path": path,
                "status": status["status"],
                "aggregateDecision": status["aggregateDecision"],
                "generatedAtUtc": status.get("generatedAtUtc"),
                "recordCount": status["recordCount"],
                "warningCount": status["warningCount"],
                "criticalFailureCount": status["criticalFailureCount"],
            }
        )
    valid = [bundle for bundle in bundles if bundle["status"] == "pass"]
    latest = max(valid, key=lambda bundle: evidence_bundle_sort_key(bundle["path"])) if valid else None
    return {
        "status": "pass" if latest else "fail",
        "bundleCount": len(bundles),
        "validBundleCount": len(valid),
        "latestBundleName": latest["name"] if latest else None,
        "latestBundle": latest["path"] if latest else None,
        "bundles": [
            {key: value for key, value in bundle.items() if key != "path"}
            for bundle in bundles
        ],
        "checks": [
            Check(
                "evidence catalog",
                "pass" if latest else "fail",
                f"{len(valid)} valid bundle(s) from {len(bundles)} JSON file(s)",
            ).__dict__
        ],
        "boundaries": EVIDENCE_BOUNDARIES,
    }


def load_evidence_config() -> pathlib.Path | None:
    if not DEFAULT_EVIDENCE_CONFIG.is_file():
        return None
    try:
        data = json.loads(DEFAULT_EVIDENCE_CONFIG.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError):
        return None
    directory = data.get("directory") if isinstance(data, dict) else None
    return pathlib.Path(directory).expanduser() if isinstance(directory, str) and directory else None


def save_evidence_config(directory: pathlib.Path) -> None:
    write_json(
        DEFAULT_EVIDENCE_CONFIG,
        {
            "schemaVersion": 1,
            "directory": str(directory.expanduser().resolve()),
            "boundary": "local-only configuration; do not commit",
        },
    )


def evidence_directory_is_default(directory: pathlib.Path) -> bool:
    configured = load_evidence_config()
    if configured is None:
        return False
    try:
        return configured.resolve() == directory.expanduser().resolve()
    except OSError:
        return False


def configured_evidence_path(explicit: pathlib.Path | None, disabled: bool = False) -> pathlib.Path | None:
    if disabled:
        return None
    if explicit:
        return explicit
    directory = load_evidence_config()
    if directory is None:
        return None
    catalog = evidence_catalog_payload(directory)
    latest = catalog.get("latestBundle")
    return latest if isinstance(latest, pathlib.Path) else None


def evidence_catalog(args: argparse.Namespace) -> int:
    payload = evidence_catalog_payload(args.directory)
    if args.set_default and payload["status"] == "pass":
        save_evidence_config(args.directory)
    default_configured = payload["status"] == "pass" and evidence_directory_is_default(args.directory)
    public_payload = {
        **payload,
        "latestBundle": payload["latestBundleName"],
        "defaultConfigured": default_configured,
    }
    if args.json:
        print(json.dumps(public_payload, indent=2, sort_keys=True))
        return 1 if payload["status"] == "fail" else 0
    print("# Axiom Qualification Evidence Catalog\n")
    print(f"- validation: `{payload['status']}`")
    print(f"- JSON files: `{payload['bundleCount']}`")
    print(f"- valid bundles: `{payload['validBundleCount']}`")
    print(f"- latest valid bundle: `{payload['latestBundleName'] or 'none'}`")
    if default_configured:
        print("- default evidence directory: configured locally")
    print("\n## Bundles\n")
    for bundle in payload["bundles"]:
        print(
            f"- `{bundle['name']}`: validation={bundle['status']}; "
            f"decision={bundle['aggregateDecision']}; records={bundle['recordCount']}"
        )
    print("\nBoundary: catalog paths remain in local configuration and are not printed or committed.")
    return 1 if payload["status"] == "fail" else 0


def evidence_ingest(args: argparse.Namespace) -> int:
    try:
        payload = build_evidence_bundle(args.paths, args.show_private_paths)
    except ValueError as exc:
        print(f"evidence-ingest: {exc}", file=sys.stderr)
        return 2
    if args.output:
        write_json(args.output, payload)
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0
    print("# Axiom Qualification Evidence Ingest\n")
    print(f"- aggregate decision: `{payload['aggregateDecision']}`")
    print(f"- records: `{len(payload['records'])}`")
    for record in payload["records"]:
        warning_suffix = f"; warnings={len(record['warnings'])}" if record["warnings"] else ""
        print(
            f"- `{record['kind']}` `{record['sourceName']}`: "
            f"source={record['sourceResult']}; decision={record['decision']}{warning_suffix}"
        )
    if args.output:
        print(f"- local output: `{args.output.expanduser()}`")
    print("\nBoundary: " + "; ".join(EVIDENCE_BOUNDARIES) + ".")
    return 0


def status_summary(args: argparse.Namespace) -> int:
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
    evidence_path = configured_evidence_path(args.evidence, args.no_evidence)
    if evidence_path:
        evidence = evidence_status_payload(evidence_path)
        print("\n## Qualification Evidence\n")
        print(f"- validation: `{evidence['status']}`")
        print(f"- aggregate decision: `{evidence['aggregateDecision']}`")
        print(f"- records: `{evidence['recordCount']}`")
        print(f"- warnings: `{evidence['warningCount']}`")
        print(f"- critical failures: `{evidence['criticalFailureCount']}`")
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

    checks.extend(validate_command_surface_data(load_command_surface()))
    checks.extend(validate_agent_profiles())
    checks.extend(validate_skill_eval_data(load_skill_eval_cases()))

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
        command_payload("agentic-audit", [sys.executable, str(pathlib.Path(__file__).resolve()), "agentic-audit", "--json"], timeout=60),
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


def validate_agent_profiles(profile_root: pathlib.Path = CODEX_AGENT_PROFILE_ROOT) -> list[Check]:
    checks: list[Check] = []
    paths = sorted(profile_root.glob("*.md"))
    seen_titles: set[str] = set()
    for path in paths:
        text = path.read_text(encoding="utf-8")
        title_match = re.search(r"^#\s+(.+)$", text, flags=re.MULTILINE)
        title = title_match.group(1).strip() if title_match else ""
        if not title:
            checks.append(Check("profile title", "fail", f"{path.name}: missing H1 title"))
        elif title in seen_titles:
            checks.append(Check("duplicate profile title", "fail", title))
        seen_titles.add(title)

        source_match = re.search(r"^Role source:\s+`([^`]+)`\s*$", text, flags=re.MULTILINE)
        if not source_match:
            checks.append(Check("profile role source", "fail", f"{path.name}: missing role source"))
        else:
            source = REPO_ROOT / source_match.group(1)
            expected = ROLE_ROOT / path.name
            if source.resolve() != expected.resolve():
                checks.append(Check("profile role mapping", "fail", f"{path.name}: expected {expected.relative_to(REPO_ROOT)}"))
            elif not source.is_file():
                checks.append(Check("profile role source", "fail", f"{path.name}: source file does not exist"))

        missing_sections = sorted(
            heading for heading in PROFILE_REQUIRED_SECTIONS
            if not re.search(rf"^## {re.escape(heading)}\s*$", text, flags=re.MULTILINE)
        )
        if missing_sections:
            checks.append(Check("profile required sections", "fail", f"{path.name}: missing {', '.join(missing_sections)}"))
        for heading in PROFILE_REQUIRED_SECTIONS - set(missing_sections):
            if not markdown_section(text, heading):
                checks.append(Check("profile section content", "fail", f"{path.name}: {heading} is empty"))
    if not paths:
        checks.append(Check("agent profiles", "fail", "no profile files found"))
    elif not checks:
        checks.append(Check("agent profile contract", "pass", f"{len(paths)} profile(s) checked"))
    return checks


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


def profile_lookup() -> dict[str, tuple[str, pathlib.Path, str, str]]:
    return {slug: (slug, path, title, purpose) for slug, path, title, purpose in load_agent_profiles()}


def build_agent_review_record(topic: str, roles: list[str] | None = None) -> dict[str, Any]:
    topic = topic.strip()
    selected_roles = roles or DEFAULT_REVIEW_ROLES
    profiles = profile_lookup()
    role_entries: list[dict[str, Any]] = []
    for role in selected_roles:
        profile = profiles.get(role)
        if profile:
            _, profile_path, _, purpose = profile
            profile_text = profile_path.read_text(encoding="utf-8")
            source_match = re.search(r"^Role source:\s+`([^`]+)`\s*$", profile_text, flags=re.MULTILINE)
            role_source = source_match.group(1) if source_match else str((ROLE_ROOT / f"{role}.md").relative_to(REPO_ROOT))
            profile_source = str(profile_path.relative_to(REPO_ROOT))
        else:
            purpose = ""
            role_source = str((ROLE_ROOT / f"{role}.md").relative_to(REPO_ROOT))
            profile_source = str((CODEX_AGENT_PROFILE_ROOT / f"{role}.md").relative_to(REPO_ROOT))
        role_entries.append(
            {
                "role": role,
                "profileSource": profile_source,
                "roleSource": role_source,
                "purpose": purpose,
                "findings": [],
                "evidenceNeeded": [],
                "evidenceReferences": [],
                "decision": "draft",
            }
        )
    return {
        "schemaVersion": 1,
        "recordType": "axiom-agent-review",
        "status": "draft",
        "topic": topic,
        "scope": "",
        "forbiddenScope": [
            "no accepted-baseline edits",
            "no private artifacts",
            "no unscoped DSP changes",
            "no publication, merge, candidate, or accepted-baseline promotion without explicit user approval",
        ],
        "roles": role_entries,
        "decision": "draft",
        "evidenceStatus": "not_evidence_until_completed",
        "boundaries": [
            "review records are planning and safety artifacts",
            "empty findings mean the review is incomplete",
            "metrics, external research, and helper output are not listening acceptance",
            "real-JDSP, candidate, publication, merge, and accepted-baseline work still require their normal gates",
        ],
    }


def validate_agent_review_record(data: Any) -> list[Check]:
    checks: list[Check] = []
    if not isinstance(data, dict):
        return [Check("agent review record", "fail", "record must be an object")]
    missing = sorted(REVIEW_RECORD_REQUIRED_FIELDS - set(data))
    if missing:
        checks.append(Check("review required fields", "fail", f"missing {', '.join(missing)}"))
    if data.get("schemaVersion") != 1:
        checks.append(Check("review schema", "fail", "schemaVersion must be 1"))
    if data.get("recordType") != "axiom-agent-review":
        checks.append(Check("review record type", "fail", "recordType must be axiom-agent-review"))
    status = str(data.get("status"))
    if status not in REVIEW_STATUSES:
        checks.append(Check("review status", "fail", f"status must be one of {', '.join(sorted(REVIEW_STATUSES))}"))
    if not isinstance(data.get("topic"), str) or not data.get("topic", "").strip():
        checks.append(Check("review topic", "fail", "topic must be non-empty text"))
    decision = str(data.get("decision"))
    if decision not in REVIEW_DECISIONS:
        checks.append(Check("review decision", "fail", f"decision must be one of {', '.join(sorted(REVIEW_DECISIONS))}"))
    evidence_status = str(data.get("evidenceStatus"))
    if evidence_status not in REVIEW_EVIDENCE_STATUSES:
        checks.append(
            Check(
                "review evidence status",
                "fail",
                f"evidenceStatus must be one of {', '.join(sorted(REVIEW_EVIDENCE_STATUSES))}",
            )
        )
    if not isinstance(data.get("forbiddenScope"), list) or not data.get("forbiddenScope"):
        checks.append(Check("review forbidden scope", "fail", "forbiddenScope must be a non-empty list"))
    if not isinstance(data.get("boundaries"), list) or not data.get("boundaries"):
        checks.append(Check("review boundaries", "fail", "boundaries must be a non-empty list"))

    profiles = profile_lookup()
    roles = data.get("roles")
    if not isinstance(roles, list) or not roles:
        checks.append(Check("review roles", "fail", "roles must be a non-empty array"))
        roles = []
    seen_roles: set[str] = set()
    for entry in roles:
        if not isinstance(entry, dict):
            checks.append(Check("review role entry", "fail", "role entry must be an object"))
            continue
        role = str(entry.get("role", "missing-role"))
        missing_role_fields = sorted(REVIEW_ROLE_REQUIRED_FIELDS - set(entry))
        if missing_role_fields:
            checks.append(Check("review role required fields", "fail", f"{role}: missing {', '.join(missing_role_fields)}"))
        if role in seen_roles:
            checks.append(Check("duplicate review role", "fail", role))
        seen_roles.add(role)
        if role not in profiles:
            checks.append(Check("unknown review role", "fail", role))
        if str(entry.get("decision")) not in REVIEW_DECISIONS:
            checks.append(Check("review role decision", "fail", f"{role}: invalid decision"))
        for field in ("findings", "evidenceNeeded", "evidenceReferences"):
            if not isinstance(entry.get(field), list):
                checks.append(Check(f"review role {field}", "fail", f"{role}: {field} must be an array"))
        for field in ("profileSource", "roleSource", "purpose"):
            if not isinstance(entry.get(field), str):
                checks.append(Check(f"review role {field}", "fail", f"{role}: {field} must be text"))

    if status == "complete":
        if not isinstance(data.get("scope"), str) or not data.get("scope", "").strip():
            checks.append(Check("completed review scope", "fail", "complete review requires non-empty scope"))
        if decision == "draft":
            checks.append(Check("completed review decision", "fail", "complete review decision cannot be draft"))
        if evidence_status != "completed_review_not_authority":
            checks.append(
                Check(
                    "completed review evidence status",
                    "fail",
                    "complete review must use completed_review_not_authority",
                )
            )
        for entry in roles:
            if not isinstance(entry, dict):
                continue
            role = str(entry.get("role", "missing-role"))
            if entry.get("decision") == "draft":
                checks.append(Check("completed role decision", "fail", f"{role}: decision cannot be draft"))
            for field in ("findings", "evidenceReferences"):
                values = entry.get(field)
                if not isinstance(values, list) or not values or not all(isinstance(value, str) and value.strip() for value in values):
                    checks.append(Check(f"completed role {field}", "fail", f"{role}: {field} must contain non-empty text"))
            review_text = "\n".join(
                value
                for field in ("findings", "evidenceNeeded", "evidenceReferences")
                for value in entry.get(field, [])
                if isinstance(value, str)
            )
            if any(pattern.search(review_text) for pattern in PRIVATE_CONTENT_PATTERNS):
                checks.append(Check("completed review private path", "fail", f"{role}: private path content detected"))
    if not checks:
        checks.append(Check("agent review record", "pass", f"{len(roles)} role(s) checked"))
    return checks


def agent_review_markdown(record: dict[str, Any], checks: list[Check]) -> str:
    lines = [
        "# Axiom Multi-Role Review Record",
        "",
        f"- schema: `{record['schemaVersion']}`",
        f"- status: `{record['status']}`",
        f"- topic: {record['topic']}",
        f"- decision: `{record['decision']}`",
        f"- evidence status: `{record['evidenceStatus']}`",
        "",
        "## Validation",
        "",
    ]
    lines.extend(f"- {check.status}: {check.name} - {check.detail}" for check in checks)
    lines.extend(["", "## Scope", "", record["scope"] or "[draft: define the narrow work area before implementation]", "", "## Forbidden Scope", ""])
    lines.extend(f"- {item}" for item in record["forbiddenScope"])
    lines.extend(["", "## Role Findings", ""])
    for entry in record["roles"]:
        lines.extend([
            f"### {entry['role']}",
            "",
            f"- profile: `{entry['profileSource']}`",
            f"- role source: `{entry['roleSource']}`",
            f"- purpose: {entry['purpose'] or '[missing purpose]'}",
            f"- decision: `{entry['decision']}`",
            "",
            "Findings:",
        ])
        if entry["findings"]:
            lines.extend(f"- {item}" for item in entry["findings"])
        else:
            lines.append("- [draft: add concrete finding with file/evidence reference]")
        lines.append("")
        lines.append("Evidence needed:")
        if entry["evidenceNeeded"]:
            lines.extend(f"- {item}" for item in entry["evidenceNeeded"])
        else:
            lines.append("- [draft: add required measurement, docs, or approval]")
        lines.append("")
        lines.append("Evidence references:")
        if entry["evidenceReferences"]:
            lines.extend(f"- {item}" for item in entry["evidenceReferences"])
        else:
            lines.append("- [draft: add repo-safe file, check, or local evidence ID]")
        lines.append("")
    lines.extend(["## Boundaries", ""])
    lines.extend(f"- {item}" for item in record["boundaries"])
    lines.append("")
    return "\n".join(lines)


def agent_review(args: argparse.Namespace) -> int:
    record = build_agent_review_record(args.topic, args.roles)
    checks = validate_agent_review_record(record)
    failed = any(check.status == "fail" for check in checks)
    if args.output:
        args.output.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps({"record": record, "checks": [check.__dict__ for check in checks]}, indent=2, sort_keys=True))
    else:
        print(agent_review_markdown(record, checks).rstrip())
    return 1 if failed else 0


def agent_review_status_payload(path: pathlib.Path) -> dict[str, Any]:
    expanded = path.expanduser()
    boundaries = [
        "completed review records are bounded planning artifacts, not approval",
        "review decisions do not execute JDSP, publication, merge, candidate creation, or baseline promotion",
        "private paths and raw local evidence must not enter review records",
    ]
    if not expanded.is_file():
        return {
            "validation": "fail",
            "lifecycleStatus": "unknown",
            "decision": "unknown",
            "roleCount": 0,
            "completedRoleCount": 0,
            "checks": [Check("agent review exists", "fail", path.name).__dict__],
            "boundaries": boundaries,
        }
    try:
        data = json.loads(expanded.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as exc:
        return {
            "validation": "fail",
            "lifecycleStatus": "unknown",
            "decision": "unknown",
            "roleCount": 0,
            "completedRoleCount": 0,
            "checks": [Check("agent review JSON", "fail", str(exc)).__dict__],
            "boundaries": boundaries,
        }
    checks = validate_agent_review_record(data)
    roles = data.get("roles", []) if isinstance(data, dict) else []
    valid_roles = [entry for entry in roles if isinstance(entry, dict)]
    return {
        "validation": "fail" if any(check.status == "fail" for check in checks) else "pass",
        "lifecycleStatus": data.get("status", "unknown") if isinstance(data, dict) else "unknown",
        "decision": data.get("decision", "unknown") if isinstance(data, dict) else "unknown",
        "topic": data.get("topic") if isinstance(data, dict) else None,
        "roleCount": len(valid_roles),
        "completedRoleCount": sum(1 for entry in valid_roles if entry.get("decision") != "draft"),
        "checks": [check.__dict__ for check in checks],
        "boundaries": boundaries,
    }


def agent_review_status(args: argparse.Namespace) -> int:
    payload = agent_review_status_payload(args.review)
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 1 if payload["validation"] == "fail" else 0
    print("# Axiom Agent Review Status\n")
    print(f"- validation: `{payload['validation']}`")
    print(f"- lifecycle status: `{payload['lifecycleStatus']}`")
    print(f"- decision: `{payload['decision']}`")
    print(f"- roles completed: `{payload['completedRoleCount']}/{payload['roleCount']}`")
    print("\n## Checks\n")
    for check in payload["checks"]:
        print(f"- {check['status']}: {check['name']} - {check['detail']}")
    print("\n## Boundaries\n")
    for boundary in payload["boundaries"]:
        print(f"- {boundary}")
    return 1 if payload["validation"] == "fail" else 0


def normalize_terms(query: str) -> list[str]:
    return [term.lower() for term in re.findall(r"[a-zA-Z0-9][a-zA-Z0-9+.-]*", query) if len(term) > 1]


def score_text(text: str, terms: list[str]) -> int:
    lowered = text.lower()
    return sum(lowered.count(term) for term in terms)


def relative_posix(path: pathlib.Path, root: pathlib.Path) -> str:
    return path.relative_to(root).as_posix()


def git_head(repo: pathlib.Path) -> str:
    result = run_in(repo, ["git", "rev-parse", "HEAD"])
    if result.returncode != 0:
        raise SystemExit(f"could not resolve Airwindows git HEAD: {result.stderr.strip()}")
    return result.stdout.strip()


def airwindows_effect_name(path: pathlib.Path) -> str:
    if path.name in {"what.txt", "Airwindopedia.txt"}:
        return path.stem
    if "plugins" in path.parts:
        plugin_index = path.parts.index("plugins")
        candidate_index = plugin_index + 2
        if candidate_index < len(path.parts) and path.parts[candidate_index] == "src":
            candidate_index += 1
        if candidate_index < len(path.parts):
            return path.parts[candidate_index]
    if path.parent.name:
        return path.parent.name
    return path.stem


def airwindows_tags(name: str, relative_path: str) -> list[str]:
    haystack = f"{name} {relative_path}".lower()
    tags = [
        tag
        for tag, needles in AIRWINDOWS_TAG_RULES
        if any(needle in haystack for needle in needles)
    ]
    return tags or ["uncategorized"]


def discover_airwindows_effects(repo: pathlib.Path) -> list[dict[str, Any]]:
    effects_by_name: dict[str, dict[str, Any]] = {}
    for path in sorted(repo.rglob("*")):
        if not path.is_file():
            continue
        if ".git" in path.parts:
            continue
        if path.suffix.lower() not in {".cpp", ".h", ".txt"}:
            continue
        rel = relative_posix(path, repo)
        if rel.startswith("plugins/WinVST/") and not path.name.endswith("Proc.cpp"):
            continue
        if path.suffix.lower() in {".cpp", ".h"} and "plugins" not in path.parts:
            continue
        name = airwindows_effect_name(path)
        key = name.lower()
        entry = effects_by_name.setdefault(
            key,
            {
                "name": name,
                "tags": set(),
                "sourcePaths": [],
            },
        )
        entry["tags"].update(airwindows_tags(name, rel))
        entry["sourcePaths"].append(rel)

    effects: list[dict[str, Any]] = []
    for entry in effects_by_name.values():
        effects.append(
            {
                "name": entry["name"],
                "tags": sorted(entry["tags"]),
                "sourcePaths": sorted(set(entry["sourcePaths"])),
            }
        )
    return sorted(effects, key=lambda item: item["name"].lower())


def build_airwindows_index(repo: pathlib.Path) -> dict[str, Any]:
    root = repo.expanduser().resolve()
    if not root.exists() or not root.is_dir():
        raise SystemExit(f"Airwindows repo path does not exist or is not a directory: {repo}")
    return {
        "schemaVersion": 2,
        "sourceId": AIRWINDOWS_SOURCE_ID,
        "title": "Airwindows Open Source DSP",
        "repoUrl": AIRWINDOWS_REPO_URL,
        "license": "MIT",
        "pinnedCommit": git_head(root),
        "generatedBy": "axiom_codex.py airwindows-index",
        "boundary": "metadata-only index for clean-room concept extraction; no source code, copied snippets, or local paths",
        "effects": discover_airwindows_effects(root),
    }


def load_airwindows_index(index_path: pathlib.Path | None) -> dict[str, Any] | None:
    if index_path is None:
        return None
    expanded = index_path.expanduser()
    if not expanded.exists():
        return None
    data = json.loads(expanded.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit(f"invalid Airwindows index: {expanded}")
    return data


def resolve_airwindows_index(
    explicit_path: pathlib.Path | None,
    disabled: bool = False,
) -> pathlib.Path | None:
    if disabled:
        return None
    if explicit_path is not None:
        return explicit_path.expanduser()
    return DEFAULT_AIRWINDOWS_INDEX if DEFAULT_AIRWINDOWS_INDEX.exists() else None


def airwindows_effect_public_fields(effect: dict[str, Any]) -> dict[str, Any]:
    source_paths = effect.get("sourcePaths")
    if not isinstance(source_paths, list):
        relative_path = effect.get("relativePath", "")
        source_paths = [relative_path] if isinstance(relative_path, str) and relative_path else []
    return {
        "name": effect.get("name", ""),
        "sourcePaths": source_paths,
        "tags": effect.get("tags", []),
    }


def airwindows_query_matches(index: dict[str, Any], terms: list[str], limit: int) -> list[tuple[int, dict[str, Any]]]:
    matches: list[tuple[int, dict[str, Any]]] = []
    for effect in index.get("effects", []):
        if not isinstance(effect, dict):
            continue
        public_fields = airwindows_effect_public_fields(effect)
        score_fields = {
            "name": public_fields["name"],
            "tags": public_fields["tags"],
        }
        score = score_text(json.dumps(score_fields, sort_keys=True), terms)
        if score:
            matches.append((score, public_fields))
    return sorted(matches, key=lambda item: (item[0], str(item[1].get("name", ""))), reverse=True)[:limit]


def audit_airwindows_index(index_path: pathlib.Path, repo: pathlib.Path | None = None) -> list[Check]:
    expanded = index_path.expanduser()
    if not expanded.exists():
        return [Check("Airwindows index exists", "fail", str(expanded))]
    try:
        data = json.loads(expanded.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [Check("Airwindows index JSON", "fail", str(exc))]
    if not isinstance(data, dict):
        return [Check("Airwindows index shape", "fail", "top-level value must be an object")]

    checks: list[Check] = []
    schema_version = data.get("schemaVersion")
    checks.append(Check("Airwindows schema version", "pass" if schema_version == 2 else "fail", str(schema_version)))
    pinned = data.get("pinnedCommit")
    pinned_valid = isinstance(pinned, str) and re.fullmatch(r"[0-9a-f]{40}", pinned) is not None
    checks.append(Check("Airwindows pinned commit", "pass" if pinned_valid else "fail", str(pinned)))
    checks.append(
        Check(
            "Airwindows source ID",
            "pass" if data.get("sourceId") == AIRWINDOWS_SOURCE_ID else "fail",
            str(data.get("sourceId")),
        )
    )
    checks.append(
        Check(
            "Airwindows repository URL",
            "pass" if data.get("repoUrl") == AIRWINDOWS_REPO_URL else "fail",
            str(data.get("repoUrl")),
        )
    )
    checks.append(Check("Airwindows license", "pass" if data.get("license") == "MIT" else "fail", str(data.get("license"))))
    forbidden_root = sorted(set(data) - AIRWINDOWS_INDEX_FIELDS)
    if forbidden_root:
        checks.append(Check("Airwindows top-level fields", "fail", ", ".join(forbidden_root)))

    effects = data.get("effects")
    if not isinstance(effects, list):
        return checks + [Check("Airwindows effects", "fail", "`effects` must be an array")]
    names: set[str] = set()
    for effect in effects:
        if not isinstance(effect, dict):
            checks.append(Check("Airwindows effect entry", "fail", "effect must be an object"))
            continue
        name = effect.get("name")
        if not isinstance(name, str) or not name.strip():
            checks.append(Check("Airwindows effect name", "fail", "missing effect name"))
            continue
        lowered = name.lower()
        if lowered in names:
            checks.append(Check("Airwindows duplicate effect", "fail", name))
        names.add(lowered)
        tags = effect.get("tags")
        paths = effect.get("sourcePaths")
        if not isinstance(tags, list) or not all(isinstance(tag, str) and tag for tag in tags):
            checks.append(Check("Airwindows effect tags", "fail", name))
        if not isinstance(paths, list) or not paths or not all(isinstance(path, str) and path for path in paths):
            checks.append(Check("Airwindows source paths", "fail", name))
            continue
        for path in paths:
            pure = pathlib.PurePosixPath(path)
            if pure.is_absolute() or ".." in pure.parts:
                checks.append(Check("Airwindows relative path", "fail", f"{name}: {path}"))
                break
        forbidden = set(effect) - {"name", "tags", "sourcePaths"}
        if forbidden:
            checks.append(Check("Airwindows metadata fields", "fail", f"{name}: {', '.join(sorted(forbidden))}"))

    if repo is not None:
        root = repo.expanduser().resolve()
        if not root.exists():
            checks.append(Check("Airwindows checkout", "fail", str(root)))
        else:
            current = git_head(root)
            checks.append(
                Check(
                    "Airwindows checkout drift",
                    "pass" if current == pinned else "warn",
                    f"index={pinned} checkout={current}",
                )
            )
    if not any(check.status == "fail" for check in checks):
        checks.append(Check("Airwindows index audit", "pass", f"{len(effects)} canonical effect(s) checked"))
    return checks


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
    airwindows_index_path = resolve_airwindows_index(args.airwindows_index, args.no_airwindows_index)
    airwindows_index = load_airwindows_index(airwindows_index_path)
    airwindows_matches = airwindows_query_matches(airwindows_index, terms, args.limit) if airwindows_index else []

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
    print("\n## Airwindows Local Index\n")
    if args.no_airwindows_index:
        print("- Airwindows index disabled")
    elif airwindows_index_path is None:
        print("- standard Airwindows index not found")
    elif not airwindows_index_path.exists():
        print("- Airwindows index not found")
    elif airwindows_matches:
        for score, effect in airwindows_matches:
            tags = ", ".join(effect.get("tags", [])) if isinstance(effect.get("tags"), list) else ""
            paths = effect.get("sourcePaths", [])
            representative = paths[0] if isinstance(paths, list) and paths else ""
            path_count = len(paths) if isinstance(paths, list) else 0
            print(f"- score {score}: {effect.get('name', 'unnamed')} :: {tags} :: {representative} (+{max(0, path_count - 1)} paths)")
    else:
        print("- no Airwindows index matches")
    print("\nBoundary: Knowledge can inform tests; it is not proof of Axiom behavior.")
    return 0


def airwindows_index(args: argparse.Namespace) -> int:
    payload = build_airwindows_index(args.repo)
    write_json(args.output, payload)
    print("# Axiom Airwindows Index\n")
    print(f"- source: {payload['sourceId']}")
    print(f"- pinned commit: {payload['pinnedCommit']}")
    print(f"- effects indexed: {len(payload['effects'])}")
    print(f"- output: {args.output.expanduser()}")
    print("\nBoundary: metadata-only local index. It does not vendor Airwindows code or approve DSP reuse.")
    return 0


def airwindows_audit(args: argparse.Namespace) -> int:
    checks = audit_airwindows_index(args.index, args.repo)
    failed = any(check.status == "fail" for check in checks)
    if args.json:
        print(json.dumps([check.__dict__ for check in checks], indent=2, sort_keys=True))
        return 1 if failed else 0
    print("# Axiom Airwindows Index Audit\n")
    for check in checks:
        print(f"- {check.status}: {check.name} - {check.detail}")
    print("\nBoundary: this validates local metadata and commit drift. It does not approve DSP reuse or candidate creation.")
    return 1 if failed else 0


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


def validate_skill_eval_data(
    data: dict[str, Any],
    known_commands: set[str] | None = None,
) -> list[Check]:
    checks: list[Check] = []
    cases = data.get("cases", [])
    if data.get("schemaVersion") != 1:
        checks.append(Check("skill eval schema", "fail", "schemaVersion must be 1"))
    if not isinstance(cases, list):
        return [Check("skill eval cases", "fail", "`cases` must be an array")]
    known_commands = known_commands if known_commands is not None else set(command_surface_lookup())
    seen: set[str] = set()
    for case in cases:
        if not isinstance(case, dict):
            checks.append(Check("skill eval entry", "fail", "case entry must be an object"))
            continue
        case_id = str(case.get("id", "missing-id"))
        missing = sorted(SKILL_EVAL_REQUIRED_FIELDS - set(case))
        if missing:
            checks.append(Check("skill eval required fields", "fail", f"{case_id}: missing {', '.join(missing)}"))
        if case_id in seen:
            checks.append(Check("duplicate skill eval id", "fail", case_id))
        seen.add(case_id)
        if not re.fullmatch(r"[a-z][a-z0-9-]*", case_id):
            checks.append(Check("skill eval id format", "fail", case_id))
        if not isinstance(case.get("prompt"), str) or not case.get("prompt", "").strip():
            checks.append(Check("skill eval prompt", "fail", f"{case_id}: prompt must be non-empty text"))
        expected = case.get("expected")
        if not isinstance(expected, dict):
            checks.append(Check("skill eval expected", "fail", f"{case_id}: expected must be an object"))
            continue
        helper_commands = expected.get("helperCommands")
        required_terms = expected.get("requiredTerms")
        if not isinstance(helper_commands, list) or not helper_commands:
            checks.append(Check("skill eval helper commands", "fail", f"{case_id}: helperCommands must be non-empty"))
        else:
            unknown = sorted({str(name) for name in helper_commands} - known_commands)
            if unknown:
                checks.append(Check("skill eval command mapping", "fail", f"{case_id}: unknown {', '.join(unknown)}"))
        if not isinstance(required_terms, list) or not required_terms or not all(
            isinstance(term, str) and term.strip() for term in required_terms
        ):
            checks.append(Check("skill eval required terms", "fail", f"{case_id}: requiredTerms must be non-empty strings"))
    if not checks:
        checks.append(Check("skill eval contract", "pass", f"{len(cases)} case(s) checked"))
    return checks


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
    checks = validate_skill_eval_data(data, set(commands))

    for case in data["cases"]:
        if not isinstance(case, dict) or not isinstance(case.get("expected"), dict):
            continue
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


def agentic_audit(args: argparse.Namespace) -> int:
    checks = [
        *validate_command_surface_data(load_command_surface()),
        *validate_agent_profiles(),
        *validate_skill_eval_data(load_skill_eval_cases()),
    ]
    failed = any(check.status == "fail" for check in checks)
    if args.json:
        print(json.dumps([check.__dict__ for check in checks], indent=2, sort_keys=True))
        return 1 if failed else 0
    print("# Axiom Agentic Contract Audit\n")
    for check in checks:
        print(f"- {check.status}: {check.name} - {check.detail}")
    print("\nBoundary: this validates Agentic Layer contracts and mappings. It does not run JDSP or grant approval.")
    return 1 if failed else 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    status = sub.add_parser("status-summary")
    status.add_argument("--evidence", type=pathlib.Path)
    status.add_argument("--no-evidence", action="store_true")
    status.set_defaults(func=status_summary)
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

    audit = sub.add_parser("agentic-audit")
    audit.add_argument("--json", action="store_true")
    audit.set_defaults(func=agentic_audit)

    tasks = sub.add_parser("task-state")
    tasks.add_argument("--json", action="store_true")
    tasks.set_defaults(func=task_state)

    next_parser = sub.add_parser("next-action")
    next_parser.add_argument("--json", action="store_true")
    next_parser.add_argument("--evidence", type=pathlib.Path)
    next_parser.add_argument("--no-evidence", action="store_true")
    next_parser.add_argument("--include-maintenance", action="store_true")
    next_parser.add_argument("--review", type=pathlib.Path)
    next_parser.set_defaults(func=next_action)

    evidence = sub.add_parser("evidence-ingest")
    evidence.add_argument("paths", nargs="+", type=pathlib.Path)
    evidence.add_argument("--output", type=pathlib.Path)
    evidence.add_argument("--json", action="store_true")
    evidence.add_argument("--show-private-paths", action="store_true")
    evidence.set_defaults(func=evidence_ingest)

    evidence_check = sub.add_parser("evidence-status")
    evidence_check.add_argument("bundle", type=pathlib.Path)
    evidence_check.add_argument("--json", action="store_true")
    evidence_check.set_defaults(func=evidence_status)

    evidence_list = sub.add_parser("evidence-catalog")
    evidence_list.add_argument("directory", type=pathlib.Path)
    evidence_list.add_argument("--set-default", action="store_true")
    evidence_list.add_argument("--json", action="store_true")
    evidence_list.set_defaults(func=evidence_catalog)

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
    review.add_argument("--json", action="store_true")
    review.add_argument("--output", type=pathlib.Path)
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

    review_status = sub.add_parser("agent-review-status")
    review_status.add_argument("review", type=pathlib.Path)
    review_status.add_argument("--json", action="store_true")
    review_status.set_defaults(func=agent_review_status)

    airwindows = sub.add_parser("airwindows-index")
    airwindows.add_argument("--repo", type=pathlib.Path, required=True)
    airwindows.add_argument("--output", type=pathlib.Path, default=DEFAULT_AIRWINDOWS_INDEX)
    airwindows.set_defaults(func=airwindows_index)

    airwindows_check = sub.add_parser("airwindows-audit")
    airwindows_check.add_argument("--index", type=pathlib.Path, default=DEFAULT_AIRWINDOWS_INDEX)
    airwindows_check.add_argument("--repo", type=pathlib.Path)
    airwindows_check.add_argument("--json", action="store_true")
    airwindows_check.set_defaults(func=airwindows_audit)

    knowledge = sub.add_parser("knowledge-query")
    knowledge.add_argument("query")
    knowledge.add_argument("--index", type=pathlib.Path, default=DEFAULT_LOCAL_INDEX)
    knowledge.add_argument("--airwindows-index", type=pathlib.Path)
    knowledge.add_argument("--no-airwindows-index", action="store_true")
    knowledge.add_argument("--limit", type=int, default=8)
    knowledge.add_argument("--show-private-paths", action="store_true")
    knowledge.set_defaults(func=knowledge_query)

    sources = sub.add_parser("knowledge-sources")
    sources.add_argument("--index", type=pathlib.Path, default=DEFAULT_LOCAL_INDEX)
    sources.add_argument("--json", action="store_true")
    sources.add_argument("--show-private-paths", action="store_true")
    sources.set_defaults(func=knowledge_sources)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
