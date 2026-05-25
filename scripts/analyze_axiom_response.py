#!/usr/bin/env python3
"""Static response checks for Axiom's current EEL biquad topology."""

import cmath
import math


Q = 0.7071
SAMPLE_RATES = (44100.0, 48000.0, 96000.0)
FREQS = (
    20.0, 31.5, 40.0, 63.0, 90.0, 120.0, 150.0, 250.0,
    500.0, 1000.0, 2000.0, 4000.0, 6000.0, 10000.0, 16000.0, 20000.0,
)


def clamp_freq(freq, sr):
    return min(max(freq, 5.0), sr * 0.45)


def biquad(kind, freq, q, sr):
    x = clamp_freq(freq, sr) * 2.0 * math.pi / sr
    sin_x = math.sin(x)
    cos_x = math.cos(x)
    alpha = sin_x / (q * 2.0)

    a0 = 1.0 + alpha
    raw_a1 = -2.0 * cos_x
    raw_a2 = 1.0 - alpha

    if kind == "lowpass":
        raw_b0 = (1.0 - cos_x) * 0.5
        raw_b1 = 1.0 - cos_x
        raw_b2 = (1.0 - cos_x) * 0.5
    elif kind == "highpass":
        raw_b0 = (1.0 + cos_x) * 0.5
        raw_b1 = -(1.0 + cos_x)
        raw_b2 = (1.0 + cos_x) * 0.5
    else:
        raise ValueError(kind)

    return {
        "b0": raw_b0 / a0,
        "b1": raw_b1 / a0,
        "b2": raw_b2 / a0,
        "a1": -raw_a1 / a0,
        "a2": -raw_a2 / a0,
    }


def response(coeffs, freq, sr):
    z1 = cmath.exp(-2j * math.pi * freq / sr)
    z2 = z1 * z1
    num = coeffs["b0"] + coeffs["b1"] * z1 + coeffs["b2"] * z2
    den = 1.0 - coeffs["a1"] * z1 - coeffs["a2"] * z2
    return num / den


def cascaded_response(kind, cutoff, freq, sr, stages=2):
    h = response(biquad(kind, cutoff, Q, sr), freq, sr)
    return h ** stages


def pole_radii(coeffs):
    # EEL structure: y = ... + a1*y1 + a2*y2, denominator z^2 - a1*z - a2.
    a1 = coeffs["a1"]
    a2 = coeffs["a2"]
    disc = cmath.sqrt(a1 * a1 + 4.0 * a2)
    return (abs((a1 + disc) * 0.5), abs((a1 - disc) * 0.5))


def db(value):
    return 20.0 * math.log10(max(abs(value), 1.0e-12))


def crossover_response(freq, sr):
    low = cascaded_response("lowpass", 150.0, freq, sr)
    hp_150 = cascaded_response("highpass", 150.0, freq, sr)
    mid = hp_150 * cascaded_response("lowpass", 4000.0, freq, sr)
    high = hp_150 * cascaded_response("highpass", 4000.0, freq, sr)
    return low + mid + high


def check_stability():
    worst_radius = 0.0
    unstable = []
    for sr in SAMPLE_RATES:
        for kind, cutoff in (
            ("highpass", 15.0), ("lowpass", 90.0), ("highpass", 90.0),
            ("lowpass", 150.0), ("highpass", 150.0),
            ("lowpass", 1500.0), ("lowpass", 4000.0),
            ("highpass", 4000.0), ("highpass", 11000.0),
        ):
            radii = pole_radii(biquad(kind, cutoff, Q, sr))
            worst_radius = max(worst_radius, radii[0], radii[1])
            if radii[0] >= 1.0 or radii[1] >= 1.0:
                unstable.append((sr, kind, cutoff, radii))
    return worst_radius, unstable


def check_crossover():
    rows = []
    worst_abs_db = 0.0
    for sr in SAMPLE_RATES:
        max_freq = min(20000.0, sr * 0.45)
        deviations = []
        for freq in FREQS:
            if freq <= max_freq:
                level = db(crossover_response(freq, sr))
                deviations.append(abs(level))
                rows.append((sr, freq, level))
        worst_abs_db = max(worst_abs_db, max(deviations))
    return worst_abs_db, rows


def main():
    worst_radius, unstable = check_stability()
    print(f"Max biquad pole radius: {worst_radius:.8f}")
    if unstable:
        print("FAIL: unstable filter coefficients detected")
        for sr, kind, cutoff, radii in unstable:
            print(f"  sr={sr:.0f} kind={kind} cutoff={cutoff} radii={radii}")
        return 1
    print("PASS: all checked biquad coefficients are stable")

    worst_abs_db, rows = check_crossover()
    print(f"Max estimated 3-way crossover deviation: {worst_abs_db:.3f} dB")
    if worst_abs_db > 1.5:
        print("WARN: crossover recombination deviation exceeds 1.5 dB")
    else:
        print("PASS: crossover recombination estimate is within 1.5 dB")

    print("Crossover sample points:")
    for sr, freq, level in rows:
        if freq in (20.0, 90.0, 150.0, 1000.0, 4000.0, 10000.0, 20000.0):
            print(f"  sr={sr:7.0f} Hz  f={freq:7.1f} Hz  sum={level:7.3f} dB")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
