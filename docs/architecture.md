# Axiom Binaural DSP Architecture

## Overview

Axiom Binaural DSP is a JDSP4Linux / JamesDSP EEL2 enhancement core intended to work consistently on speakers and headphones. `v4.1.4.9` is the accepted listening baseline: it retains `.8` behavior at default controls and applies a measured reduced reserve slope above the default Sub Harmonics Gain to retain more elevated-bass output level.

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
  -> transparent / bass-aware output reserve (`v4.1.4.7` through `v4.1.4.9`)
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

The exciter tracks stereo-averaged RMS and applies more high-frequency enhancement at lower levels. The current baseline uses sample-rate-derived attack/release and gain smoothing coefficients so the behavior is closer across 44.1, 48, and 96 kHz.

Current timing:

- Loudness attack: 10 ms
- Loudness release: 400 ms
- Exciter gain smoothing: 20 ms
- Exciter band: above 11 kHz

### STFT Dynamic Resonance Suppressor

The suppressor processes the 2-6 kHz region in the STFT domain. The current baseline tracks per-bin state instead of using one band-global threshold:

- `resBinFloor[bin]`: adaptive magnitude floor
- `resBinGain[bin]`: smoothed per-bin gain
- Stereo-linked magnitude from L/R real and imaginary bin values
- Identical gain applied to L/R real and imaginary parts to preserve stereo phase relationship

This stage is intentionally conservative. It should reduce short harsh resonances without broad pumping or left/right imbalance.

### Crossfeed Ownership

`v4.1.4.4` contains a manual crossfeed path: a delayed opposite-channel signal is band-passed from 150 Hz to 1500 Hz and additively mixed at a default coefficient of `0.33`. For correlated mono material, transfer analysis shows a range of approximately `-3.34 dB` to `+2.31 dB` at 48 kHz, with the peak near 285 Hz. That both spends headroom and alters centered midrange tonality.

`v4.1.4.5` removes the script delay buffers, crossfeed filters, mix arithmetic, and `slider4`. `v4.1.4.6` retains that device-neutral core. `v4.1.4.9` remains device-neutral and does not alter crossfeed ownership. If crossfeed is useful for a headphone listening session, it is enabled manually in JamesDSP rather than being coupled to the Axiom script.

For reference, host BS2B custom mode at `700 Hz / 6.0 dB` uses complementary filtered paths with gain normalization. Under the same correlated-mono analysis it produces no positive gain peak, avoiding the removed manual path's limiter-driving boost.

### Output Limiter Ownership

`v4.1.4.3` contains a script-local limiter followed by a hard clamp. `v4.1.4.4` removed that processing path. `v4.1.4.5` through `v4.1.4.9` retain the same host-only limiter ownership.

### Transparent Output Reserve

`v4.1.4.7` applies a fixed `-1.0 dB` gain immediately before the final output assignment. The change is deliberately terminal and linear: it preserves the `.6` bass generation, width ratios, exciter, STFT behavior, and stereo phase relationship while providing margin before JDSP's terminal limiter.

The real-host stress probe identified the need for this margin. Under the default controls, the `.6` side-only capture reached `-0.128 dBFS`; `.7` reduced the same probe to `-1.128 dBFS` with no clipped samples. This established the transparent reserve inherited by `.8` and `.9`.

### Bass-Aware Output Reserve Evolution

`v4.1.4.8` preserves the `.7` output multiplier exactly while `slider1 <= +4 dB`. When the user requests more generated bass than the accepted default, it adds terminal reserve equal to the amount above default:

```text
bassReserveDb = max(0, slider1 - 4)
outputGain = -1 dB fixed reserve - bassReserveDb
```

This does not compress or retune the generated bass branch; its purpose is to reduce avoidable host-limiter involvement at elevated user-selected bass gain. Real-host qualification confirmed that `.8` matches `.7` at default and provides the expected additional reserve at elevated Sub Harmonics settings.

`v4.1.4.9` preserves `.8` exactly while `slider1 <= +4 dB` and reduces the additional reserve above default to retain more practical playback level:

```text
bassReserveDb = max(0, slider1 - 4) * 0.750
outputGain = -1 dB fixed reserve - bassReserveDb
```

Real-host range screening rejected a more aggressive `0.500 dB/dB` reserve slope. Managed `.8` versus `.9` qualification passed with an investigation marker for existing near-ceiling host-limiter participation, and device A/B listening accepted `.9` as the new baseline.

JDSP always applies its output limiter after Liveprog and postgain. The fixed comparison baseline is:

- Master processing: enabled
- Limiter threshold: `-1.00 dB`; selected after CC0 high-energy material clipped at `-0.10 dB`, while persistent `-1.00 dB` operation cleared clipping across the external corpus
- Limiter release: `60 ms`
- Post gain: `0 dB`
- Host crossfeed: disabled for the Axiom comparison baseline; enable manually only when desired
- Stereo widening, reverb, compander, bass, EQ, convolver, DDC, and tube processing: disabled

The `.9` baseline was accepted after device A/B listening against `.8` and real-host verification. Managed qualification passed default equivalence, recovered elevated-bass level, `+12 dB` terminal margin, and program-like corpus checks. A four-excerpt CC0 music corpus remained unclipped at the persistent `-1.00 dB` host limiter threshold; its dense electronic passage reached `-0.443 dBFS` at default controls and is retained as limiter involvement already present in the `.8` comparison.

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
scripts/validate_axiom_static.sh src/axiom_binaural_dsp_v4.1.4.7.eel
scripts/validate_axiom_static.sh src/axiom_binaural_dsp_v4.1.4.8.eel
scripts/validate_axiom_static.sh src/axiom_binaural_dsp_v4.1.4.9.eel
```

Run coefficient and crossover response analysis:

```bash
scripts/analyze_axiom_response.py
scripts/analyze_axiom_crossfeed.py
scripts/analyze_axiom_bass_path.py
```

Run real-host A/B capture through JDSP Liveprog:

```bash
scripts/run_jdsp_ab_testbench.py \
  src/axiom_binaural_dsp_v4.1.4.8.eel \
  src/axiom_binaural_dsp_v4.1.4.9.eel \
  /tmp/axiom-v48-v49-host-suite \
  --pulse-server unix:/run/user/1000/pulse/native
```

The suite exercises impulse, bass transient, sustained correlated `90 Hz` bass pressure at `0.65` peak input, sweep, correlated mono, and side-only inputs. `render_jdsp_host.py` targets an explicit Pulse server, captures only a private temporary sink fed by JDSP's processed-output stream, and restores all host keys it temporarily normalizes. The orchestrator rejects silent reference or candidate captures instead of accepting a broken routing run as analysis. Liveprog reloads still reinitialize internal DSP history, so execute the suite in a dedicated development JDSP session. Continuous probes are suitable for output/gain comparisons; the impulse probe is retained primarily for transient, mute, and corruption checks because separately scheduled live captures can vary in alignment. Generated captures and reports belong outside the repository, such as under `/tmp`.

For the WSL workstation route, `scripts/run_jdsp_wsl_qualification.py` invokes the local `~/.local/bin/jdsp-audio-reset` launcher, verifies that its native PulseAudio server exposes a `JamesDSP` sink, sets the selected host limiter threshold once for the managed session, and restores both the preceding threshold and PipeWire-Pulse on completion or failure. It runs the default-control A/B suite, creates temporary elevated-bass fixtures, performs a maximum-bass boundary capture, and renders a default-control original program-like corpus. `generate_axiom_program_corpus.py` produces three deterministic bass-dense passages: sub/kick transients, a sustained bass-synth phrase, and a dense low-end mix. These passages are reproducible engineering material, not commercial music or an assertion of musical coverage. For the accepted `.8` versus `.9` comparison, elevated probes verify expected level recovery from the reduced reserve law and the maximum-bass capture is gated against the terminal observation ceiling. When a default pressure or corpus output exceeds `-0.50 dBFS`, the report returns `PASS_WITH_INVESTIGATION`: no EEL regression has been established, but the host limiter is participating enough to record the observation. The fixtures change only slider defaults and never replace source EEL scripts.

When a private manifest is supplied through `--local-material-manifest`, `run_jdsp_local_material.py` converts only the selected excerpt windows to temporary 48 kHz, 16-bit stereo PCM without normalizing their original decoded level, renders the selected baseline and candidate through the same host route at default controls, and merges integrity and terminal-margin observations into the managed report. The manifest and excerpt outputs must remain outside the repository; this permits relevant listening-library checks without distributing source recordings or treating deterministic test arrangements as substitutes for actual program material.

`scripts/run_jdsp_accepted_stress.py` characterizes the selected accepted baseline at the tracked `-1.00 dB` host threshold before another DSP candidate is justified. It repeats each registered external excerpt, rejects clipped or unusable level profiles, and records stable peaks above `-0.50 dBFS` as existing limiter-pressure behavior rather than retroactively failing the accepted listening baseline. New investigations use accepted `.9`; the `.8` artifact remains the comparison evidence that justified `.9`.

`scripts/run_jdsp_sub_slider_map.py` expands that measurement across temporary fixtures based on the selected accepted script whose only difference is the `Sub Harmonics Gain` default. Its default grid of `+4`, `+6`, `+8`, `+10`, and `+12 dB` establishes whether real program material remains unclipped as user bass gain rises. A failure at the accepted `+4 dB` default rejects the baseline measurement; clipping found only at elevated settings records an operating-range boundary and supplies evidence for deciding whether a later bass-reserve revision is worthwhile. The original `.8` map exposed repeatable RMS retreat and led to `.9`; future maps start from the accepted `.9` reserve law.

`scripts/run_jdsp_reserve_law_screen.py` evaluates that tradeoff before any versioned DSP edit. At a practical elevated `+8 dB` slider setting, it creates external fixtures whose conditional reserve slope is reduced from the accepted `1.000 dB` attenuation per added slider dB to candidate slopes `0.875`, `0.750`, and `0.500`. It runs one excluded conditioning render before measuring each fixture/excerpt set, then screens critical dense excerpts using repeated real-host captures and rejects a slope that clips or crosses `-0.50 dBFS`. A slope must recover measurable RMS level on every screened excerpt before broader boundary qualification is justified; a passing focused screen is not listening acceptance or a production architecture change.

`scripts/run_jdsp_reserve_range_qualification.py` takes focused-screen survivors through full registered-material coverage before any listening candidate is created. It starts at `+12 dB` Sub Harmonics Gain and descends through `+10`, `+8`, and `+6 dB`, rejecting and stopping a slope at the first clipped or above-boundary result. An unstable scalar measurement receives one fresh conditioned retry before it fails the qualification as unusable evidence. This ordering minimizes unnecessary live-host renders while preserving the actual full-range eligibility decision.

Qualify measurement repeatability before relying on fine differences. `scripts/qualify_jdsp_repeatability.py` accepts three or more captures of one script/stimulus/configuration and recommends five for decision-grade reports. It rejects invalid stereo PCM, frame mismatch, silence, clipping, caller-excessive level spread, and low-confidence alignment. Its optional jitter value is relative content-alignment spread only; it is not an absolute latency measurement. Variance and confidence limits must be supplied by the caller until repeated host measurements provide a defensible tolerance policy.

Use `scripts/analyze_jdsp_transfer.py` only with low-level deterministic stimuli and processed-output WAVs. Since capture occurs after JDSP host processing, its result is a stimulus-conditioned `end_to_end_host_path` measurement, not an Axiom-only transfer function. A report is unqualified when processed output is silent, clipped, or above the default `-6.0 dBFS` ceiling intended to avoid terminal-limiter involvement.

The transfer report retains timing against the known stimulus playback timeline without correlation alignment. When `--capture-pre-roll-ms` is supplied, it represents a known intentional lead-in in that timeline, not measured host latency. A pure mono probe identifies `M->M` and `M->S`; a pure side-only probe identifies `S->M` and `S->S`. General stereo material energizes both input components and cannot identify an individual transfer-matrix column from a single render, so those matrix values are deliberately invalidated.

`scripts/analyze_axiom_subharmonics.py` models the exact `.7` sub-harmonic branch independently of host capture: two cascaded 90 Hz low-pass filters, the fixed `drive = 3.5` saturator, two cascaded 90 Hz harmonic-path high-pass filters, `slider1` gain, and the terminal `-1.0 dB` reserve. It sweeps controlled tone levels and slider positions so high-gain headroom risks can be identified before proposing a sound-changing candidate. Because the exciter, STFT suppressor, host limiter, and program-material interactions are excluded, branch-local peaks are investigation triggers rather than final output claims.

Example offline qualification commands:

```bash
scripts/qualify_jdsp_repeatability.py \
  /tmp/axiom-repeat/run-1.wav /tmp/axiom-repeat/run-2.wav /tmp/axiom-repeat/run-3.wav \
  /tmp/axiom-repeat/run-4.wav /tmp/axiom-repeat/run-5.wav \
  --max-peak-spread-db 0.10 --max-rms-spread-db 0.10 --min-correlation 0.999 \
  --json /tmp/axiom-repeat/repeatability.json \
  --markdown /tmp/axiom-repeat/repeatability.md

scripts/analyze_jdsp_transfer.py \
  /tmp/axiom-transfer/stimulus.wav /tmp/axiom-transfer/processed.wav \
  --label v4.1.4.7-mono-probe \
  --json /tmp/axiom-transfer/transfer.json \
  --markdown /tmp/axiom-transfer/transfer.md

scripts/analyze_axiom_subharmonics.py \
  --json /tmp/axiom-subharmonics.json \
  --markdown /tmp/axiom-subharmonics.md

scripts/analyze_axiom_subharmonics.py \
  --reserve-above-slider-db 4 \
  --json /tmp/axiom-v48-subharmonics.json \
  --markdown /tmp/axiom-v48-subharmonics.md
```

Load an earlier comparison version or the accepted baseline:

```bash
scripts/hot_reload_liveprog.sh src/axiom_binaural_dsp_v4.1.4.5.eel
scripts/hot_reload_liveprog.sh src/axiom_binaural_dsp_v4.1.4.6.eel
scripts/hot_reload_liveprog.sh src/axiom_binaural_dsp_v4.1.4.7.eel
scripts/hot_reload_liveprog.sh src/axiom_binaural_dsp_v4.1.4.8.eel
scripts/hot_reload_liveprog.sh src/axiom_binaural_dsp_v4.1.4.9.eel
```

## Engineering Constraints

- Do not assign to `$pi`, `$e`, or `$eps`.
- Do not use `%`; wrap indices with explicit comparisons.
- Do not use `FractionalDelayLineInit`, `pfb_init`, or `InitPolyphaseFilterbank`.
- Keep final executable lines of `@sample` as `spl0 = out_L;` and `spl1 = out_R;`.
- Use flat pointer arithmetic for memory blocks and never overlap allocations.
