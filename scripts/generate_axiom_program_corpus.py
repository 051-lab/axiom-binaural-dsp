#!/usr/bin/env python3
"""Generate original deterministic bass-heavy program-like WAV passages."""

from __future__ import annotations

import argparse
import math
import struct
import wave
from pathlib import Path


SAMPLE_RATE = 48000
DURATION_SECONDS = 4.0
TARGET_PEAK = 0.65
PEAK_SAMPLE = 32767


def envelope(time_s: float, start_s: float, duration_s: float, attack_s: float, release_s: float) -> float:
    relative = time_s - start_s
    if relative < 0.0 or relative >= duration_s:
        return 0.0
    attack = min(1.0, relative / attack_s) if attack_s > 0.0 else 1.0
    remaining = duration_s - relative
    release = min(1.0, remaining / release_s) if release_s > 0.0 else 1.0
    return min(attack, release)


def decaying_tone(time_s: float, start_s: float, frequency_hz: float, decay_s: float) -> float:
    relative = time_s - start_s
    if relative < 0.0:
        return 0.0
    return math.sin(2.0 * math.pi * frequency_hz * relative) * math.exp(-relative / decay_s)


def sub_kick_sequence(frame: int, sample_rate: int, total_frames: int) -> tuple[float, float]:
    del total_frames
    time_s = frame / sample_rate
    mono = 0.0
    for start_s, frequency_hz in ((0.10, 46.0), (0.60, 46.0), (1.10, 55.0), (1.60, 46.0),
                                  (2.10, 46.0), (2.60, 55.0), (3.10, 46.0), (3.60, 55.0)):
        mono += 0.78 * decaying_tone(time_s, start_s, frequency_hz, 0.17)
        mono += 0.10 * decaying_tone(time_s, start_s, 110.0, 0.045)
    pulse = math.sin(2.0 * math.pi * 1000.0 * time_s) * envelope(time_s, 0.0, 4.0, 0.01, 0.01)
    left = mono + 0.045 * pulse
    right = mono - 0.045 * pulse
    return left, right


def sustained_bass_synth(frame: int, sample_rate: int, total_frames: int) -> tuple[float, float]:
    del total_frames
    time_s = frame / sample_rate
    notes = ((0.00, 1.00, 55.0), (1.00, 1.00, 73.416), (2.00, 1.00, 82.407), (3.00, 1.00, 90.0))
    bass = 0.0
    for start_s, duration_s, frequency_hz in notes:
        env = envelope(time_s, start_s, duration_s, 0.012, 0.05)
        phase = 2.0 * math.pi * frequency_hz * (time_s - start_s)
        bass += env * (0.78 * math.sin(phase) + 0.20 * math.sin(2.0 * phase) + 0.08 * math.sin(3.0 * phase))
    air_env = envelope(time_s, 0.0, 4.0, 0.02, 0.02)
    left = bass + air_env * (0.08 * math.sin(2.0 * math.pi * 880.0 * time_s))
    right = bass + air_env * (0.08 * math.sin(2.0 * math.pi * 1100.0 * time_s + 0.4))
    return left, right


def dense_low_end_mix(frame: int, sample_rate: int, total_frames: int) -> tuple[float, float]:
    del total_frames
    time_s = frame / sample_rate
    bass_notes = ((0.0, 0.5, 55.0), (0.5, 0.5, 55.0), (1.0, 0.5, 65.406), (1.5, 0.5, 73.416))
    bass = 0.0
    cycle = time_s - 2.0 * math.floor(time_s / 2.0)
    for start_s, duration_s, frequency_hz in bass_notes:
        env = envelope(cycle, start_s, duration_s, 0.008, 0.06)
        bass += env * (0.56 * math.sin(2.0 * math.pi * frequency_hz * cycle)
                       + 0.14 * math.sin(2.0 * math.pi * 2.0 * frequency_hz * cycle))
    kick = 0.0
    for start_s in (0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5):
        kick += 0.52 * decaying_tone(time_s, start_s, 48.0, 0.12)
    pad_env = envelope(time_s, 0.0, 4.0, 0.02, 0.02)
    left = bass + kick + pad_env * (0.12 * math.sin(2.0 * math.pi * 440.0 * time_s)
                                     + 0.06 * math.sin(2.0 * math.pi * 2200.0 * time_s))
    right = bass + kick + pad_env * (0.12 * math.sin(2.0 * math.pi * 554.365 * time_s + 0.25)
                                      + 0.06 * math.sin(2.0 * math.pi * 2600.0 * time_s + 0.4))
    return left, right


PROGRAMS = (
    ("sub_kick_sequence", sub_kick_sequence),
    ("sustained_bass_synth", sustained_bass_synth),
    ("dense_low_end_mix", dense_low_end_mix),
)


def render_program(signal, sample_rate: int = SAMPLE_RATE, duration_s: float = DURATION_SECONDS) -> list[tuple[float, float]]:
    total_frames = int(round(sample_rate * duration_s))
    frames = [signal(frame, sample_rate, total_frames) for frame in range(total_frames)]
    peak = max(abs(value) for pair in frames for value in pair)
    scale = TARGET_PEAK / peak if peak > 0.0 else 1.0
    return [(left * scale, right * scale) for left, right in frames]


def write_wav(path: Path, frames: list[tuple[float, float]], sample_rate: int = SAMPLE_RATE) -> None:
    with wave.open(str(path), "wb") as output:
        output.setnchannels(2)
        output.setsampwidth(2)
        output.setframerate(sample_rate)
        payload = bytearray()
        for left, right in frames:
            payload.extend(
                struct.pack(
                    "<hh",
                    round(max(-1.0, min(1.0, left)) * PEAK_SAMPLE),
                    round(max(-1.0, min(1.0, right)) * PEAK_SAMPLE),
                )
            )
            if len(payload) >= 16384:
                output.writeframesraw(payload)
                payload.clear()
        if payload:
            output.writeframesraw(payload)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--sample-rate", type=int, default=SAMPLE_RATE)
    parser.add_argument("--duration", type=float, default=DURATION_SECONDS)
    args = parser.parse_args()
    if args.sample_rate < 8000:
        parser.error("--sample-rate must be at least 8000")
    if args.duration < 4.0:
        parser.error("--duration must be at least 4.0 seconds")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for name, signal in PROGRAMS:
        path = args.output_dir / f"{name}.wav"
        write_wav(path, render_program(signal, args.sample_rate, args.duration), args.sample_rate)
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
