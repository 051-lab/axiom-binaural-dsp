# Axiom Binaural DSP Architecture

## Overview

Axiom Binaural DSP is a JDSP4Linux / JamesDSP EEL2 enhancement core intended to work consistently on speakers and headphones. `v4.1.4.10` is the accepted listening baseline: it retains `.9` bass reserve behavior and applies a measured reduction to default low-mid side width.

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
  -> transparent / bass-aware output reserve (`v4.1.4.7` and later)
  -> JDSP terminal output limiter (host)
  -> spl0/spl1 output
```

JamesDSP crossfeed may be enabled manually after Axiom for headphone listening; it is not part of the measured core baseline.

## Processing Layers

### Input DC Protection

Each channel passes through a 15 Hz high-pass biquad before nonlinear or dynamic stages. This protects headroom and keeps downstream dynamics from reacting to DC offset.

### 3-Way M/S Spatializer

The script splits stereo input into low, mid, and high regions using cascaded biquad filters:

- Low-pass region: below 150 Hz, summed to mono; the complementary high-pass
  crossover skirt retains some side energy near the split
- Mid region: 150 Hz to 4 kHz, M/S width controlled by `slider5 * slider2`
- High region: above 4 kHz, M/S width controlled by `slider6 * slider2`

The low mono fold improves headphone bass stability. Mid/high width are independent so perceived space can be increased without substantially widening deep sub-bass. This is not a brick-wall mono boundary: the widened high-pass transition can retain side information in upper sub-bass and low bass near `150 Hz`.

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

`v4.1.4.5` removes the script delay buffers, crossfeed filters, mix arithmetic, and `slider4`. `v4.1.4.6` retains that device-neutral core. `v4.1.4.10` remains device-neutral and does not alter crossfeed ownership. If crossfeed is useful for a headphone listening session, it is enabled manually in JamesDSP rather than being coupled to the Axiom script.

For reference, host BS2B custom mode at `700 Hz / 6.0 dB` uses complementary filtered paths with gain normalization. Under the same correlated-mono analysis it produces no positive gain peak, avoiding the removed manual path's limiter-driving boost.

### Output Limiter Ownership

`v4.1.4.3` contains a script-local limiter followed by a hard clamp. `v4.1.4.4` removed that processing path. `v4.1.4.5` and later retain the same host-only limiter ownership.

### Transparent Output Reserve

`v4.1.4.7` applies a fixed `-1.0 dB` gain immediately before the final output assignment. The change is deliberately terminal and linear: it preserves the `.6` bass generation, width ratios, exciter, STFT behavior, and stereo phase relationship while providing margin before JDSP's terminal limiter.

The real-host stress probe identified the need for this margin. Under the default controls, the `.6` side-only capture reached `-0.128 dBFS`; `.7` reduced the same probe to `-1.128 dBFS` with no clipped samples. This established the transparent reserve inherited by `.8`, `.9`, and `.10`.

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

`v4.1.4.10` retains this output reserve law without modification. Its only
sound-changing default is the qualified low-mid width reduction described
below.

JDSP always applies its output limiter after Liveprog and postgain. The fixed comparison baseline is:

- Master processing: enabled
- Limiter threshold: `-1.00 dB`; selected after CC0 high-energy material clipped at `-0.10 dB`, while persistent `-1.00 dB` operation cleared clipping across the external corpus
- Limiter release: `60 ms`
- Post gain: `0 dB`
- Host crossfeed: disabled for the Axiom comparison baseline; enable manually only when desired
- Stereo widening, reverb, compander, bass, EQ, convolver, DDC, and tube processing: disabled

The `.9` baseline was accepted after device A/B listening against `.8` and real-host verification. Managed qualification passed default equivalence, recovered elevated-bass level, `+12 dB` terminal margin, and program-like corpus checks. A four-excerpt CC0 music corpus remained unclipped at the persistent `-1.00 dB` host limiter threshold; its dense electronic passage reached `-0.443 dBFS` at default controls and is retained as limiter involvement already present in the `.8` comparison.

The `.10` baseline was accepted after scoped real-host qualification and
device listening against `.9`. It reduced affected-band side-to-mid balance
by an average `0.888 dB` over four registered CC0 excerpts, with no clipped
candidate samples and a highest measured peak of `-0.586 dBFS`.

## Sliders

| Slider | Default | Range | Purpose |
|---|---:|---:|---|
| `slider1` | 4 dB | -12 to 12 dB | Sub harmonic blend gain |
| `slider2` | 135% | 0 to 200% | Global side width multiplier |
| `slider3` | 50% | 0 to 100% | Loudness-contingent exciter sensitivity |
| `slider5` | 126% | 0 to 200% | Low-mid width multiplier |
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
scripts/validate_axiom_static.sh src/axiom_binaural_dsp_v4.1.4.10.eel
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

`scripts/run_jdsp_accepted_stress.py` characterizes the selected accepted baseline at the tracked `-1.00 dB` host threshold before another DSP candidate is justified. It repeats each registered external excerpt, rejects clipped or unusable level profiles, and records stable peaks above `-0.50 dBFS` as existing limiter-pressure behavior rather than retroactively failing the accepted listening baseline. New investigations use accepted `.10`; the `.8` and `.9` artifacts remain the evidence that justified the current reserve and spatial defaults.

`scripts/run_jdsp_sub_slider_map.py` expands that measurement across temporary fixtures based on the selected accepted script whose only difference is the `Sub Harmonics Gain` default. Its default grid of `+4`, `+6`, `+8`, `+10`, and `+12 dB` establishes whether real program material remains unclipped as user bass gain rises. A failure at the accepted `+4 dB` default rejects the baseline measurement; clipping found only at elevated settings records an operating-range boundary and supplies evidence for deciding whether a later bass-reserve revision is worthwhile. The original `.8` map exposed repeatable RMS retreat and led to `.9`; future maps start from `.10`, which inherits the accepted `.9` reserve law.

`scripts/run_jdsp_reserve_law_screen.py` evaluates that tradeoff before any versioned DSP edit. At a practical elevated `+8 dB` slider setting, it creates external fixtures whose conditional reserve slope is reduced from the accepted `1.000 dB` attenuation per added slider dB to candidate slopes `0.875`, `0.750`, and `0.500`. It runs one excluded conditioning render before measuring each fixture/excerpt set, then screens critical dense excerpts using repeated real-host captures and rejects a slope that clips or crosses `-0.50 dBFS`. A slope must recover measurable RMS level on every screened excerpt before broader boundary qualification is justified; a passing focused screen is not listening acceptance or a production architecture change.

`scripts/run_jdsp_reserve_range_qualification.py` takes focused-screen survivors through full registered-material coverage before any listening candidate is created. It starts at `+12 dB` Sub Harmonics Gain and descends through `+10`, `+8`, and `+6 dB`, rejecting and stopping a slope at the first clipped or above-boundary result. An unstable scalar measurement receives one fresh conditioned retry before it fails the qualification as unusable evidence. This ordering minimizes unnecessary live-host renders while preserving the actual full-range eligibility decision.

Qualify measurement repeatability before relying on fine differences. `scripts/qualify_jdsp_repeatability.py` accepts three or more captures of one script/stimulus/configuration and recommends five for decision-grade reports. It rejects invalid stereo PCM, frame mismatch, silence, clipping, caller-excessive level spread, and low-confidence alignment. Its optional jitter value is relative content-alignment spread only; it is not an absolute latency measurement. Variance and confidence limits must be supplied by the caller until repeated host measurements provide a defensible tolerance policy.

Use `scripts/analyze_jdsp_transfer.py` only with low-level deterministic stimuli and processed-output WAVs. Since capture occurs after JDSP host processing, its result is a stimulus-conditioned `end_to_end_host_path` measurement, not an Axiom-only transfer function. A report is unqualified when processed output is silent, clipped, or above the default `-6.0 dBFS` ceiling intended to avoid terminal-limiter involvement.

The transfer report retains timing against the known stimulus playback timeline without correlation alignment. When `--capture-pre-roll-ms` is supplied, it represents a known intentional lead-in in that timeline, not measured host latency. A pure mono probe identifies `M->M` and `M->S`; a pure side-only probe identifies `S->M` and `S->S`. General stereo material energizes both input components and cannot identify an individual transfer-matrix column from a single render, so those matrix values are deliberately invalidated.

`scripts/analyze_audio_perceptual_metrics.py` adds an offline perceptual-proxy layer for any stereo PCM WAV capture without touching JDSP. It reports ungated loudness proxy, combined RMS and crest behavior, cubic-oversampled true-peak proxy, 20 ms envelope percentiles, transient contrast, mid/side balance, left/right correlation, and ERB-like band metrics from sub-bass through air. These are engineering metrics for A/B direction and regression screening; they are not certified BS.1770 LUFS, certified true peak, or a psychoacoustic preference model. Generated reports stay outside git unless their findings are summarized in a public decision record. See `docs/perceptual-metrics.md`.

`scripts/run_jdsp_stft_audit.py` creates temporary fixtures from accepted `.9` at `0%` and accepted `50%` suppression. With mono probes, each diagnostic fixture routes its pre-STFT path to one output channel and its processed STFT path to the other in the same real-JDSP render. `unity_round_trip` exposes STFT analysis/resynthesis delay and residual behavior; `accepted_suppression` exposes the accepted suppression path against its simultaneous pre-STFT signal. Impulse captures are repeated three times by default and include peak-arrival, peak-level, short-window energy, and temporal-span metrics. The audit fails on mute or clipping only. Residual size is measurement evidence to assess before any production-path change.

The completed `.9` STFT audit measured approximately `11.6 ms` of same-render STFT path delay. The unity round trip produced a measurable sweep residual, and accepted suppression increased that sweep difference while leaving bass-burst behavior effectively unchanged. Across three impulse renders, the largest temporal-energy-span change was one sample at `48 kHz`, with no meaningful local-energy loss that justifies bypass or retuning. See `docs/stft-audit-v4.1.4.9.md`.

`scripts/run_jdsp_stage_observability.py` creates temporary same-render tap
fixtures from accepted `.10` to compare `spatial_out -> bass_post` and
`reserve_pre -> reserve_post`. The completed `.10` run confirmed additive bass
behavior before reserve and exact `-1.000 dB` fixed reserve behavior at the
accepted `+4 dB` Sub Harmonics default. No bass or reserve candidate is
justified from that evidence; see `docs/stage-observability-v4.1.4.10.md`.

`scripts/run_jdsp_width_mono_audit.py` measures accepted spatial-control behavior without creating a candidate. It creates a temporary fixture with `slider2`, `slider5`, and `slider6` fixed at `100%`, then renders low-level pure-mid and pure-side multitone probes through that fixture and through accepted `.9`. `M->S` and `S->M` transfer observations expose unintended center/side leakage; accepted-versus-unity `S->S` differences quantify widening by band. A pure-side signal is expected to disappear when downmixed to mono, so cancellation of intended side-only content is not a mono-compatibility fault.

`scripts/run_jdsp_width_material_screen.py` applies the same accepted-versus-unity-width comparison to registered local excerpts and reports side-to-mid RMS balance across deep-bass, upper-bass, low-mid, and high bands. Symmetrical `S` scaling does not change the mono sum; the material screen determines whether the crossover-transition widening is a meaningful stereo bass-image characteristic in actual program material before any taper candidate is considered.

The completed `.9` material screen found that accepted width increases `70-150 Hz` side balance by approximately `+5.0` to `+5.6 dB` relative to a temporary unity-width fixture, but remains no wider than the source material in that band across all four tested CC0 excerpts. This evidence does not justify a low-frequency side taper: it would further narrow an already controlled stereo bass image without establishing a defect. See `docs/width-mono-audit-v4.1.4.9.md`.

`scripts/run_jdsp_lowmid_width_screen.py` addresses the remaining spatial question before any `.10` proposal. It keeps accepted global and high-frequency width behavior fixed, then creates temporary `slider5 = 126%` and `slider5 = 115%` fixtures against accepted `140%`. With global width at `135%`, these correspond to low-mid side products of `1.701x`, `1.553x`, and accepted `1.890x`. It reports registered-material `S/M` balance separately across `150-300`, `300-800`, `800-2000`, and `2000-4000 Hz` so any listening candidate has a measured target in center focus, body, presence, or articulation.

The completed screen found accepted `.9` to be approximately `+5.3 dB` more side-forward than source material on average through `300 Hz-4 kHz` across all four CC0 excerpts. A restrained `slider5 = 126%` fixture reduced that emphasis by approximately `0.8` to `0.9 dB` without an integrity or terminal-pressure finding. A stronger `115%` reduction crossed the `-0.50 dBFS` observation boundary on dense electronic material. This supports one restrained listening candidate, not an automatic baseline replacement; see `docs/lowmid-width-screen-v4.1.4.9.md`.

For that narrowly scoped candidate, `scripts/run_jdsp_lowmid_width_candidate_qualification.py` replaces generic default-transparency qualification. A low-mid width change is deliberately not level-transparent on side-bearing content. The scoped runner allows only the version description and the two `slider5` default sites to change, then renders accepted-versus-candidate registered material through JDSP. It rejects silence, clipping, unscoped EEL differences, or absence of the expected reduced `S/M` balance in any affected band; terminal pressure remains an explicit investigation result. Human listening is still required for acceptance.

`scripts/run_jdsp_high_width_screen.py` begins the next spatial investigation from accepted `.10` without modifying it. It retains the accepted `slider6 = 110%` high-frequency width default and creates temporary `105%` and `100%` fixtures while preserving `.10` low-mid width. With global width at `135%`, these correspond to high-band side products of `1.485x`, `1.4175x`, and `1.350x`. Reports divide the affected region into `4-7`, `7-12`, and `12-18 kHz` bands so any later listening proposal is based on measured brilliance and air-band behavior rather than broad subjective retuning.

`scripts/run_jdsp_exciter_sensitivity_screen.py` starts the post-width
measurement pass on the dynamic exciter. It retains accepted `slider3 = 50%`
and creates temporary `35%` and `0%` fixtures while preserving all spatial,
bass, STFT, and output-reserve settings. Reports divide `4-18 kHz` into
presence-edge, brilliance, and air bands, measuring both band RMS and `S/M`
balance so the accepted clarity contribution can be separated from possible
harshness or terminal-pressure evidence before any listening candidate exists.
The completed registered-material screen found those temporary changes to be
effectively level-neutral on the high-energy corpus, so no reduced-exciter
candidate is justified from that evidence. A future exciter investigation
should use lower-level material designed to exercise the loudness-contingent
boost law.

`scripts/run_jdsp_exciter_probe_screen.py` supplies that first controlled
follow-up path. It generates deterministic quiet air-bearing, dull-control,
sibilance-texture, and louder air-control probes, then renders accepted `50%`,
reduced `35%`, and bypassed `0%` sensitivity through the same real-JDSP route.
This screen asks whether the accepted exciter is material-aware in the intended
direction: measurable on quiet air-bearing content, minimal on dull content,
and reduced on louder bright content. Its report includes explicit activation
and restraint checks so a future `.11` exciter decision can be based on probe
behavior rather than raw band tables alone.

The completed generated-probe screen confirmed that accepted `.10` adds
measurable `12-18 kHz` air on quiet air-bearing material and backs off on
louder bright material. After absolute band-RMS context was added, the
dull-control air delta was below the `-90 dBFS` decision floor and the small
reduced-vs-bypass ordering irregularity was inside the `0.20 dB` tolerance.
That supports the accepted exciter behavior, not an immediate candidate; see
`docs/exciter-probe-screen-v4.1.4.10.md`.

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

scripts/run_jdsp_stft_audit.py \
  src/axiom_binaural_dsp_v4.1.4.9.eel \
  /tmp/axiom-v49-stft-audit

scripts/run_jdsp_width_mono_audit.py \
  src/axiom_binaural_dsp_v4.1.4.9.eel \
  /tmp/axiom-v49-width-mono-audit

scripts/run_jdsp_width_material_screen.py \
  src/axiom_binaural_dsp_v4.1.4.9.eel \
  ~/.local/share/axiom-test-material/cc0-opengameart/axiom-external-cc0-manifest.json \
  /tmp/axiom-v49-width-material-screen

scripts/run_jdsp_lowmid_width_screen.py \
  src/axiom_binaural_dsp_v4.1.4.9.eel \
  ~/.local/share/axiom-test-material/cc0-opengameart/axiom-external-cc0-manifest.json \
  /tmp/axiom-v49-lowmid-width-screen

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
scripts/hot_reload_liveprog.sh src/axiom_binaural_dsp_v4.1.4.10.eel Axiom-v4.1.4.10-accepted
```

## Engineering Constraints

- Do not assign to `$pi`, `$e`, or `$eps`.
- Do not use `%`; wrap indices with explicit comparisons.
- Do not use `FractionalDelayLineInit`, `pfb_init`, or `InitPolyphaseFilterbank`.
- Keep final executable lines of `@sample` as `spl0 = out_L;` and `spl1 = out_R;`.
- Use flat pointer arithmetic for memory blocks and never overlap allocations.
