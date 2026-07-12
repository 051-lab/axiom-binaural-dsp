# Axiom Binaural DSP

[![Platform](https://img.shields.io/badge/platform-JamesDSP-green.svg)](https://github.com/james34602/JamesDSPManager)
[![Runtime](https://img.shields.io/badge/runtime-EEL2-blue.svg)](docs/JDSP4Linux_Knowledge_Base.md)
[![License](https://img.shields.io/badge/license-MIT-yellow.svg)](LICENSE)

**Evidence-driven psychoacoustic audio enhancement for JamesDSP.**

Axiom is a real-time EEL2 processing system designed to improve stereo
coherence, perceived bass extension, clarity, and listening comfort on mobile
playback systems. It is intended for both headphones and speakers, while
headphone-specific crossfeed remains controlled by JamesDSP.

Axiom development begins with a human description of the desired sound. That
description is converted into one narrow DSP hypothesis, tested through a
controlled experiment, technically qualified through JamesDSP, and finally
accepted or rejected through human listening.

## Current Status

| Role | Label | Script | Status |
| --- | --- | --- | --- |
| Accepted baseline | **Axiom Clean R011** | `src/axiom_binaural_dsp_v4.1.4.11.eel` | Recommended |
| Active candidate | **Axiom Clean R012** | `src/axiom_clean_r012.eel` | Unqualified; investigation required |

R011 remains the accepted and recommended version. R012 has passed static
validation, but its elevated-bass technical qualification requires further
investigation before structured listening or promotion.

The exact operational state is recorded in [`axiom-state.json`](axiom-state.json).

## What Axiom Does

```text
Input
  -> DC protection
  -> low-mid/high-band mid-side width shaping
  -> additive bass harmonic enhancement
  -> level-dependent high-frequency excitation
  -> stereo-linked STFT resonance suppression
  -> conservative output reserve
  -> JamesDSP terminal limiter
  -> Output
```

### Stereo coherence

- Three-way stereo processing with low frequencies folded toward mono stability
- Independent low-mid and high-frequency width control
- Device-neutral processing for headphones and speakers

### Perceived bass extension

- Low-band extraction below 90 Hz
- Soft nonlinear generation of upper harmonics
- Additive harmonic injection that preserves the direct dry path

### Dynamic clarity

- Level-dependent enhancement above 11 kHz
- Sample-rate-derived attack, release, and smoothing behavior
- Conservative gain limiting to reduce fatigue risk

### Resonance control

- Stereo-linked STFT attenuation in the 2-6 kHz region
- Adaptive per-bin tracking
- Matching gain applied to both channels to preserve stereo relationships

## Design Principles

- Low artifact risk before maximum effect strength
- Stable stereo imaging and mono compatibility
- Conservative CPU and latency for Android-class hardware
- JamesDSP-safe EEL2 processing
- Measurement-informed experimentation
- Final sound decisions made through human listening
- Accepted and historical DSP files are never overwritten in place

## Installation

### JamesDSP on Android

1. Download `src/axiom_binaural_dsp_v4.1.4.11.eel`.
2. Copy or import it into the JamesDSP Liveprog area.
3. Load the script and enable Liveprog.
4. Configure the JamesDSP output limiter:
   - Threshold: `-1.00 dB`
   - Release: `60 ms`
   - Postgain: `0 dB`
5. Enable JamesDSP crossfeed only when desired for headphone listening.

### JDSP4Linux

```bash
scripts/hot_reload_liveprog.sh \
  src/axiom_binaural_dsp_v4.1.4.11.eel \
  Axiom-Clean-R011
```

The helper loads the accepted script with the qualified host settings and keeps
crossfeed disabled for the neutral baseline.

## Axiom Clean R011 Controls

| Control | Default | Range |
| --- | ---: | ---: |
| Sub Harmonics Gain | `+4 dB` | `-12` to `+12 dB` |
| Global Side Width | `135%` | `0` to `200%` |
| Fletcher-Munson Sensitivity | `50%` | `0` to `100%` |
| Low-Mid Width Multiplier | `126%` | `0` to `200%` |
| High-Frequency Width Multiplier | `110%` | `0` to `150%` |
| STFT Resonance Suppression | `50%` | `0` to `100%` |

## Development Workflow

```text
human sound description
  -> one clear sound goal
  -> one narrow DSP hypothesis
  -> Axiom Labs fixture or analysis
  -> technical qualification
  -> owner listening decision
  -> keep, reject, retest, or promote
```

A Labs result is not accepted behavior. A candidate is not accepted merely
because it exists or passes measurements. Only explicit human listening
acceptance can authorize a promotion path.

See [`AXIOM.md`](AXIOM.md) for the project philosophy and
[`docs/dsp-change-workflow.md`](docs/dsp-change-workflow.md) for the active
sound-to-DSP workflow.

## Repository Map

| Area | Purpose |
| --- | --- |
| `src/` | Accepted, candidate, and historical EEL2 scripts |
| `src/labs/` | Controlled, non-authoritative DSP experiments |
| `docs/` | Architecture, current state, qualification, and workflow documentation |
| `docs/archive/` | Historical plans, reviews, and completed Labs records |
| `docs/knowledge/` | Repository-safe DSP research notes |
| `scripts/` | Validation, rendering, analysis, and qualification tools |
| `tools/axiom-codex/` | Repository helper and guardrail tooling |
| `tools/axiom-team/` | Serialized JamesDSP qualification harness |

Private music, captures, local manifests, generated reports, and device-specific
state remain outside the repository. Sanitized findings may be recorded in
qualification documents.

## Documentation

- [Plain-language Axiom overview](AXIOM.md)
- [Current system status](docs/system-status.md)
- [DSP architecture](docs/architecture.md)
- [DSP change workflow](docs/dsp-change-workflow.md)
- [Accepted R011 qualification](docs/qualification-v4.1.4.11.md)
- [R012 technical qualification record](docs/qualification-r012.md)
- [Release and promotion gates](docs/release-gates.md)
- [Complete documentation index](docs/README.md)

## About the Name

“Binaural” describes Axiom's listening-oriented psychoacoustic and stereo
processing mission. The current Axiom Clean core is a device-neutral stereo
enhancement processor, not a full HRTF spatial renderer.

## License

Axiom Binaural DSP is released under the [MIT License](LICENSE).

## Acknowledgments

- JamesDSP and JDSP4Linux EEL2 runtime by James34602
- Fletcher-Munson equal-loudness research
- Bauer BS2B crossfeed research and implementation history
