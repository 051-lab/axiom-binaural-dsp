#!/usr/bin/env python3
"""Generate the Axiom session work-log PDF copies.

The source is a small Markdown file where each `## Run ...` section becomes a
new PDF page. When the cover artwork exists, it is embedded as page 1. The
generator intentionally uses only the Python standard library so the session
log can be refreshed without installing a document toolchain.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import textwrap
from dataclasses import dataclass


REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = REPO_ROOT / "docs" / "session-work-log.md"
DEFAULT_REPO_PDF = REPO_ROOT / "docs" / "session-work-log.pdf"
DEFAULT_WINDOWS_PDF = pathlib.Path("/mnt/c/Users/soloa/Documents/Axiom-DSP-Session-Work-Log.pdf")
DEFAULT_COVER_IMAGE = REPO_ROOT / "docs" / "assets" / "axiom-session-work-log-cover.jpg"
DEFAULT_POLICY = REPO_ROOT / "tools" / "axiom-team" / "policy.json"

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
COVER_SEARCH_TEXT = [
    ("Axiom-DSP", 54, 700, "F2", 36),
    ("Session Work Log", 54, 654, "F2", 24),
    ("Engineering Record", 54, 622, "F1", 15),
    ("JamesDSP / EEL2 Audio DSP", 54, 594, "F1", 12),
    ("Current Baseline: {baseline_version}", 54, 566, "F1", 12),
    ("Stability First | Measurement Second | Experimentation Third", 54, 538, "F1", 11),
]


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


def accepted_baseline_version(policy_path: pathlib.Path) -> str:
    try:
        policy = json.loads(policy_path.read_text(encoding="utf-8"))
        return str(policy["acceptedBaseline"]["version"])
    except (OSError, KeyError, TypeError, json.JSONDecodeError):
        return "unknown"


def text_command(text: str, x: float, y: float, font: str, size: float) -> str:
    return f"BT /{font} {size:g} Tf 1 0 0 1 {x:g} {y:g} Tm ({pdf_escape(text)}) Tj ET\n"


def invisible_text_command(text: str, x: float, y: float, font: str, size: float) -> str:
    return f"BT /{font} {size:g} Tf 3 Tr 1 0 0 1 {x:g} {y:g} Tm ({pdf_escape(text)}) Tj ET\n"


def jpeg_dimensions(data: bytes) -> tuple[int, int]:
    if len(data) < 4 or data[:2] != b"\xff\xd8":
        raise ValueError("cover image must be a JPEG file")
    index = 2
    start_of_frame = {
        0xC0,
        0xC1,
        0xC2,
        0xC3,
        0xC5,
        0xC6,
        0xC7,
        0xC9,
        0xCA,
        0xCB,
        0xCD,
        0xCE,
        0xCF,
    }
    while index < len(data):
        while index < len(data) and data[index] != 0xFF:
            index += 1
        while index < len(data) and data[index] == 0xFF:
            index += 1
        if index >= len(data):
            break
        marker = data[index]
        index += 1
        if marker in {0xD8, 0xD9, 0x01} or 0xD0 <= marker <= 0xD7:
            continue
        if index + 2 > len(data):
            break
        length = int.from_bytes(data[index : index + 2], "big")
        if length < 2 or index + length > len(data):
            break
        if marker in start_of_frame:
            segment = data[index + 2 : index + length]
            if len(segment) < 5:
                break
            height = int.from_bytes(segment[1:3], "big")
            width = int.from_bytes(segment[3:5], "big")
            return width, height
        index += length
    raise ValueError("could not read JPEG dimensions")


def cover_page_stream(total_pages: int, baseline_version: str) -> str:
    stream = "q\n"
    stream += f"{PAGE_WIDTH} 0 0 {PAGE_HEIGHT} 0 0 cm\n"
    stream += "/ImCover Do\n"
    stream += "Q\n"
    for text, x, y, font, size in COVER_SEARCH_TEXT:
        stream += invisible_text_command(text.format(baseline_version=baseline_version), x, y, font, size)
    stream += text_command(f"Axiom-DSP Session Work Log - page 1 of {total_pages}", MARGIN_X, 32, "F1", 8)
    return stream


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


def make_pdf(entries: list[RunEntry], cover_image: pathlib.Path | None = None, baseline_version: str = "unknown") -> bytes:
    objects: list[bytes] = []

    def add_bytes(obj: bytes) -> int:
        objects.append(obj)
        return len(objects)

    def add(obj: str) -> int:
        return add_bytes(obj.encode("latin-1"))

    catalog_id = add("PLACEHOLDER")
    pages_id = add("PLACEHOLDER")
    font_regular_id = add("<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
    font_bold_id = add("<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>")
    page_ids: list[int] = []

    cover_image_id: int | None = None
    if cover_image is not None and cover_image.exists():
        image_data = cover_image.read_bytes()
        width, height = jpeg_dimensions(image_data)
        cover_image_id = add_bytes(
            (
                f"<< /Type /XObject /Subtype /Image /Width {width} /Height {height} "
                f"/ColorSpace /DeviceRGB /BitsPerComponent 8 /Filter /DCTDecode "
                f"/Length {len(image_data)} >>\nstream\n"
            ).encode("latin-1")
            + image_data
            + b"\nendstream"
        )

    total_pages = len(entries) + (1 if cover_image_id is not None else 0)

    if cover_image_id is not None:
        stream = cover_page_stream(total_pages, baseline_version).encode("latin-1")
        content_id = add_bytes(b"<< /Length " + str(len(stream)).encode("latin-1") + b" >>\nstream\n" + stream + b"\nendstream")
        page_id = add(
            f"<< /Type /Page /Parent {pages_id} 0 R "
            f"/MediaBox [0 0 {PAGE_WIDTH} {PAGE_HEIGHT}] "
            f"/Resources << /Font << /F1 {font_regular_id} 0 R /F2 {font_bold_id} 0 R >> "
            f"/XObject << /ImCover {cover_image_id} 0 R >> >> "
            f"/Contents {content_id} 0 R >>"
        )
        page_ids.append(page_id)

    start_page = 2 if cover_image_id is not None else 1
    for idx, entry in enumerate(entries, start=start_page):
        stream = page_stream(entry, idx, total_pages).encode("latin-1")
        content_id = add_bytes(b"<< /Length " + str(len(stream)).encode("latin-1") + b" >>\nstream\n" + stream + b"\nendstream")
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
    parser.add_argument("--cover-image", type=pathlib.Path, default=DEFAULT_COVER_IMAGE)
    parser.add_argument("--policy", type=pathlib.Path, default=DEFAULT_POLICY)
    parser.add_argument("--no-cover", action="store_true")
    args = parser.parse_args()

    entries = parse_runs(args.source)
    cover_image = None if args.no_cover else args.cover_image
    pdf = make_pdf(entries, cover_image, accepted_baseline_version(args.policy))
    for destination in [args.repo_pdf, args.windows_pdf]:
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(pdf)
        print(destination)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
