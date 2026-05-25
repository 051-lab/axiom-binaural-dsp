# Changelog

All notable changes to Axiom Binaural DSP are documented in this file.

---

## [4.1.4.7] - 2026-05-24 - Transparent Headroom Candidate

### Changed
- Preserved the accepted `v4.1.4.6` bass, spatial, exciter, and STFT processing without parameter retuning.
- Added a fixed terminal `-1.0 dB` linear output reserve before JDSP's host-owned limiter.
- Extended static validation and liveprog preset loading for the new candidate.
- Increased real-host comparison alignment search to tolerate capture scheduling offsets between independent Liveprog renders.
- Added an A/B suite failure gate for silent host captures after a WSLg routing attempt returned invalid muted recordings.

### Validation
- Executed the real-JDSP host suite comparing accepted `v4.1.4.6` against `v4.1.4.7`.
- Reduced the side-only stress-probe peak from approximately `-0.128 dBFS` to `-1.128 dBFS`, with zero clipped samples.
- Continuous bass-burst and sweep probes reduced by approximately `1.0 dB` as intended; impulse captures remain safety probes rather than fine gain measurements due to live capture timing variability.

---

## [4.1.4.6] - 2026-05-24 - Phase-Preserving Bass Injection Baseline

### Changed
- Removed the redundant 90 Hz high-pass dry reconstruction from the bass harmonic stage.
- Preserved low-band saturation and additive harmonic injection while leaving the spatializer dry output intact.
- Removed four unused dry-path biquad instances and two sample-state variables from the new candidate.
- Removed two redundant per-sample constant assignments without changing their initialized values.
- Kept internal crossfeed absent; JamesDSP crossfeed is now a manual playback choice only.
- Corrected the hot-reload helper to reload a changed script even when its file path is unchanged.

### Validation
- Added bass-path analysis showing the removed LP+HP dry reconstruction was level-neutral within `0.001 dB` but added approximately `5.0 ms` group delay at `90 Hz`.
- Added a real-JDSP A/B testbench with deterministic stimuli, isolated processed-output capture, state restoration, and JSON/Markdown difference reports.
- Executed the host suite comparing `v4.1.4.5` with `v4.1.4.6`; all five candidate captures remained unclipped, with the side-only probe reaching `-0.115 dBFS`.

---

## [4.1.4.5] - 2026-05-23 - Device-Neutral Core Baseline

### Changed
- Removed the manual EEL crossfeed delay buffers, band-pass filters, additive mix, and crossfeed slider.
- Established crossfeed as an optional JamesDSP control rather than an always-on Axiom stage.
- Kept the accepted `v4.1.4.4` sound-shaping and host-limiter architecture unchanged outside crossfeed ownership.

### Validation
- Added crossfeed transfer analysis: the removed default path ranged from approximately `-3.34 dB` to `+2.31 dB` on correlated mono at 48 kHz; JDSP BS2B introduces no positive gain peak at the selected setting.

---

## [4.1.4.4] - 2026-05-23 - Host Limiter Baseline

### Changed
- Removed the script-local limiter and hard clamp so JDSP supplies the single terminal output limiter.
- Removed initialized-but-unused resonance/limiter state while preserving the active spatial, sub, exciter, and STFT processing.

---

## [3.0] - 2025 - Audiophile Mastering Edition

### Added
- **Asymmetric Envelope Follower** for Fletcher-Munson exciter (1ms attack / 300ms release)
- **BS2B Crossfeed Implementation** - circular buffer delay (~0.3ms), dual-stage 1500Hz LPF
- **HPF 150Hz on crossfeed path** - removes low-frequency crosstalk artifacts
- **VCA Soft-Knee Limiter** - fast attack (~2ms), smooth release (~300ms), 1-pole gain smoothing
- **Hard clip safety net** at +/-0.999 to prevent DAC overload
- **DC offset protection** via high-pass filter at input
- **presets/axiom-preset.conf** - JamesDSP-compatible full preset file
- **docs/architecture.md** - comprehensive technical documentation

### Fixed
- **Full Mute Bug** - corrected spl0/spl1 write-back in @sample block
- **Circular Buffer Index Wrapping** - fixed boundary condition with ternary operator
- **EEL2 Reserved Constant** - removed assignment to $pi (read-only in JamesDSP)
- **Non-existent Function** - replaced FractionalDelayLineInit with manual circular buffer
- **Namespace Pollution** - cleaned up global variable declarations
- **Additive Mixing** - all layers now use additive mixing to prevent signal dropouts

### Changed
- Refactored signal chain to use object-style filter processing
- Improved layer isolation for phase coherence
- Limiter threshold adjusted to 0.92 (~-0.7 dBFS) for headroom

---

## [2.0] - 2024 - Working Build

### Fixed
- spl0/spl1 write-back corrected
- Circular buffer implementation fixed
- Namespace pollution resolved
- Signal recombination made additive

### Added
- Biquad filter coefficient pre-computation in @init
- Slider-driven parameter updates in @slider

---

## [1.0] - 2023 - Initial Architecture

### Added
- Five-layer processing design concept
- Initial EEL2 implementation
- M/S Spatializer
- Virtual Sub-Bass Generator
- Fletcher-Munson Exciter placeholder
- BS2B Crossfeed Matrix placeholder
- Output Limiter placeholder

---

## Upcoming: v4.0 Roadmap

1. **STFT Integration** - Linear-phase EQ and surgical frequency processing
2. **Polyphase Filterbank** - Efficient multi-band parallel processing
3. **Fractional Delay Lines** - Lagrange/Thiran interpolation for sub-sample accuracy
4. **Real-Time Spectrum Analyzer** - Visual frequency feedback via EEL2 GFX
5. **Preset Memory Slots** - Internal configuration storage (8 slots)
6. **Mid-Side EQ** - Independent frequency shaping per M/S channel
7. **Oversampling** - 2x/4x oversampling for saturation stages
8. **HRTF Convolution** - Head-related transfer function for personalized binaural
