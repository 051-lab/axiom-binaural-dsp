#!/usr/bin/env python3
"""Generate the Axiom Agentic Engineering Blueprint PDF copies."""

from __future__ import annotations

import argparse
import pathlib
import re
import textwrap


REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = REPO_ROOT / "docs" / "axiom-agentic-engineering-blueprint.md"
DEFAULT_REPO_PDF = REPO_ROOT / "docs" / "axiom-agentic-engineering-blueprint.pdf"
DEFAULT_WINDOWS_PDF = pathlib.Path("/mnt/c/Users/soloa/Documents/Axiom-DSP-Agentic-Engineering-Blueprint.pdf")

PAGE_WIDTH = 612
PAGE_HEIGHT = 792
MARGIN_X = 54
TOP_Y = 742
BOTTOM_Y = 54
BODY_SIZE = 9.5
TITLE_SIZE = 17
HEADING_SIZE = 12
SUBHEADING_SIZE = 10.5
LINE_HEIGHT = 12
MAX_CHARS = 91


def pdf_escape(value: str) -> str:
    ascii_value = value.encode("latin-1", "replace").decode("latin-1")
    return ascii_value.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def text_command(text: str, x: float, y: float, font: str, size: float) -> str:
    return f"BT /{font} {size:g} Tf 1 0 0 1 {x:g} {y:g} Tm ({pdf_escape(text)}) Tj ET\n"


def clean_markdown(line: str) -> tuple[str, str, int]:
    stripped = line.strip()
    if not stripped:
        return "", "body", 0
    stripped = stripped.replace("`", "")
    if stripped.startswith("# "):
        return stripped.removeprefix("# ").strip(), "title", 0
    if stripped.startswith("## "):
        return stripped.removeprefix("## ").strip(), "heading", 0
    if stripped.startswith("### "):
        return stripped.removeprefix("### ").strip(), "subheading", 0
    if stripped.startswith("- "):
        return "- " + stripped.removeprefix("- ").strip(), "body", 2
    if re.match(r"^\d+\. ", stripped):
        return stripped, "body", 2
    if stripped.startswith("|"):
        return re.sub(r"\s*\|\s*", " | ", stripped.strip("| ")), "mono", 0
    if stripped in {"```text", "```"}:
        return "", "body", 0
    return stripped, "body", 0


def wrap_line(text: str, indent: int, width: int = MAX_CHARS) -> list[str]:
    if not text:
        return [""]
    prefix = " " * indent
    return textwrap.wrap(
        text,
        width=max(28, width - indent),
        initial_indent=prefix,
        subsequent_indent=prefix + ("  " if text.startswith("- ") else ""),
        break_long_words=False,
        break_on_hyphens=False,
    ) or [prefix]


def cover_stream() -> str:
    stream = ""
    stream += "0.055 0.075 0.085 rg 0 0 612 792 re f\n"
    stream += "0.39 0.78 0.84 RG 1.2 w 54 74 504 644 re S\n"
    stream += "0.85 0.93 0.9 RG 0.6 w 72 92 468 608 re S\n"
    for x in range(90, 540, 45):
        stream += f"0.2 0.36 0.39 RG 0.4 w {x} 94 m {x} 700 l S\n"
    for y in range(120, 690, 45):
        stream += f"0.2 0.36 0.39 RG 0.4 w 72 {y} m 540 {y} l S\n"
    stream += text_command("AXIOM-DSP", 78, 620, "F2", 42)
    stream += text_command("Agentic Engineering Blueprint", 78, 575, "F2", 22)
    stream += text_command("Codex | Pi | Knowledge | Qualification | User Authority", 78, 538, "F1", 12)
    stream += text_command("Blueprint v0.1", 78, 470, "F2", 14)
    stream += text_command("Purpose: design the specialized agentic system around Axiom-DSP.", 78, 442, "F1", 10.5)
    stream += text_command("Boundary: no autonomous accepted-baseline changes; user approval remains mandatory.", 78, 424, "F1", 10.5)
    stream += text_command("Current Axiom Core baseline: v4.1.4.11", 78, 388, "F1", 11)
    stream += text_command("Stability First | Measurement Second | Experimentation Third", 78, 148, "F1", 10)
    stream += text_command("Axiom-DSP Agentic Engineering Blueprint - page 1", 54, 32, "F1", 8)
    return stream


def content_streams(lines: list[str]) -> list[str]:
    pages: list[str] = []
    stream = ""
    y = TOP_Y
    page_number = 2
    for raw_line in lines:
        text, kind, indent = clean_markdown(raw_line)
        if not text:
            y -= LINE_HEIGHT * 0.55
            continue
        if kind == "title":
            continue
        font = "F1"
        size = BODY_SIZE
        if kind == "heading":
            font, size = "F2", HEADING_SIZE
            y -= 5
        elif kind == "subheading":
            font, size = "F2", SUBHEADING_SIZE
            y -= 3
        elif kind == "mono":
            font, size = "F3", 7.8
        width = 78 if kind == "mono" else MAX_CHARS
        for wrapped in wrap_line(text, indent, width):
            if y < BOTTOM_Y + 24:
                stream += text_command(f"Axiom-DSP Agentic Engineering Blueprint - page {page_number}", MARGIN_X, 32, "F1", 8)
                pages.append(stream)
                stream = ""
                y = TOP_Y
                page_number += 1
            stream += text_command(wrapped, MARGIN_X, y, font, size)
            y -= LINE_HEIGHT
    stream += text_command(f"Axiom-DSP Agentic Engineering Blueprint - page {page_number}", MARGIN_X, 32, "F1", 8)
    pages.append(stream)
    return pages


def make_pdf(source: pathlib.Path) -> bytes:
    objects: list[bytes] = []

    def add(obj: str) -> int:
        objects.append(obj.encode("latin-1"))
        return len(objects)

    catalog_id = add("PLACEHOLDER")
    pages_id = add("PLACEHOLDER")
    font_regular_id = add("<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
    font_bold_id = add("<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>")
    font_mono_id = add("<< /Type /Font /Subtype /Type1 /BaseFont /Courier >>")

    raw_lines = source.read_text(encoding="utf-8").splitlines()
    streams = [cover_stream(), *content_streams(raw_lines)]
    page_ids: list[int] = []

    for stream_text in streams:
        stream = stream_text.encode("latin-1")
        content_id = add(f"<< /Length {len(stream)} >>\nstream\n{stream_text}\nendstream")
        page_id = add(
            f"<< /Type /Page /Parent {pages_id} 0 R "
            f"/MediaBox [0 0 {PAGE_WIDTH} {PAGE_HEIGHT}] "
            f"/Resources << /Font << /F1 {font_regular_id} 0 R /F2 {font_bold_id} 0 R /F3 {font_mono_id} 0 R >> >> "
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

    pdf = make_pdf(args.source)
    for destination in [args.repo_pdf, args.windows_pdf]:
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(pdf)
        print(destination)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
