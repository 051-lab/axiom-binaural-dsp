#!/usr/bin/env python3
"""Generate the Axiom session work-log cover artwork.

The cover is intentionally deterministic so the public PDF can be refreshed
without relying on external image services. It uses Pillow when available and
keeps the visual language technical: spectrum grid, waveform traces, and
manual-cover typography.
"""

from __future__ import annotations

import argparse
import json
import math
import pathlib
import random

from PIL import Image, ImageDraw, ImageFilter, ImageFont


REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = REPO_ROOT / "docs" / "assets" / "axiom-session-work-log-cover.jpg"
DEFAULT_POLICY = REPO_ROOT / "tools" / "axiom-team" / "policy.json"

WIDTH = 1650
HEIGHT = 2138
FONT_ROOT = pathlib.Path("/usr/share/fonts/truetype/dejavu")


def load_font(name: str, size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    path = FONT_ROOT / name
    if path.exists():
        return ImageFont.truetype(str(path), size=size)
    return ImageFont.load_default()


def accepted_baseline_version(policy_path: pathlib.Path) -> str:
    try:
        policy = json.loads(policy_path.read_text(encoding="utf-8"))
        return str(policy["acceptedBaseline"]["version"])
    except (OSError, KeyError, TypeError, json.JSONDecodeError):
        return "unknown"


def draw_text(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    text: str,
    font: ImageFont.FreeTypeFont | ImageFont.ImageFont,
    fill: tuple[int, int, int],
    spacing: int = 0,
) -> None:
    x, y = xy
    if spacing <= 0:
        draw.text((x, y), text, font=font, fill=fill)
        return
    for char in text:
        draw.text((x, y), char, font=font, fill=fill)
        bbox = draw.textbbox((x, y), char, font=font)
        x += bbox[2] - bbox[0] + spacing


def draw_gradient_background(base: Image.Image) -> None:
    draw = ImageDraw.Draw(base)
    for y in range(HEIGHT):
        t = y / HEIGHT
        r = int(12 + 10 * t)
        g = int(17 + 18 * t)
        b = int(21 + 22 * t)
        if 0.54 < t < 0.82:
            b += int(10 * math.sin((t - 0.54) / 0.28 * math.pi))
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))


def draw_grid(overlay: Image.Image) -> None:
    draw = ImageDraw.Draw(overlay, "RGBA")
    for x in range(110, WIDTH, 110):
        alpha = 42 if x % 330 == 0 else 18
        draw.line([(x, 0), (x, HEIGHT)], fill=(120, 190, 205, alpha), width=1)
    for y in range(120, HEIGHT, 120):
        alpha = 38 if y % 360 == 0 else 16
        draw.line([(0, y), (WIDTH, y)], fill=(120, 190, 205, alpha), width=1)

    for offset in range(-600, 1700, 150):
        draw.line(
            [(offset, HEIGHT), (offset + 720, 0)],
            fill=(65, 110, 125, 18),
            width=1,
        )


def draw_waveform_panel(overlay: Image.Image) -> None:
    draw = ImageDraw.Draw(overlay, "RGBA")
    x0, y0, w, h = 150, 755, 1350, 500
    draw.rounded_rectangle((x0, y0, x0 + w, y0 + h), radius=18, outline=(155, 214, 222, 135), width=2)
    draw.rectangle((x0 + 1, y0 + 1, x0 + w - 1, y0 + h - 1), fill=(8, 14, 17, 92))

    for i in range(1, 12):
        x = x0 + int(w * i / 12)
        draw.line([(x, y0 + 28), (x, y0 + h - 28)], fill=(125, 193, 202, 38), width=1)
    for i in range(1, 6):
        y = y0 + int(h * i / 6)
        draw.line([(x0 + 28, y), (x0 + w - 28, y)], fill=(125, 193, 202, 38), width=1)

    random.seed(51411)
    colors = [(102, 215, 229, 210), (234, 244, 236, 178), (143, 184, 166, 155)]
    for trace, color in enumerate(colors):
        points: list[tuple[int, int]] = []
        for i in range(w - 96):
            x = x0 + 48 + i
            t = i / (w - 96)
            amp = 0.34 + 0.07 * math.sin(t * math.tau * 2.4 + trace)
            signal = (
                math.sin(t * math.tau * (3.1 + trace * 0.55))
                + 0.38 * math.sin(t * math.tau * (9.0 + trace * 1.2))
                + 0.18 * math.sin(t * math.tau * (23.0 + trace))
            )
            y = y0 + h // 2 - int(signal * amp * h * 0.28)
            points.append((x, y))
        draw.line(points, fill=color, width=3 - min(trace, 1))

    band_left = x0 + 70
    band_bottom = y0 + h - 54
    for i in range(44):
        t = i / 43
        height = int(40 + 160 * (math.sin(t * math.pi) ** 1.8) + 34 * math.sin(t * 31))
        bar_x = band_left + i * 28
        draw.rounded_rectangle(
            (bar_x, band_bottom - height, bar_x + 12, band_bottom),
            radius=4,
            fill=(92, 205, 218, 94),
        )


def draw_phase_diagram(overlay: Image.Image) -> None:
    draw = ImageDraw.Draw(overlay, "RGBA")
    cx, cy = 1260, 430
    for radius, alpha in [(245, 44), (178, 55), (104, 72)]:
        draw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), outline=(136, 206, 216, alpha), width=2)
    draw.line((cx - 280, cy, cx + 280, cy), fill=(136, 206, 216, 62), width=2)
    draw.line((cx, cy - 280, cx, cy + 280), fill=(136, 206, 216, 62), width=2)
    for angle in range(0, 360, 30):
        rad = math.radians(angle)
        x1 = cx + int(math.cos(rad) * 82)
        y1 = cy + int(math.sin(rad) * 82)
        x2 = cx + int(math.cos(rad) * 250)
        y2 = cy + int(math.sin(rad) * 250)
        draw.line((x1, y1, x2, y2), fill=(136, 206, 216, 28), width=1)

    path: list[tuple[int, int]] = []
    for i in range(420):
        t = i / 419
        angle = t * math.tau * 2.2
        radius = 68 + 155 * t + 22 * math.sin(t * math.tau * 9)
        path.append((cx + int(math.cos(angle) * radius), cy + int(math.sin(angle) * radius)))
    draw.line(path, fill=(232, 244, 237, 168), width=3)


def draw_manual_marks(overlay: Image.Image) -> None:
    draw = ImageDraw.Draw(overlay, "RGBA")
    draw.rectangle((92, 88, WIDTH - 92, HEIGHT - 88), outline=(220, 236, 230, 150), width=3)
    draw.rectangle((116, 112, WIDTH - 116, HEIGHT - 112), outline=(112, 176, 188, 90), width=1)
    draw.line((150, 1510, 1500, 1510), fill=(205, 230, 222, 130), width=2)
    draw.line((150, 1682, 1500, 1682), fill=(95, 155, 166, 72), width=1)
    for x in range(150, 1500, 90):
        draw.line((x, 1502, x, 1522), fill=(205, 230, 222, 110), width=1)


def draw_cover_text(overlay: Image.Image, baseline_version: str) -> None:
    draw = ImageDraw.Draw(overlay, "RGBA")
    title = load_font("DejaVuSans-Bold.ttf", 146)
    subtitle = load_font("DejaVuSans-Bold.ttf", 70)
    body = load_font("DejaVuSans.ttf", 40)
    small = load_font("DejaVuSans.ttf", 30)
    mono = load_font("DejaVuSansMono.ttf", 30)
    mono_small = load_font("DejaVuSansMono.ttf", 24)

    draw_text(draw, (150, 165), "051-LAB ENGINEERING RECORDS", mono_small, (176, 219, 217), spacing=2)
    draw_text(draw, (150, 255), "AXIOM-DSP", title, (239, 246, 239))
    draw_text(draw, (156, 420), "SESSION WORK LOG", subtitle, (112, 216, 229))
    draw_text(draw, (158, 520), "JamesDSP / EEL2 Audio DSP", body, (210, 228, 222))

    draw_text(draw, (150, 1615), f"Current Baseline: {baseline_version}", body, (239, 246, 239))
    draw_text(draw, (150, 1726), "Stability First | Measurement Second | Experimentation Third", small, (194, 219, 214))
    draw_text(draw, (150, 1822), "Repository workflow, qualification gates, Pi runbooks, and Codex orchestration record.", small, (166, 196, 196))
    draw_text(draw, (150, 1935), "DOCUMENT CLASS: PUBLIC REPOSITORY LOG", mono, (119, 207, 219))
    draw_text(draw, (150, 1985), "NO AUDIO CAPTURES OR PRIVATE MATERIAL INCLUDED", mono_small, (178, 204, 199))


def make_cover(baseline_version: str) -> Image.Image:
    base = Image.new("RGB", (WIDTH, HEIGHT))
    draw_gradient_background(base)
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw_grid(overlay)
    draw_phase_diagram(overlay)
    draw_waveform_panel(overlay)
    draw_manual_marks(overlay)
    overlay = overlay.filter(ImageFilter.UnsharpMask(radius=1.2, percent=110, threshold=3))
    base = Image.alpha_composite(base.convert("RGBA"), overlay)

    text_layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw_cover_text(text_layer, baseline_version)
    base = Image.alpha_composite(base, text_layer)
    return base.convert("RGB")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=pathlib.Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--policy", type=pathlib.Path, default=DEFAULT_POLICY)
    args = parser.parse_args()

    args.output.parent.mkdir(parents=True, exist_ok=True)
    make_cover(accepted_baseline_version(args.policy)).save(args.output, "JPEG", quality=94, optimize=True, progressive=True)
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
