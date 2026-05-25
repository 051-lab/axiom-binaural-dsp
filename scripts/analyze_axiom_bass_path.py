#!/usr/bin/env python3
"""Measure the removable dry-path transformation in the Axiom bass stage."""

import cmath
import math

from analyze_axiom_response import SAMPLE_RATES, cascaded_response, db


def legacy_dry_response(freq, sample_rate):
    low = cascaded_response("lowpass", 90.0, freq, sample_rate)
    high = cascaded_response("highpass", 90.0, freq, sample_rate)
    return low + high


def group_delay_ms(freq, sample_rate):
    delta_hz = max(0.001, freq * 0.0001)
    lower_phase = cmath.phase(legacy_dry_response(freq - delta_hz, sample_rate))
    upper_phase = cmath.phase(legacy_dry_response(freq + delta_hz, sample_rate))
    phase_delta = upper_phase - lower_phase
    while phase_delta > math.pi:
        phase_delta -= 2.0 * math.pi
    while phase_delta < -math.pi:
        phase_delta += 2.0 * math.pi
    return -phase_delta / (2.0 * math.pi * (2.0 * delta_hz)) * 1000.0


def frequency_grid(sample_rate):
    upper = min(20000.0, sample_rate * 0.45)
    ratio = upper / 10.0
    return (10.0 * ratio ** (step / 1000.0) for step in range(1001))


def main():
    worst_deviation_db = 0.0
    minimum_delay_ms = float("inf")

    print("v4.1.4.5 dry bass reconstruction (LP90 + HP90):")
    for sample_rate in SAMPLE_RATES:
        deviation_db = max(
            abs(db(legacy_dry_response(freq, sample_rate)))
            for freq in frequency_grid(sample_rate)
        )
        delay_at_45 = group_delay_ms(45.0, sample_rate)
        delay_at_90 = group_delay_ms(90.0, sample_rate)
        worst_deviation_db = max(worst_deviation_db, deviation_db)
        minimum_delay_ms = min(minimum_delay_ms, delay_at_90)
        print(
            f"  sr={sample_rate:7.0f} Hz  magnitude deviation={deviation_db:.6f} dB"
            f"  delay@45Hz={delay_at_45:.3f} ms  delay@90Hz={delay_at_90:.3f} ms"
        )

    if worst_deviation_db > 0.01:
        print("FAIL: legacy dry crossover is not magnitude-neutral enough for removal audit")
        return 1
    if minimum_delay_ms < 4.5:
        print("FAIL: expected legacy dry-path phase delay was not measured")
        return 1

    print("PASS: legacy dry split changes phase while contributing no material level shaping")
    print("v4.1.4.6 dry bass path: direct signal plus generated harmonic branch only")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
