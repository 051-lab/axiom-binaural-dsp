#!/usr/bin/env python3
"""Generate the Axiom session work-log PDF copies.

The source is a small Markdown file where each `## Run ...` section becomes a
new PDF page. The generator intentionally uses only the Python standard
library so the session log can be refreshed without installing a document
toolchain.
"""

from __future__ import annotations

import argparse
import pathlib
import re
import textwrap
from dataclasses import dataclass


REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = REPO_ROOT / "docs" / "session-work-log.md"
DEFAULT_REPO_PDF = REPO_ROOT / "docs" / "session-work-log.pdf"
DEFAULT_WINDOWS_PDF = pathlib.Path("/mnt/c/Users/soloa/Documents/Axiom-DSP-Session-Work-Log.pdf")

PAGE_WIDTH = 612
PAGE_HEIGHT = 792
MARGIN_X = 54
TOP_Y = 742
BOTTOM_Y = 54
BODY_SIZE = 9.5
TITLE_SIZE = 15
HEADING_SIZE = 11
LINE_HEIGHT = 12
MAX_CHARS = 92


@dataclass
class RunEntry:
    title: str
    lines: list[str]


def parse_runs(source: pathlib.Path) -> list[RunEntry]:
    text = source.read_text(encoding="utf-8")
    runs: list[RunEntry] = []
    current_title: str | None = None
    current_lines: list[str] = []
    for raw_line in text.splitlines():
        if raw_line.startswith("## Run "):
            if current_title is not None:
                runs.append(RunEntry(current_title, current_lines))
            current_title = raw_line.removeprefix("## ").strip()
            current_lines = []
            continue
        if current_title is not None:
            current_lines.append(raw_line.rstrip())
    if current_title is not None:
        runs.append(RunEntry(current_title, current_lines))
    if not runs:
        raise SystemExit(f"No `## Run ...` sections found in {source}")
    return runs


def clean_markdown(line: str) -> tuple[str, str, int]:
    stripped = line.strip()
    if not stripped:
        return "", "body", 0
    stripped = stripped.replace("`", "")
    if stripped.startswith("### "):
        return stripped.removeprefix("### ").strip(), "heading", 0
    if stripped.startswith("- "):
        return "- " + stripped.removeprefix("- ").strip(), "body", 2
    if re.match(r"^\d+\. ", stripped):
        return stripped, "body", 2
    return stripped, "body", 0


def wrap_line(text: str, indent: int) -> list[str]:
    if not text:
        return [""]
    prefix = " " * indent
    width = max(30, MAX_CHARS - indent)
    return textwrap.wrap(
        text,
        width=width,
        initial_indent=prefix,
        subsequent_indent=prefix + ("  " if text.startswith("- ") else ""),
        break_long_words=False,
        break_on_hyphens=False,
    ) or [prefix]


def pdf_escape(value: str) -> str:
    ascii_value = value.encode("latin-1", "replace").decode("latin-1")
    return ascii_value.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def text_command(text: str, x: float, y: float, font: str, size: float) -> str:
    return f"BT /{font} {size:g} Tf 1 0 0 1 {x:g} {y:g} Tm ({pdf_escape(text)}) Tj ET\n"


def page_stream(entry: RunEntry, index: int, total: int) -> str:
    stream = ""
    y = TOP_Y
    stream += text_command(entry.title, MARGIN_X, y, "F2", TITLE_SIZE)
    y -= 24
    for raw_line in entry.lines:
        text, kind, indent = clean_markdown(raw_line)
        if not text:
            y -= LINE_HEIGHT * 0.6
            continue
        font = "F2" if kind == "heading" else "F1"
        size = HEADING_SIZE if kind == "heading" else BODY_SIZE
        if kind == "heading":
            y -= 4
        for wrapped in wrap_line(text, indent):
            if y < BOTTOM_Y + 24:
                stream += text_command("[Entry truncated to preserve one run per PDF page.]", MARGIN_X, y, "F1", BODY_SIZE)
                footer = f"Axiom-DSP Session Work Log - page {index} of {total}"
                stream += text_command(footer, MARGIN_X, 32, "F1", 8)
                return stream
            stream += text_command(wrapped, MARGIN_X, y, font, size)
            y -= LINE_HEIGHT
    footer = f"Axiom-DSP Session Work Log - page {index} of {total}"
    stream += text_command(footer, MARGIN_X, 32, "F1", 8)
    return stream


def make_pdf(entries: list[RunEntry]) -> bytes:
    objects: list[bytes] = []

    def add(obj: str) -> int:
        objects.append(obj.encode("latin-1"))
        return len(objects)

    catalog_id = add("PLACEHOLDER")
    pages_id = add("PLACEHOLDER")
    font_regular_id = add("<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
    font_bold_id = add("<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>")
    page_ids: list[int] = []

    for idx, entry in enumerate(entries, start=1):
        stream = page_stream(entry, idx, len(entries)).encode("latin-1")
        content_id = add(f"<< /Length {len(stream)} >>\nstream\n".encode("latin-1").decode("latin-1") + stream.decode("latin-1") + "\nendstream")
        page_id = add(
            f"<< /Type /Page /Parent {pages_id} 0 R "
            f"/MediaBox [0 0 {PAGE_WIDTH} {PAGE_HEIGHT}] "
            f"/Resources << /Font << /F1 {font_regular_id} 0 R /F2 {font_bold_id} 0 R >> >> "
            f"/Contents {content_id} 0 R >>"
        )
        page_ids.append(page_id)

    kids = " ".join(f"{page_id} 0 R" for page_id in page_ids)
    objects[catalog_id - 1] = f"<< /Type /Catalog /Pages {pages_id} 0 R >>".encode("latin-1")
    objects[pages_id - 1] = f"<< /Type /Pages /Kids [{kids}] /Count {len(page_ids)} >>".encode("latin-1")

    output = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets = [0]
    for obj_id, obj in enumerate(objects, start=1):
        offsets.append(len(output))
        output.extend(f"{obj_id} 0 obj\n".encode("latin-1"))
        output.extend(obj)
        output.extend(b"\nendobj\n")
    xref_offset = len(output)
    output.extend(f"xref\n0 {len(objects) + 1}\n".encode("latin-1"))
    output.extend(b"0000000000 65535 f\n")
    for offset in offsets[1:]:
        output.extend(f"{offset:010d} 00000 n\n".encode("latin-1"))
    output.extend(
        (
            "trailer\n"
            f"<< /Size {len(objects) + 1} /Root {catalog_id} 0 R >>\n"
            "startxref\n"
            f"{xref_offset}\n"
            "%%EOF\n"
        ).encode("latin-1")
    )
    return bytes(output)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=pathlib.Path, default=DEFAULT_SOURCE)
    parser.add_argument("--repo-pdf", type=pathlib.Path, default=DEFAULT_REPO_PDF)
    parser.add_argument("--windows-pdf", type=pathlib.Path, default=DEFAULT_WINDOWS_PDF)
    args = parser.parse_args()

    entries = parse_runs(args.source)
    pdf = make_pdf(entries)
    for destination in [args.repo_pdf, args.windows_pdf]:
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(pdf)
        print(destination)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
