# Axiom Clean R012 Qualification Plan

Date: 2026-07-10
Status: Plan complete; technical execution result is recorded in `qualification-r012.md`

This plan prepares controlled technical qualification. The execution record is
`qualification-r012.md`; neither document grants listening acceptance or
promotion approval.
`../axiom-state.json` remains the operational state authority.

## Identity

| Role | Label and path | SHA-256 | State |
| --- | --- | --- | --- |
| Accepted comparison (A) | `Axiom Clean R011` / `src/axiom_binaural_dsp_v4.1.4.11.eel` | `ad7dd7b33f2e62ff03ae08d7101c7ac333d707baef26b952806990ad979b0b0e` | accepted |
| Width-only control (B) | `src/labs/axiom_binaural_dsp_v4.1.4.11_width_profile_lab.eel` | `2e8e192200701cfe49b5cc0cc5046395eb67c76ec4b2fffc64de635d6abe50c9` | Labs-supported control; not a candidate |
| Candidate (C) | `Axiom Clean R012` / `src/axiom_clean_r012.eel` | `774e3d601b471f98b1818ee4ba424abf9e71a494f4a5a228d45c3d6af3ce070d` | active and unqualified |

R012 inherits R011 and changes only:

- global side-width default normalization from `135%` to `100%`;
- interpolated nonlinear saturation of the generated-sub signal, averaging the
  saturated midpoint and current sample before the harmonic high-pass path.

The bass change is interpolation/smoothing around the existing nonlinear
operation. It is not claimed as a complete oversampled processing path.

The project owner controls listening acceptance and promotion. Measurements may
make R012 eligible for listening or require investigation; they cannot accept
or promote it.

## A/B/C Comparisons

| Comparison | Isolated question |
| --- | --- |
| A versus B | Does the `135% -> 100%` global-width default improve coherence without unacceptable image or depth loss? |
| B versus C | What does interpolated saturation change when width is already held at `100%`? |
| A versus C | Is the complete R012 candidate technically safe and suitable for owner listening against accepted R011? |

Use the existing B fixture. Do not create another DSP fixture for this plan.
Every report must identify A, B, and C by path and hash.

## Host Record

Record this before each capture or listening pass:

- JamesDSP/JDSP application and engine version;
- sample rate and sample format;
- audio route and endpoint;
- device class: speakers, wired headphones/IEMs, USB DAC, Bluetooth, or other;
- terminal limiter enabled state, threshold, release, and postgain;
- crossfeed state and settings;
- every other host module and whether it is enabled;
- EEL path/hash actually loaded;
- material or deterministic-stimulus identifier;
- capture repetition and timestamp.

The qualified host reference is limiter enabled, `-1.00 dB` threshold, `60 ms`
release, `0 dB` postgain, and crossfeed disabled. Other JDSP effects remain
disabled for technical A/B/C comparison.

Crossfeed-off and crossfeed-on listening are separate recorded passes. Do not
mix their observations or treat crossfeed-on results as technical equivalence
to the crossfeed-off baseline.

## Test Matrix

Run each technically supported rate as its own capture group:

| Dimension | Required coverage |
| --- | --- |
| Sample rate | `44.1 kHz`, `48 kHz`, `96 kHz` |
| Sub Harmonics | `+4`, `+6`, `+8`, `+10`, `+12 dB`, where the real host and material route are technically practical |
| Program classes | normal musical; dense electronic; hip-hop/trap-sub; vocal/acoustic; strongly stereo; mono |
| Deterministic bass | bass-focused probes and transient kick-and-bass stimuli |
| Comparisons | A/B, B/C, and A/C as defined above |
| Repetition | enough repeated renders to apply the existing stability qualifier; use the same count within a comparison group |

Use generated corpus material plus local manifests or sanitized material
descriptions. Do not commit copyrighted program material, private paths,
decoded excerpts, captures, or raw reports.

If the real host cannot operate reliably at one required rate or elevated-bass
setting, record the exact limitation and continue only with an explicitly
incomplete matrix. Do not substitute a resampled capture and label it as a
native-rate result.

## Measurements

Collect or review for each valid capture:

- sample peak and clipped-sample count;
- RMS/loudness delta for A/B, B/C, and A/C;
- limiter participation or gain reduction, when host telemetry exposes it;
- limiter active-time percentage, when observable;
- left/right level balance and correlation;
- mid/side energy in sub-bass, bass, low-mid, mid, presence, brilliance, and
  air bands where the sample rate supports the band;
- low-frequency mono compatibility;
- repeated-render peak, RMS, alignment, and correlation stability;
- format, frame-count, sample-rate, silence/mute, and invalid-capture checks.

Zero clipped output samples are necessary but do not prove limiter pressure is
unchanged. Near-ceiling peaks, RMS retreat, waveform/envelope changes, and any
available limiter telemetry must be interpreted together.

## Focused Saturation Analysis

Compare A and C with identical deterministic low-frequency input and host
settings:

- `40 Hz`, `60 Hz`, `80 Hz`, and `90 Hz` sine;
- a two-tone bass stimulus;
- a decaying kick-like sine;
- a short bass transient.

At minimum measure output level, peak, repeatability, transient response, and
resolved generated harmonics. Where the current capture and spectral tools can
support defensible estimates, also evaluate THD, alias products, and phase
relationship of the generated branch.

Current limitations must be explicit:

- `analyze_axiom_subharmonics.py` models the older single-sample saturator and
  does not yet model R012 interpolation;
- the normal host capture exposes full output, not an isolated generated-branch
  tap, so branch phase and branch-only THD require a diagnostic method that
  does not change A or C;
- the repository has no accepted alias-product or THD qualification threshold;
- limiter gain reduction and active-time telemetry depend on host observability
  and may be unavailable;
- proxy true-peak and perceptual metrics are supporting context, not certified
  meters or listening evidence.

Unavailable measurements are recorded as limitations. Do not infer or invent
values.

## Existing Capabilities

Use these existing paths where applicable:

- `scripts/validate_axiom_static.sh` plus
  `scripts/validate_axiom_r012_candidate.py` for EEL safety and candidate scope;
- `scripts/generate_jdsp_stimuli.py` and
  `scripts/generate_axiom_program_corpus.py` for deterministic material;
- `scripts/render_jdsp_host.py` and `scripts/run_jdsp_wsl_qualification.py` for
  serialized real-host rendering and baseline/candidate qualification;
- `scripts/compare_jdsp_captures.py` for integrity, peak/RMS, clipping,
  left/right, and broad mid/side comparison;
- `scripts/qualify_jdsp_repeatability.py` for repeated-capture validity,
  alignment, spread, and silence rejection;
- `scripts/analyze_jdsp_transfer.py` for identifiable transfer and phase data;
- `scripts/analyze_audio_perceptual_metrics.py` for banded mid/side and
  supporting transient/loudness proxies;
- `scripts/run_jdsp_local_material.py` for private manifest material without
  importing source audio.

All real-JDSP capture work remains serialized.

## Listening Questions

For later owner listening, ask in plain language:

- Does the vocal center stay fixed and believable?
- Is stereo placement more coherent, and is useful width or depth lost?
- Does the image move or become unstable?
- Does the kick stay centered, located, and impactful?
- Is bass fuller, or does it become blurred, fuzzy, smeared, or detached?
- Does the bass image remain anchored and compatible in mono?
- Do cymbals or upper mids become tiring?
- Is there audible loudness retreat at elevated Sub Harmonics settings?
- Is there obvious pumping or limiter involvement?

Record crossfeed-off and crossfeed-on answers separately.

## Decision Rules

| Outcome | Rule |
| --- | --- |
| Proceed to listening | Required captures are valid and repeatable; no unexplained normal-material clipping, channel imbalance, mono regression, instability, or unsafe terminal-pressure result remains. |
| Investigation required | A result is repeatable but its source or significance is unresolved, limiter pressure may have regressed, or a required observable is missing. |
| Reject candidate | A repeatable candidate-specific safety, integrity, severe mono/spatial, or unacceptable terminal-pressure regression is established. |
| Needs retest | Route, host state, capture validity, repetition, or matrix coverage is insufficient for a decision. |
| Technically safe but no audible decision | Technical gates permit listening, but results do not establish audible preference; keep R011 accepted pending owner comparison. |
| Accept after explicit owner listening decision | Only after technical eligibility and an explicit owner decision. Acceptance still does not itself update policy or complete promotion. |

R012 is never promoted automatically from measurements. Accepted-baseline
promotion remains a separate explicitly approved release action.

## Excluded Scope

Fleet material is not part of R012 qualification. Do not import or evaluate the
Fleet agent package, configuration, `v4.1.4.13` EEL, width curve, centered bass
source, exciter-cap change, or STFT threshold change. Do not create R013.

## Execution Gate

Before real-host execution:

1. review and approve this plan;
2. confirm A/B/C paths and hashes still match;
3. confirm the host record and local material manifest are ready;
4. select a serialized output location outside the repository;
5. run static and state consistency checks again.

Stop here until that execution gate is approved.
