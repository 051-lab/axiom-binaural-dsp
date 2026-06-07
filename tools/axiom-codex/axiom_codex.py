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
CODEX_AGENT_PROFILE_ROOT = CODEX_ROOT / "agent_profiles"
SKILL_EVAL_CASES = CODEX_ROOT / "skill_eval_cases.json"
SKILL_SOURCE = REPO_ROOT / "tools" / "codex-skills" / "axiom-engineering"
INSTALLED_SKILL = pathlib.Path.home() / ".codex" / "skills" / "axiom-engineering"
DEFAULT_SUB_GAIN_RUN = "20260603T004349-post-acceptance-v4-1-4-1-0d309b"
DEFAULT_SUB_GAIN_LABEL_REGEX = "electronic|hip hop|bass|flawed"

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


@dataclass
class Check:
    name: str
    status: str
    detail: str


def run(command: list[str], timeout: int = 30) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=REPO_ROOT,
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


def load_command_surface() -> dict[str, Any]:
    data = load_json(COMMAND_SURFACE)
    if not isinstance(data, dict) or not isinstance(data.get("commands"), list):
        raise SystemExit(f"invalid command surface: {COMMAND_SURFACE}")
    return data


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


def pi_handoff_command(args: argparse.Namespace) -> list[str]:
    command = [
        "node",
        "tools/axiom-team/bin/axiom-team.mjs",
        "map-sub-gain",
        args.run_id,
    ]
    for slider_db in (args.slider_db or [10, 12]):
        command.extend(["--slider-db", str(slider_db)])
    if args.label_regex:
        command.extend(["--label-regex", args.label_regex])
    if args.repetitions is not None:
        command.extend(["--repetitions", str(args.repetitions)])
    return command


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
    print("- Targeted Sub Harmonics map for +10 dB and +12 dB dense/flawed material.")
    print("- Updated investigation gate or local evidence summary from the Pi harness.")
    print("- No candidate creation unless the evidence supports a scoped hypothesis and listening target.\n")
    print("Boundary: Codex generated this handoff; Pi/harness owns execution.")
    return 0


def path_parts(path: str) -> set[str]:
    return {part.lower() for part in pathlib.PurePosixPath(path.replace("\\", "/")).parts}


def is_docs_safe_schema(path: str) -> bool:
    lowered = path.lower().replace("\\", "/")
    return lowered.endswith("source-index.schema.json") or lowered.startswith("docs/knowledge/templates/")


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

    surface = sub.add_parser("command-surface")
    surface.add_argument("--json", action="store_true")
    surface.set_defaults(func=command_surface)

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

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
