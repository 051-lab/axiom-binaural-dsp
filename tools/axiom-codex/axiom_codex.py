#!/usr/bin/env python3
"""Safe Codex-side helper commands for Axiom-DSP orchestration."""

from __future__ import annotations

import argparse
import json
import pathlib
import re
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

DEFAULT_REVIEW_ROLES = [
    "dsp-architect",
    "eel-engineer",
    "measurement-engineer",
    "safety-auditor",
    "release-steward",
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


def git_status() -> str:
    result = run(["git", "status", "-sb"])
    return result.stdout.strip() or result.stderr.strip()


def git_diff_name_only(*paths: str) -> list[str]:
    result = run(["git", "diff", "--name-only", "--", *paths])
    return [line for line in result.stdout.splitlines() if line.strip()]


def section(text: str, heading: str) -> str:
    pattern = rf"^## {re.escape(heading)}\n(.*?)(?=^## |\Z)"
    match = re.search(pattern, text, flags=re.MULTILINE | re.DOTALL)
    return match.group(1).strip() if match else ""


def command_status(result: subprocess.CompletedProcess[str]) -> str:
    return "pass" if result.returncode == 0 else "fail"


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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("status-summary").set_defaults(func=status_summary)
    sub.add_parser("ready-check").set_defaults(func=ready_check)

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
