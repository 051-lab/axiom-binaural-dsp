#!/usr/bin/env python3
"""Compare removed v4.1.4.4 crossfeed with optional manual JDSP BS2B."""

import cmath
import math

from analyze_axiom_response import cascaded_response, db


SAMPLE_RATES = (44100.0, 48000.0, 96000.0)
PROBE_FREQS = (50.0, 90.0, 150.0, 250.0, 285.0, 400.0, 500.0, 630.0, 750.0, 1000.0, 1500.0, 2000.0)
INTERNAL_MIX = 0.60 * 0.55
JDSP_FCUT = 700.0
JDSP_FEED_TENTHS_DB = 60.0


def internal_mono_response(freq, sr):
    delay_samples = math.floor(0.00065 * sr)
    path = cascaded_response("highpass", 150.0, freq, sr)
    path *= cascaded_response("lowpass", 1500.0, freq, sr)
    path *= cmath.exp(-2j * math.pi * freq * delay_samples / sr)
    return 1.0 + INTERNAL_MIX * path


def host_bs2b_mono_response(freq, sr):
    level = JDSP_FEED_TENTHS_DB / 10.0
    gain_lo_db = level * -5.0 / 6.0 - 3.0
    gain_hi_db = level / 6.0 - 3.0
    gain_lo = 10.0 ** (gain_lo_db / 20.0)
    gain_hi = 1.0 - 10.0 ** (gain_hi_db / 20.0)
    freq_hi = JDSP_FCUT * 2.0 ** ((gain_lo_db - 20.0 * math.log10(gain_hi)) / 12.0)
    z1 = cmath.exp(-2j * math.pi * freq / sr)

    pole_lo = math.exp(-2.0 * math.pi * JDSP_FCUT / sr)
    low = gain_lo * (1.0 - pole_lo) / (1.0 - pole_lo * z1)

    pole_hi = math.exp(-2.0 * math.pi * freq_hi / sr)
    high = (1.0 - gain_hi * (1.0 - pole_hi) - pole_hi * z1) / (1.0 - pole_hi * z1)

    normalization = 1.0 / (1.0 - gain_hi + gain_lo)
    return (high + low) * normalization


def extrema(response, sr):
    values = [(db(response(float(freq), sr)), freq) for freq in range(1, int(min(20000.0, sr * 0.45)) + 1)]
    return max(values), min(values)


def main():
    print(f"v4.1.4.4 internal mix coefficient: {INTERNAL_MIX:.3f}")
    print(f"Optional manual JDSP BS2B setting: cutoff={JDSP_FCUT:.0f} Hz, feed={JDSP_FEED_TENTHS_DB / 10.0:.1f} dB")
    print()

    failure = False
    for sr in SAMPLE_RATES:
        internal_max, internal_min = extrema(internal_mono_response, sr)
        host_max, host_min = extrema(host_bs2b_mono_response, sr)
        print(
            f"sr={sr:7.0f} Hz  internal mono range={internal_min[0]:+6.3f} to {internal_max[0]:+6.3f} dB "
            f"(max @ {internal_max[1]:.0f} Hz)"
        )
        print(
            f"sr={sr:7.0f} Hz  host BS2B mono range={host_min[0]:+6.3f} to {host_max[0]:+6.3f} dB "
            f"(max @ {host_max[1]:.0f} Hz)"
        )
        if internal_max[0] < 2.0 or host_max[0] > 0.01:
            failure = True

    print()
    print("48 kHz correlated-mono probe points:")
    print(" frequency | internal crossfeed | host BS2B")
    for freq in PROBE_FREQS:
        internal = db(internal_mono_response(freq, 48000.0))
        host = db(host_bs2b_mono_response(freq, 48000.0))
        print(f"{freq:8.0f} Hz | {internal:+16.3f} dB | {host:+8.3f} dB")

    if failure:
        print("FAIL: crossfeed ownership assumptions no longer match the measured transfer functions")
        return 1

    print("PASS: host BS2B eliminates the internal crossfeed's correlated-mono peak boost")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
