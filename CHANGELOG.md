# Changelog

All notable changes to Axiom Binaural DSP are documented in this file.

---

## [Unreleased] - Agentic Layer Hardening

### Added
- Added `agentic-audit` to validate command registry/runtime mappings, native
  aliases, JDSP approval metadata, agent profile contracts, and skill-eval
  fixture schemas.
- Added validated `agent-review` records with JSON/file output, role-source
  links, decision enums, and explicit evidence boundaries.
- Added `next-action --include-maintenance` so ongoing Agentic hardening can
  intentionally select initial-maintenance tasks without changing default
  conservative planning.
- Added adversarial regression coverage for malformed Agentic Layer metadata.

### Changed
- Made `ready-check` consume the strict Agentic contract validators instead of
  checking only whether registry, profile, and fixture files exist.
- Replaced the free-form multi-role review scaffold with a schema-validated
  draft record that can still render as Markdown for human review.

---

## [4.1.4.11] - 2026-06-01 - Accepted Reduced Elevated-Bass Reserve Baseline

### Changed
- Preserved the accepted `.10` processing chain, restrained low-mid width,
  host-output policy, crossfeed ownership, exciter behavior, and STFT behavior.
- Reduced only the elevated-bass terminal reserve slope above the default
  `+4 dB` Sub Harmonics setting from `0.750 dB/dB` to `0.500 dB/dB`.

### Rationale
- Full-manifest reserve-law qualification showed the `0.500 dB/dB` target
  recovered meaningful level on dense electronic and hip-hop/trap-sub material
  while preserving headroom across normal registered material.
- User listening tests against `v4.1.4.10` accepted `.11` as the better
  baseline.

### Validation
- Passed strict EEL static validation, Python unit tests, and Pi harness tests.
- Inherited the full-manifest temporary-fixture qualification: 14 registered
  material items across `+12`, `+10`, `+8`, and `+6 dB`, with no
  normal-material clipped samples.
- Promoted `tools/axiom-team/policy.json` to the `.11` SHA-256 anchor.

---

## [4.1.4.10] - 2026-05-26 - Accepted Restrained Low-Mid Width Baseline

### Changed
- Preserved the accepted `.9` processing chain, reduced bass-reserve law,
  high-frequency width, and host-output policy.
- Reduced the default `Low-Mid Width Multiplier` from `140%` to `126%`,
  moving its effective side product from `1.890x` to `1.701x`.
- Extended static validation to enforce inherited `.9` architectural
  invariants for the versioned `.10` candidate.

### Rationale
- Registered-material measurement identified consistent low-mid side emphasis
  in `.9`, especially through `300 Hz-4 kHz`.
- The restrained setting reduced measured affected-band side balance by an
  average `0.888 dB` relative to `.9` without advancing the more aggressive
  alternative that showed higher terminal pressure.

### Validation
- Passed strict EEL static validation and the Python and Pi harness test suites.
- Passed scoped real-JDSP qualification on four registered CC0 excerpts with
  zero clipped candidate samples and a highest peak of `-0.586 dBFS`.
- Accepted after device listening against `v4.1.4.9`.

---

## [4.1.4.9] - 2026-05-26 - Accepted Reduced Bass-Reserve Baseline

### Changed
- Preserved the accepted `.8` signal chain and exact default Sub Harmonics behavior.
- Reduced the conditional terminal reserve above the `+4 dB` default from
  `1.000 dB/dB` to `0.750 dB/dB`.
- Removed the now-unused full-reserve baseline state from the output stage.

### Rationale
- Real-host external-material screening identified `0.750 dB/dB` as the
  strongest reduced-reserve slope to pass every tested `+6`, `+8`, `+10`,
  and `+12 dB` setting without clipping.
- A more aggressive `0.500 dB/dB` slope exceeded the observation boundary on
  dense electronic material at `+6 dB`, so it is not used for listening.

### Validation
- Passed managed real-JDSP qualification with an investigation marker: the
  external electronic excerpt approached the observation ceiling at default
  controls under both `.8` and `.9`, with zero clipped samples.
- Accepted after device A/B listening against `v4.1.4.8` confirmed the
  reduced-reserve behavior should become the new baseline.

---

## [4.1.4.8] - 2026-05-24 - Accepted Bass-Aware Headroom Baseline

### Changed
- Preserved the `v4.1.4.7` signal chain and exact default Sub Harmonics behavior.
- Added conditional output reserve only when `Sub Harmonics Gain` is raised above its `+4 dB` default.
- Extended sub-harmonics characterization to model the baseline's bass-aware reserve.
- Established JDSP master processing at `-1.00 dB` limiter threshold, `60 ms`
  release, and `0 dB` postgain as the accepted host-owned terminal stage.

### Rationale
- Branch-local nonlinear analysis showed increasing headroom pressure for high bass-gain settings near the 90 Hz extraction boundary.
- The baseline preserves the requested bass ratio and trades total output level for reduced limiter pressure rather than compressing or retuning the bass timbre.

### Validation
- Passed the managed real-JDSP WSL qualification at a persistent `-1.00 dB`
  terminal-limiter threshold: default transparency, elevated-bass reserve,
  maximum-boundary margin, and generated program-corpus checks passed.
- Checked four externally stored CC0 high-energy music excerpts through the
  real host path with zero clipped candidate samples. The densest electronic
  excerpt reached `-0.474 dBFS` and remains documented as terminal-limiter
  involvement rather than concealed by further script attenuation.
- Accepted after device listening confirmed the `.8` result across multiple
  songs without an audible issue.

---

## [Unreleased] - Measurement Qualification Expansion

### Added
- Added an Airwindows Knowledge intake workflow with repo-safe provenance,
  clean-room concept taxonomy, and a local-only metadata index helper for
  source IDs, effect names, tags, relative upstream paths, and pinned commits.
- Canonicalized Airwindows indexing to one schema-v2 record per effect and
  added an audit command for metadata safety, duplicate detection, and checkout
  commit drift.
- Added a pre-candidate high-frequency width screen for accepted `.10` that
  compares temporary `slider6` alternatives across presence-edge, brilliance,
  and air bands without modifying the accepted baseline.
- Recorded that the completed `.10` high-width screen does not justify a new
  DSP candidate: restrained width reduced measured side emphasis modestly and
  caused the only terminal observation on dense electronic material.
- Added a pre-candidate dynamic exciter sensitivity screen for accepted `.10`
  that compares temporary `slider3` alternatives across presence-edge,
  brilliance, and air bands without modifying the accepted baseline.
- Recorded that the completed registered-material exciter screen does not
  justify a new DSP candidate because reduced and bypassed sensitivity were
  effectively level-neutral on the high-energy corpus.
- Added an offline repeated-capture qualifier that rejects invalid, muted, clipped, unstable, or low-confidence real-host measurements before fine A/B interpretation.
- Added a stimulus-conditioned end-to-end host-path analyzer with low-level output qualification and identifiable mid/side transfer-matrix reporting.
- Added branch-local nonlinear characterization for the user-adjustable `Sub Harmonics Gain` path across bass tone levels and slider values.
- Added a sustained `90 Hz` pressure probe, deterministic program-like corpus,
  optional private-material manifest runner, and a managed WSL qualification
  runner that restores the prior audio route and limiter setting.
- Added deterministic unit tests for repeatability, clipping/silence rejection, retained known-timeline delay, and `M->S` / `S->M` leakage visibility.
- Added a serialized STFT stage audit that compares same-render pre-STFT and
  processed paths at unity and accepted suppression without modifying the
  accepted `.9` DSP source.
- Added a serialized width/mono audit that measures accepted `S->S` widening
  and unintended `M->S` / `S->M` leakage against a temporary unity-width
  fixture without changing the accepted `.9` script.
- Added a registered-material spatial-balance screen that measures
  band-specific side-to-mid behavior for accepted and temporary unity-width
  processing before any low-frequency taper candidate is considered.
- Added a pre-candidate low-mid width screen for restrained `slider5`
  alternatives, subdividing `150 Hz-4 kHz` material behavior before deciding
  whether a new listening iteration is warranted.
- Added a scoped real-JDSP qualification path for a versioned restrained
  low-mid width candidate, since an intentional spatial change must not be
  rejected by generic default-transparency gates.
- Added a project-owned Pi engineering harness with immutable-baseline checks,
  external candidate worktrees, restricted specialist consultations, serialized
  real-JDSP qualification, and explicit listening/publication/merge gates.
- Added a same-script JDSP limiter-threshold sweep that evaluates default `.8`
  limiter participation with repeated external-material captures before any
  new EEL candidate is justified.
- Added an accepted-setting dense-material stress gate that repeats registered
  external excerpts at the tracked `-1.00 dB` limiter setting and preserves
  stable terminal-limiter pressure as regression evidence for future candidates.
- Added a dense-material `Sub Harmonics Gain` map using temporary accepted-`.8`
  fixtures from `+4` through `+12 dB` to identify practical control-range
  boundaries before proposing a sound-changing DSP iteration.
- Added a focused experimental reserve-law screen that compares reduced
  elevated-bass output attenuation against the current `.8` reserve law using
  repeat-captured critical music excerpts before candidate creation, with an
  excluded conditioning render to prevent cold host initialization from
  contaminating measured level repeatability.
- Added a reduced-reserve range qualifier that screens focused-test survivors
  across all registered material and elevated bass settings, testing the
  highest-risk setting first, retrying unstable scalar evidence once, and
  stopping headroom-rejected slopes early.

### Measurement Boundary
- Captures occur after JDSP host processing and therefore do not prove an Axiom-only transfer function.
- Transfer measurements are qualified only below the default `-6.0 dBFS` processed-output ceiling and do not infer absolute host latency from caller-supplied pre-roll.

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

## Future Work Policy

The accepted `.9` chain is optimized before introducing additional DSP stages.
Any new audio behavior must be proposed against measurement evidence and device
listening. `FractionalDelayLineInit`, `pfb_init`, and
`InitPolyphaseFilterbank` remain excluded because they are not safe for the
target JDSP host.
