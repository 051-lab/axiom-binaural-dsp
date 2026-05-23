# Axiom Binaural DSP Architecture

## Overview
Axiom Binaural DSP is a phase-coherent, mastering-grade audio processing pipeline designed for JamesDSP's EEL2 (Expressive Embedded Language 2) runtime. The architecture consists of five cascading processing layers that transform stereo input into an enhanced binaural output optimized for headphone listening.

**Version:** 3.0 (Audiophile Mastering Edition)  
**Target Platform:** JamesDSP (Android/Linux)  
**Sample Rate:** Any (all filters are sample-rate adaptive)  

---

## Signal Chain Diagram
```
INPUT: spl0 (L), spl1 (R)
         |
         v
[LAYER 1: M/S SPATIALIZER]
  Mid/Side Encode -> HPF 300Hz (Side) -> Width Scale -> Reconstruct L/R
         |
         v
[LAYER 2: VIRTUAL SUB-BASS GENERATOR]
  LPF 90Hz -> Soft-Clip Saturation -> HPF 90Hz -> Blend with original
         |
         v
[LAYER 3: FLETCHER-MUNSON EXCITER]
  Asymmetric Env Follower -> Boost Compute -> HPF 10kHz -> Add Air Band
         |
         v
[LAYER 4: BS2B CROSSFEED MATRIX]
  Circular Buffer (1024) -> Delay ~0.3ms -> Dual LPF 1500Hz -> Mix
         |
         v
[LAYER 5: VCA SOFT-KNEE LIMITER]
  Threshold: 0.92 (~-0.7 dB) | Fast Attack ~2ms | Smooth Release ~300ms
         |
         v
OUTPUT: spl0 (L), spl1 (R) - Phase-coherent, binaurally enhanced
```

---

## Layer-by-Layer Technical Description

### Layer 1: M/S Spatializer
**Purpose:** Convert stereo to Mid/Side domain, apply high-pass filtering to the side channel to remove low-frequency phase issues, then scale side width and reconstruct to L/R.

- Mid = (L + R) * 0.5
- Side = (L - R) * 0.5
- Side channel filtered with HPF at 300Hz (Q=0.707)
- Side width controlled by slider2 (100-200%)
- Reconstruction: L = Mid + Side_filtered * width, R = Mid - Side_filtered * width

### Layer 2: Virtual Sub-Bass Generator
**Purpose:** Generate psychoacoustic sub-bass harmonics for systems with limited low-end response.

- Sub extraction: LPF at 90Hz (Q=0.707, Butterworth)
- Soft-clip saturation: x / (1 + |x|) with 4x drive
- Harmonic isolation: HPF at 90Hz removes fundamental, keeps harmonics
- Additive blend: original + sub + harmonics * subGainLin

### Layer 3: Fletcher-Munson Exciter
**Purpose:** Apply dynamic high-frequency excitation based on equal-loudness contours. Quieter passages receive more high-frequency boost.

- Asymmetric envelope follower: attack 1ms, release 300ms
- boost_db = loudnessSens * (1.0 - env_sqrt) * 6.0 / 100.0
- Air band: HPF at 10kHz extracts high-frequency content
- Additive: spl += air_band * (exp(boost_db * 0.115129) - 1.0)

### Layer 4: BS2B Crossfeed Matrix
**Purpose:** Simulate natural speaker listening via Bauer Stereophonic-to-Binaural conversion.

- Circular buffer: 1024 samples per channel
- Interaural delay: floor(0.0003 * srate) samples (~0.3ms at 44.1kHz)
- Skull attenuation: dual-stage LPF cascade at 1500Hz (4th-order effective)
- HPF at 150Hz on crossfeed path (removes low-frequency crosstalk)
- Mix: spl0 += cross_l * crossAmtLin, spl1 += cross_r * crossAmtLin

### Layer 5: VCA Soft-Knee Limiter
**Purpose:** Prevent clipping after all processing stages with transparent gain reduction.

- Threshold: 0.92 (~-0.7 dBFS)
- Ballistics: fast attack (~2ms), smooth release (~300ms)
- 1-pole gain smoothing to prevent TIM/clicks
- Hard clip safety net at ±0.999

---

## DSP Math: Biquad Filter Coefficients
All filters use Direct Form I biquad structure with bilinear transform:
```
y[n] = b0*x[n] + b1*x[n-1] + b2*x[n-2] - a1*y[n-1] - a2*y[n-2]
```

### Filter Summary Table
| Filter | Frequency | Q | Type | Purpose |
|--------|-----------|---|------|---------|
| HPF300 | 300 Hz | 0.707 | 2nd-order HPF | Side channel cleanup |
| LPF90 | 90 Hz | 0.707 | 2nd-order LPF | Sub-bass extraction |
| HPF90 | 90 Hz | 0.707 | 2nd-order HPF | Harmonic isolation |
| HPF10k | 10 kHz | 0.707 | 2nd-order HPF | Air band extraction |
| LPF1500 | 1500 Hz | 0.707 | 4th-order LPF (x2) | BS2B skull attenuation |
| HPF150 | 150 Hz | 0.707 | 2nd-order HPF | Crossfeed low-cut |

---

## Parameter Tuning Guide

### Slider Reference
| Slider | Parameter | Default | Range | Effect |
|--------|-----------|---------|-------|--------|
| slider1 | Sub Harmonics Gain | 3 dB | 0-12 dB | Sub-bass harmonic blend level |
| slider2 | Side Width | 135% | 100-200% | Stereo width multiplier |
| slider3 | Fletcher-Munson Sensitivity | 45% | 0-100% | Dynamic air-band boost amount |
| slider4 | Crossfeed Amount | 60% | 0-100% | BS2B crossfeed blend ratio |

### Presets
- **Trance/EDM:** Sub Gain 6-9dB, Side Width 150-180%, FM Sens 40%, Crossfeed 60%
- **Audiophile:** Sub Gain 3dB, Side Width 120%, FM Sens 50%, Crossfeed 40-50%
- **Late Night:** Sub Gain 0-3dB, Side Width 110%, FM Sens 60-80%, Crossfeed 50%

---

## Known Limitations
1. **Fixed Delay Resolution:** BS2B uses integer sample delays (~22.7us at 44.1kHz)
2. **Static Filter Coefficients:** Q/type hardcoded at init
3. **Single-Band Dynamics:** Exciter uses broadband RMS
4. **No Oversampling:** Operates at native sample rate
5. **Circular Buffer Size:** Fixed at 1024 samples

---

## v4.0 Roadmap
1. **STFT Integration:** Linear-phase EQ and surgical processing
2. **Polyphase Filterbank:** Efficient multi-band processing
3. **Fractional Delay Lines:** Lagrange/Thiran interpolation
4. **Real-Time Spectrum Analyzer:** Visual feedback
5. **Preset Memory Slots:** Internal configuration storage
6. **Mid-Side EQ:** Independent channel shaping
