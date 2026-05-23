# Changelog

All notable changes to Axiom Binaural DSP are documented in this file.

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
