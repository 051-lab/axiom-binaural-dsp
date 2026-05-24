# Axiom Binaural DSP Architecture

## Overview

Axiom Binaural DSP is a JDSP4Linux / JamesDSP EEL2 enhancement core intended to work consistently on speakers and headphones. `v4.1.4.5` is the accepted device-neutral baseline after internal crossfeed was removed. `v4.1.4.6` is the next candidate: it removes a phase-only dry reconstruction from the bass harmonic stage while preserving the generated harmonic branch.

Target priorities:

- Low artifact risk over maximum effect strength
- Phase-stable stereo processing
- Conservative CPU and latency for Android testing devices
- JDSP-safe EEL2 only: no crash-prone polyphase or fractional-delay helper APIs

## Signal Chain

```text
spl0/spl1 input
  -> DC protection
  -> 3-way cascaded biquad M/S spatializer
  -> additive bass harmonic generator
  -> dynamic loudness-contingent exciter
  -> STFT dynamic resonance suppressor
  -> JDSP terminal output limiter (host)
  -> spl0/spl1 output
```

JamesDSP crossfeed may be enabled manually after Axiom for headphone listening; it is not part of the measured core baseline.

## Processing Layers

### Input DC Protection

Each channel passes through a 15 Hz high-pass biquad before nonlinear or dynamic stages. This protects headroom and keeps downstream dynamics from reacting to DC offset.

### 3-Way M/S Spatializer

The script splits stereo input into low, mid, and high regions using cascaded biquad filters:

- Low region: below 150 Hz, summed to mono
- Mid region: 150 Hz to 4 kHz, M/S width controlled by `slider5 * slider2`
- High region: above 4 kHz, M/S width controlled by `slider6 * slider2`

The low mono fold improves headphone bass stability. Mid/high width are independent so perceived space can be increased without widening sub-bass.

### Additive Bass Harmonic Generator

The bass stage extracts content below 90 Hz, applies soft saturation, high-passes the generated harmonic path, and adds those harmonics to the spatializer output.

In `v4.1.4.5`, this stage also split the dry signal into cascaded low-pass and high-pass 90 Hz paths and recombined them before adding harmonics. Analysis shows that reconstruction is level-neutral within `0.001 dB`, but adds approximately `5.0 ms` of group delay at 90 Hz. `v4.1.4.6` removes the redundant dry split, its four high-pass biquads, and its two sample state values. The intended harmonic generation remains active.

Important controls:

- `slider1`: harmonic gain in dB
- `drive`: fixed conservative saturation drive
- 90 Hz extraction/isolation filters: cascaded biquad pairs on the generated branch only

### Dynamic Exciter

The exciter tracks stereo-averaged RMS and applies more high-frequency enhancement at lower levels. The current candidates use sample-rate-derived attack/release and gain smoothing coefficients so the behavior is closer across 44.1, 48, and 96 kHz.

Current timing:

- Loudness attack: 10 ms
- Loudness release: 400 ms
- Exciter gain smoothing: 20 ms
- Exciter band: above 11 kHz

### STFT Dynamic Resonance Suppressor

The suppressor processes the 2-6 kHz region in the STFT domain. The current candidates track per-bin state instead of using one band-global threshold:

- `resBinFloor[bin]`: adaptive magnitude floor
- `resBinGain[bin]`: smoothed per-bin gain
- Stereo-linked magnitude from L/R real and imaginary bin values
- Identical gain applied to L/R real and imaginary parts to preserve stereo phase relationship

This stage is intentionally conservative. It should reduce short harsh resonances without broad pumping or left/right imbalance.

### Crossfeed Ownership

`v4.1.4.4` contains a manual crossfeed path: a delayed opposite-channel signal is band-passed from 150 Hz to 1500 Hz and additively mixed at a default coefficient of `0.33`. For correlated mono material, transfer analysis shows a range of approximately `-3.34 dB` to `+2.31 dB` at 48 kHz, with the peak near 285 Hz. That both spends headroom and alters centered midrange tonality.

`v4.1.4.5` removes the script delay buffers, crossfeed filters, mix arithmetic, and `slider4`; this removal was accepted as the new baseline. `v4.1.4.6` retains that device-neutral core. If crossfeed is useful for a headphone listening session, it is enabled manually in JamesDSP rather than being coupled to the Axiom script.

For reference, host BS2B custom mode at `700 Hz / 6.0 dB` uses complementary filtered paths with gain normalization. Under the same correlated-mono analysis it produces no positive gain peak, avoiding the removed manual path's limiter-driving boost.

### Output Limiter Ownership

`v4.1.4.3` contains a script-local limiter followed by a hard clamp. `v4.1.4.4` removed that processing path. `v4.1.4.5` and `v4.1.4.6` retain the same host-only limiter ownership.

JDSP always applies its output limiter after Liveprog and postgain. The fixed comparison baseline is:

- Limiter threshold: `0` in JDSP4Linux configuration, applied by the engine as approximately `-0.09 dB`; use `-0.10 dB` on RootlessJamesDSP where fractional entry is available
- Limiter release: `60 ms`
- Post gain: `0 dB`
- Host crossfeed: disabled for the Axiom comparison baseline; enable manually only when desired
- Stereo widening, reverb, compander, bass, EQ, convolver, DDC, and tube processing: disabled

## Sliders

| Slider | Default | Range | Purpose |
|---|---:|---:|---|
| `slider1` | 4 dB | -12 to 12 dB | Sub harmonic blend gain |
| `slider2` | 135% | 0 to 200% | Global side width multiplier |
| `slider3` | 50% | 0 to 100% | Loudness-contingent exciter sensitivity |
| `slider5` | 140% | 0 to 200% | Low-mid width multiplier |
| `slider6` | 110% | 0 to 150% | High-frequency width multiplier |
| `slider7` | 50% | 0 to 100% | STFT resonance suppression depth |

## Validation

Run static EEL safety checks:

```bash
scripts/validate_axiom_static.sh src/axiom_binaural_dsp_v4.1.4.3.eel
scripts/validate_axiom_static.sh src/axiom_binaural_dsp_v4.1.4.4.eel
scripts/validate_axiom_static.sh src/axiom_binaural_dsp_v4.1.4.5.eel
scripts/validate_axiom_static.sh src/axiom_binaural_dsp_v4.1.4.6.eel
```

Run coefficient and crossover response analysis:

```bash
scripts/analyze_axiom_response.py
scripts/analyze_axiom_crossfeed.py
scripts/analyze_axiom_bass_path.py
```

Load and save the accepted baseline and phase-preserving bass candidate:

```bash
scripts/hot_reload_liveprog.sh src/axiom_binaural_dsp_v4.1.4.5.eel
scripts/hot_reload_liveprog.sh src/axiom_binaural_dsp_v4.1.4.6.eel
```

## Engineering Constraints

- Do not assign to `$pi`, `$e`, or `$eps`.
- Do not use `%`; wrap indices with explicit comparisons.
- Do not use `FractionalDelayLineInit`, `pfb_init`, or `InitPolyphaseFilterbank`.
- Keep final executable lines of `@sample` as `spl0 = out_L;` and `spl1 = out_R;`.
- Use flat pointer arithmetic for memory blocks and never overlap allocations.
