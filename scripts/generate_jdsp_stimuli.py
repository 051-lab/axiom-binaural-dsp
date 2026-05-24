#!/usr/bin/env python3
"""Generate deterministic stereo PCM WAV stimuli for JDSP capture tests."""

import argparse
import math
import struct
import wave
from pathlib import Path


DEFAULT_SAMPLE_RATE = 48000
DEFAULT_DURATION = 2.0
PEAK_SAMPLE = 32767


def clamp(value):
    return max(-1.0, min(1.0, value))


def pcm16(value):
    return int(round(clamp(value) * PEAK_SAMPLE))


def fade_envelope(frame, total_frames, fade_frames):
    if fade_frames <= 0:
        return 1.0
    if frame < fade_frames:
        return frame / fade_frames
    if frame >= total_frames - fade_frames:
        return max(0.0, (total_frames - frame - 1) / fade_frames)
    return 1.0


def impulse(frame, sample_rate, total_frames):
    del total_frames
    value = 0.8 if frame == int(round(0.1 * sample_rate)) else 0.0
    return value, value


def bass_burst(frame, sample_rate, total_frames):
    del total_frames
    time_s = frame / sample_rate
    value = 0.0
    for start_s, end_s, frequency in ((0.15, 0.70, 45.0), (0.95, 1.50, 70.0)):
        if start_s <= time_s < end_s:
            edge_s = min(time_s - start_s, end_s - time_s)
            envelope = min(1.0, edge_s / 0.025)
            value = 0.65 * envelope * math.sin(2.0 * math.pi * frequency * (time_s - start_s))
            break
    return value, value


def sweep(frame, sample_rate, total_frames):
    duration_s = total_frames / sample_rate
    time_s = frame / sample_rate
    low_hz = 20.0
    high_hz = min(20000.0, sample_rate * 0.45)
    ratio = high_hz / low_hz
    phase = 2.0 * math.pi * low_hz * duration_s * (ratio ** (time_s / duration_s) - 1.0) / math.log(ratio)
    envelope = fade_envelope(frame, total_frames, max(1, int(round(sample_rate * 0.01))))
    value = 0.5 * envelope * math.sin(phase)
    return value, value


def correlated_mono(frame, sample_rate, total_frames):
    time_s = frame / sample_rate
    envelope = fade_envelope(frame, total_frames, max(1, int(round(sample_rate * 0.01))))
    value = envelope * (
        0.25 * math.sin(2.0 * math.pi * 90.0 * time_s)
        + 0.20 * math.sin(2.0 * math.pi * 1000.0 * time_s + 0.31)
        + 0.14 * math.sin(2.0 * math.pi * 6000.0 * time_s + 0.77)
    )
    return value, value


def side_only(frame, sample_rate, total_frames):
    time_s = frame / sample_rate
    envelope = fade_envelope(frame, total_frames, max(1, int(round(sample_rate * 0.01))))
    value = envelope * (
        0.34 * math.sin(2.0 * math.pi * 250.0 * time_s)
        + 0.24 * math.sin(2.0 * math.pi * 2400.0 * time_s + 0.43)
    )
    return value, -value


STIMULI = (
    ("impulse", impulse),
    ("bass_burst", bass_burst),
    ("sweep", sweep),
    ("correlated_mono", correlated_mono),
    ("side_only", side_only),
)


def write_stimulus(path, signal, sample_rate, total_frames):
    with wave.open(str(path), "wb") as output:
        output.setnchannels(2)
        output.setsampwidth(2)
        output.setframerate(sample_rate)
        chunk = bytearray()
        for frame in range(total_frames):
            left, right = signal(frame, sample_rate, total_frames)
            chunk.extend(struct.pack("<hh", pcm16(left), pcm16(right)))
            if len(chunk) >= 16384:
                output.writeframesraw(chunk)
                chunk.clear()
        if chunk:
            output.writeframesraw(chunk)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output_dir", type=Path, help="directory for generated WAV files")
    parser.add_argument("--sample-rate", type=int, default=DEFAULT_SAMPLE_RATE)
    parser.add_argument("--duration", type=float, default=DEFAULT_DURATION)
    args = parser.parse_args()

    if args.sample_rate < 8000:
        parser.error("--sample-rate must be at least 8000")
    if args.duration < 1.55:
        parser.error("--duration must be at least 1.55 seconds to contain all probes")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    total_frames = int(round(args.sample_rate * args.duration))
    for name, signal in STIMULI:
        path = args.output_dir / (name + ".wav")
        write_stimulus(path, signal, args.sample_rate, total_frames)
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
