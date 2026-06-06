#!/usr/bin/env python3
"""Install the repo-tracked Axiom Codex skill into the local Codex skill dir."""

from __future__ import annotations

import argparse
import filecmp
import pathlib
import shutil
import sys


REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = REPO_ROOT / "tools" / "codex-skills" / "axiom-engineering"
DEFAULT_DESTINATION = pathlib.Path.home() / ".codex" / "skills" / "axiom-engineering"


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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=pathlib.Path, default=DEFAULT_SOURCE)
    parser.add_argument("--destination", type=pathlib.Path, default=DEFAULT_DESTINATION)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--dry-run", action="store_true")
    action.add_argument("--install", action="store_true")
    parser.add_argument("--force", action="store_true", help="Replace an existing differing destination during --install.")
    args = parser.parse_args()

    source = args.source.resolve()
    destination = args.destination.expanduser().resolve()
    if args.dry_run:
        print(dry_run(source, destination))
    else:
        print(install(source, destination, args.force))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
