#!/usr/bin/env python3
"""Install repo-tracked Axiom Codex skills into the local Codex skill dir."""

from __future__ import annotations

import argparse
import filecmp
import pathlib
import shutil
import sys


REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = REPO_ROOT / "tools" / "codex-skills" / "axiom-engineering"
DEFAULT_DESTINATION = pathlib.Path.home() / ".codex" / "skills" / "axiom-engineering"
DEFAULT_SKILL_ROOT = REPO_ROOT / "tools" / "codex-skills"
DEFAULT_DESTINATION_ROOT = pathlib.Path.home() / ".codex" / "skills"
AXIOM_SKILL_NAMES = [
    "axiom-engineering",
    "axiom-coordinator",
    "axiom-safety-auditor",
    "axiom-tooling-engineer",
    "axiom-signal-researcher",
    "axiom-dsp-architect",
    "axiom-eel-engineer",
    "axiom-measurement-engineer",
    "axiom-qualification-lead",
    "axiom-release-steward",
    "axiom-implementation-lead",
]


def iter_files(root: pathlib.Path) -> list[pathlib.Path]:
    return sorted(path for path in root.rglob("*") if path.is_file())


def relative_file_list(root: pathlib.Path) -> list[pathlib.Path]:
    return [path.relative_to(root) for path in iter_files(root)]


def trees_match(source: pathlib.Path, destination: pathlib.Path) -> bool:
    if not destination.exists():
        return False
    source_files = relative_file_list(source)
    dest_files = relative_file_list(destination)
    if source_files != dest_files:
        return False
    return all(filecmp.cmp(source / rel, destination / rel, shallow=False) for rel in source_files)


def install(source: pathlib.Path, destination: pathlib.Path, force: bool) -> str:
    if not source.exists():
        raise SystemExit(f"source skill does not exist: {source}")
    if destination.exists():
        if trees_match(source, destination):
            return f"Already installed and up to date: {destination}"
        if not force:
            raise SystemExit(
                f"destination exists and differs: {destination}\n"
                "Use --force with --install to replace the local skill copy."
            )
        shutil.rmtree(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, destination)
    return f"Installed Axiom Codex skill: {destination}"


def dry_run(source: pathlib.Path, destination: pathlib.Path) -> str:
    lines = [
        "Axiom Codex skill install dry run",
        f"source: {source}",
        f"destination: {destination}",
        f"destination exists: {destination.exists()}",
        "",
        "files:",
    ]
    for rel in relative_file_list(source):
        lines.append(f"- {rel}")
    return "\n".join(lines)


def skill_pairs(skill_root: pathlib.Path, destination_root: pathlib.Path) -> list[tuple[pathlib.Path, pathlib.Path]]:
    return [
        (skill_root / name, destination_root / name)
        for name in AXIOM_SKILL_NAMES
    ]


def dry_run_many(pairs: list[tuple[pathlib.Path, pathlib.Path]]) -> str:
    lines = ["Axiom skills install dry run", ""]
    for source, destination in pairs:
        lines.extend(
            [
                f"skill: {source.name}",
                f"source: {source}",
                f"destination: {destination}",
                f"source exists: {source.exists()}",
                f"destination exists: {destination.exists()}",
                "files:",
            ]
        )
        if source.exists():
            lines.extend(f"- {source.name}/{rel}" for rel in relative_file_list(source))
        lines.append("")
    return "\n".join(lines).rstrip()


def install_many(pairs: list[tuple[pathlib.Path, pathlib.Path]], force: bool) -> str:
    messages = []
    for source, destination in pairs:
        messages.append(install(source, destination, force))
    return "\n".join(messages)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=pathlib.Path, default=DEFAULT_SOURCE)
    parser.add_argument("--destination", type=pathlib.Path, default=DEFAULT_DESTINATION)
    parser.add_argument("--all-axiom-skills", action="store_true", help="Install the umbrella skill plus all Axiom specialist skills.")
    parser.add_argument("--skill-root", type=pathlib.Path, default=DEFAULT_SKILL_ROOT)
    parser.add_argument("--destination-root", type=pathlib.Path, default=DEFAULT_DESTINATION_ROOT)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--dry-run", action="store_true")
    action.add_argument("--install", action="store_true")
    parser.add_argument("--force", action="store_true", help="Replace an existing differing destination during --install.")
    args = parser.parse_args()

    if args.all_axiom_skills:
        pairs = [
            (source.resolve(), destination.expanduser().resolve())
            for source, destination in skill_pairs(args.skill_root.resolve(), args.destination_root.expanduser().resolve())
        ]
        if args.dry_run:
            print(dry_run_many(pairs))
        else:
            print(install_many(pairs, args.force))
        print("\nRestart Codex to pick up newly installed or updated Axiom skills.")
        return 0

    source = args.source.resolve()
    destination = args.destination.expanduser().resolve()
    if args.dry_run:
        print(dry_run(source, destination))
    else:
        print(install(source, destination, args.force))
        print("Restart Codex to pick up newly installed or updated Axiom skills.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
