# Axiom Binaural DSP

[![Version](https://img.shields.io/badge/version-v3.0-blue.svg)](https://github.com/051-lab/axiom-binaural-dsp/releases)
[![Platform](https://img.shields.io/badge/platform-JamesDSP-green.svg)](https://github.com/james34602/JamesDSPManager)
[![License](https://img.shields.io/badge/license-MIT-yellow.svg)](LICENSE)

**Phase-coherent mastering-grade binaural processing for JamesDSP**

Axiom Binaural DSP is a professional audio processing script for JamesDSP's EEL2 runtime, designed to deliver audiophile-quality binaural enhancement for headphone listening. The five-layer processing pipeline combines M/S spatialization, virtual sub-bass generation, Fletcher-Munson loudness compensation, BS2B crossfeed, and transparent limiting.

## Features

### Layer 1: M/S Spatializer
- Mid/Side stereo encoding with side-channel high-pass filtering (300Hz)
- Adjustable stereo width from 100% to 200%
- Removes low-frequency phase issues in the side channel

### Layer 2: Virtual Sub-Bass Generator
- Psychoacoustic sub-bass synthesis via soft-clip saturation
- 90Hz crossover with Butterworth alignment (Q=0.707)
- Harmonic blending for perceived bass extension on small drivers
- Gain control: 0-12dB

### Layer 3: Fletcher-Munson Exciter
- Dynamic high-frequency excitation based on equal-loudness contours
- Asymmetric envelope follower (1ms attack / 300ms release)
- Air band extraction at 10kHz+
- Sensitivity control: 0-100%

### Layer 4: BS2B Crossfeed Matrix
- Bauer Stereophonic-to-Binaural simulation
- ~0.3ms interaural delay with circular buffer
- Dual-stage 1500Hz lowpass filter (skull attenuation)
- Crossfeed amount: 0-100%

### Layer 5: VCA Soft-Knee Limiter
- Transparent peak limiting at ~-0.7 dBFS (0.92 linear)
- Fast attack (~2ms) / smooth release (~300ms) ballistics
- 1-pole gain smoothing prevents TIM and clicks
- Hard clip safety net at +/-0.999

## Installation

### JamesDSP Android
1. Copy `src/axiom_binaural_dsp.eel` to your JamesDSP liveprog directory
2. Open JamesDSP -> Liveprog -> Load script -> select `axiom_binaural_dsp.eel`
3. Enable the Liveprog engine
4. Optionally import `presets/axiom-preset.conf` as a full preset

### JamesDSP Linux
1. Copy `src/axiom_binaural_dsp.eel` to `~/.config/jamesdsp/liveprog/`
2. In JamesDSP settings, point Liveprog to the script file
3. Enable the Liveprog engine

## Quick Start: Default Slider Settings

| Slider | Parameter | Default | Range |
|--------|-----------|---------|-------|
| slider1 | Sub Harmonics Gain | 3 dB | 0-12 dB |
| slider2 | Side Width | 135% | 100-200% |
| slider3 | Fletcher-Munson Sensitivity | 45% | 0-100% |
| slider4 | Crossfeed Amount | 60% | 0-100% |

## Tuning Presets

- **Trance/EDM:** Sub Gain 6-9dB, Side Width 150-180%, FM Sens 40%, Crossfeed 60%
- **Audiophile:** Sub Gain 3dB, Side Width 120%, FM Sens 50%, Crossfeed 40-50%
- **Late Night:** Sub Gain 0-3dB, Side Width 110%, FM Sens 60-80%, Crossfeed 50%

## Repository Structure

```
axiom-binaural-dsp/
  src/
    axiom_binaural_dsp.eel    # Main EEL2 DSP script
  presets/
    axiom-preset.conf         # JamesDSP preset configuration
  docs/
    architecture.md           # Technical architecture documentation
  README.md
  CHANGELOG.md
```

## Architecture

See [docs/architecture.md](docs/architecture.md) for the full technical documentation including signal chain diagram, DSP math, filter coefficient tables, and tuning guides.

## License

MIT License - see LICENSE for details.

## Acknowledgments

- Bauer BS2B crossfeed algorithm
- Fletcher-Munson equal-loudness research
- JamesDSP EEL2 runtime by James34602

---

## AI Agent Setup

This repository is configured for AI agent collaboration. The following files provide complete context for any AI assistant working on this codebase:

| File | Purpose |
|------|---------|
| [`AGENTS.md`](AGENTS.md) | **Start here** — complete operating instructions, EEL2 constraints, file editing rules |
| [`.github/copilot-instructions.md`](.github/copilot-instructions.md) | GitHub Copilot workspace context (auto-loaded) |
| [`CONTRIBUTING.md`](CONTRIBUTING.md) | Commit conventions, code standards, testing checklist |
| [`docs/JDSP4Linux_Knowledge_Base.md`](docs/JDSP4Linux_Knowledge_Base.md) | Full EEL2/JDSP runtime API reference |
| [`docs/architecture.md`](docs/architecture.md) | 5-layer signal chain documentation |

### Quick Reference for AI Agents

```eel2
// Critical rules (violations cause mute/crash):
// 1. Never assign to $pi
// 2. No FractionalDelayLineInit (use manual circular buffers)
// 3. No % modulo (use conditional wrap)
// 4. Use this.* for persistent state inside function()
// 5. Additive mixing only (never replace spl0/spl1 mid-chain)
// 6. Final @sample lines MUST be: spl0 = out_L; spl1 = out_R;
// 7. Initialize ALL variables in @init
```
