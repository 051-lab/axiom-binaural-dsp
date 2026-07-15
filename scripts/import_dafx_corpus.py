#!/usr/bin/env python3
"""Download and index the complete open-access DAFx proceedings corpus."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import tempfile
import urllib.request
import zipfile
from pathlib import Path, PurePosixPath


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "docs/knowledge/dafx-proceedings.json"
DEFAULT_PDF_DIR = ROOT / "docs/knowledge/pdfs"
DEFAULT_INDEX = ROOT / "docs/knowledge/source-index.local.json"


def slug(text: str) -> str:
    value = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return value or "paper"


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def safe_pdf_members(archive: zipfile.ZipFile):
    for member in archive.infolist():
        path = PurePosixPath(member.filename)
        if member.is_dir() or path.suffix.lower() != ".pdf":
            continue
        if path.is_absolute() or ".." in path.parts:
            raise ValueError(f"unsafe archive member: {member.filename}")
        yield member


def download(url: str, destination: Path) -> None:
    request = urllib.request.Request(url, headers={"User-Agent": "Axiom-DAFx-Knowledge-Importer/1.0"})
    with urllib.request.urlopen(request, timeout=120) as response, destination.open("wb") as out:
        shutil.copyfileobj(response, out)


def source_record(year: int, output: Path, upstream_name: str, archive_url: str) -> dict:
    relative = output.relative_to(ROOT / "docs/knowledge")
    return {
        "id": output.stem,
        "title": Path(upstream_name).stem.replace("_", " ").replace("-", " "),
        "authors": [],
        "year": year,
        "type": "paper",
        "topics": ["digital audio effects", "DAFx", "unreviewed for Axiom relevance"],
        "localPath": relative.as_posix(),
        "publicUrl": archive_url,
        "licenseNotes": "Open-access DAFx conference paper. Keep the local PDF out of git; cite and summarize in original wording.",
        "axiomUse": "Research candidate only. Review before using it to justify an Axiom design, test, or DSP change.",
        "status": "unread",
    }


def output_path(pdf_dir: Path, year: int, upstream_name: str) -> Path:
    """Match the established local DAFx filename and source-ID convention."""
    return pdf_dir / f"dafx-{year}-{slug(Path(upstream_name).stem)}.pdf"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--pdf-dir", type=Path, default=DEFAULT_PDF_DIR)
    parser.add_argument("--index", type=Path, default=DEFAULT_INDEX)
    parser.add_argument("--year", type=int, action="append", help="Import only this year; repeatable.")
    parser.add_argument("--force", action="store_true", help="Replace existing PDFs.")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    manifest = load_json(args.manifest)
    selected = set(args.year or [])
    proceedings = [p for p in manifest["proceedings"] if not selected or p["year"] in selected]
    if selected - {p["year"] for p in proceedings}:
        parser.error("requested year is not present in the manifest")

    existing = {"schemaVersion": 1, "sources": []}
    if args.index.exists():
        existing = load_json(args.index)
    records = {record["id"]: record for record in existing.get("sources", [])}

    args.pdf_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="axiom-dafx-") as temp:
        temp_dir = Path(temp)
        for proceeding in proceedings:
            year = int(proceeding["year"])
            url = proceeding["url"]
            archive_path = temp_dir / f"DAFx-{year}.zip"
            print(f"[{year}] {url}")
            if args.dry_run:
                continue
            download(url, archive_path)
            if not zipfile.is_zipfile(archive_path):
                raise ValueError(f"download is not a ZIP archive: {url}")
            with zipfile.ZipFile(archive_path) as archive:
                members = list(safe_pdf_members(archive))
                for member in members:
                    output = output_path(args.pdf_dir, year, member.filename)
                    if args.force or not output.exists():
                        with archive.open(member) as source, output.open("wb") as target:
                            shutil.copyfileobj(source, target)
                    record = source_record(year, output, member.filename, url)
                    record["id"] = output.stem
                    # Keep richer user-local provenance when this source was
                    # already indexed by an earlier compatible import.
                    records.setdefault(record["id"], record)
            print(f"[{year}] indexed {len(members)} PDFs")

    if not args.dry_run:
        result = {"schemaVersion": 1, "sources": sorted(records.values(), key=lambda item: (str(item.get("year")), item["id"]))}
        args.index.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"index: {args.index}")
        print(f"papers: {sum(1 for r in result['sources'] if r['id'].startswith('dafx-'))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
