# Axiom Current State

Last updated: 2026-06-02

## Accepted Baseline

| Item | Value |
| --- | --- |
| Human-facing label | `Axiom Clean R011` |
| Accepted version | `v4.1.4.11` |
| Accepted script | `src/axiom_binaural_dsp_v4.1.4.11.eel` |
| SHA-256 | `ad7dd7b33f2e62ff03ae08d7101c7ac333d707baef26b952806990ad979b0b0e` |
| Qualification record | `docs/qualification-v4.1.4.11.md` |
| Policy anchor | `tools/axiom-team/policy.json` |

`v4.1.4.11` is the current accepted listening baseline. It keeps the `.10`
low-mid width setting and reduces only the elevated-bass reserve slope above
the default `+4 dB` Sub Harmonics setting from `0.750 dB/dB` to
`0.500 dB/dB`. `v4.1.4.10` remains the previous accepted reference.

For future EEL iterations, use the readable `Axiom Clean R012+` naming scheme
instead of extending the confusing `v4.1.4.x` sequence. See
`docs/versioning-and-naming.md`.

## Active Listening Candidate

None. The next sound-changing version should not be created until a new scoped
hypothesis has measurement support and a defined listening target.

## Host Baseline

| Host setting | Value |
| --- | --- |
| JDSP master processing | enabled |
| Master limiter threshold | `-1.00 dB` |
| Master limiter release | `60 ms` |
| Master postgain | `0 dB` |
| Crossfeed during qualification | disabled |

JamesDSP crossfeed may be enabled manually for headphone listening, but it is
not part of the measured Axiom comparison baseline. Axiom does not own an
internal crossfeed or internal limiter stage.

## Product Boundary

- **Axiom Clean** is the only accepted product baseline.
- **Axiom Lab** is where temporary fixtures, analysis tools, stage taps,
  metrics, corpus work, and analog-color research belong.
- **Axiom Color** is future-only and must not become public without separate
  evidence, qualification, listening acceptance, and maintenance ownership.
- Historical `.eel` files are preserved. Sound-changing work creates a new
  versioned script instead of editing an accepted or historical script.
- Future Axiom Clean candidates should use `Axiom Clean R012`, `Axiom Clean
  R013`, and matching `src/axiom_clean_r012.eel` style filenames unless a later
  approved naming policy replaces this rule.

## Public Repo State

Tracked public project state belongs in:

- `src/` for versioned EEL scripts;
- `scripts/` and `tests/` for analysis and verification tooling;
- `docs/` for architecture, qualification records, roadmap, and public
  engineering notes, with `docs/README.md` as the documentation index;
- `tools/axiom-team/` for the controlled Pi engineering harness;
- `presets/` for JDSP preset templates.

Do not commit captured audio, private music, local manifests, credentials,
generated run folders, or device-specific test outputs.

`docs/axiom-notes.html` is a local planning workspace because it can contain
machine-specific paths, private library notes, and working conversation
context. Keep it out of public git unless it is explicitly sanitized first.
The public roadmap derived from that workspace is `docs/axiom-roadmap.md`.

## Local And Private State

Expected local-only state includes:

- `~/.config/jamesdsp/liveprog/` for Liveprog script deployment;
- `~/.config/axiom-engineering/` for harness configuration;
- `~/.local/state/axiom-engineering/` for run records, worktrees, and Pi
  session logs;
- `~/.local/share/axiom-test-material/` for locally registered test material;
- `/tmp` or another local output folder for generated captures and reports.

Google Drive copies are user-managed distribution convenience for testing
devices. The Git repository and `tools/axiom-team/policy.json` remain the
source of truth.

## Next Roadmap Step

Follow `docs/axiom-roadmap.md`, using the `.11` accepted baseline as the new
anchor for any future measurement or candidate decision. The current decision
record is `docs/architecture-decision-v4.1.4.10.md`.
Use `docs/tool-inventory.md` before choosing measurement or harness commands.
Use `docs/bass-host-limiter-investigation-plan.md` before any elevated
bass/reserve or host-limiter candidate work. The `.10` bass/reserve stage
capture is recorded in `docs/stage-observability-v4.1.4.10.md`; it supported
the default path rather than an immediate low-end candidate.
The generated low-level exciter probe screen is recorded in
`docs/exciter-probe-screen-v4.1.4.10.md`; floor-aware evaluation supported the
inherited exciter behavior rather than an immediate exciter candidate. The
accepted-setting dense-material stress baseline is recorded in
`docs/accepted-stress-v4.1.4.10.md`; normal material passed integrity and the
remaining observations are host-contract pressure on one dense electronic
excerpt plus expected flawed-source clipping evidence. Scoped Sub Harmonics
slider maps are recorded in `docs/sub-harmonics-map-v4.1.4.10.md`; dense
electronic and hip-hop/trap-sub material stayed unclipped through `+12 dB` but
showed repeatable RMS retreat at elevated bass settings. The focused `.10`
reserve-law screen is recorded in
`docs/reserve-law-screen-v4.1.4.10.md`; a temporary `0.500 dB/dB` elevated-bass
reserve slope recovered meaningful RMS on dense electronic and hip-hop/trap-sub
material, remained safe across `+6` through `+12 dB` for those scoped stress
classes, survived full-manifest range qualification across 14 registered items
with no normal-material clipped samples, and was accepted as `v4.1.4.11` after
listening against `.10`. The
first standalone perceptual-proxy analyzer is recorded in
`docs/perceptual-metrics.md` and is wired into A/B, corpus, private
local-material, and scoped candidate reports as evidence context. Structured
human listening records are defined in `docs/listening-records.md`; full
records should remain local unless sanitized. Corpus material taxonomy and
manifest validation are defined in `docs/corpus-material.md`. Android
validation package generation and RootlessJamesDSP phone-side checks are defined
in `docs/android-validation.md`. Local level-matched A/B listening packages are
defined in `docs/ab-listening-packages.md`. Device and route coverage is
defined in `docs/device-matrix.md`, Windows endpoint/default-render snapshots
are available through `scripts/audit_windows_audio_endpoints.py`, and local
route checklists are defined in `docs/device-readiness-packages.md`.
`scripts/hot_reload_liveprog.sh` restores `master_limthreshold=-1.0` after
JDSP preset saves because the host currently rewrites that setting to `0`.
Candidate readiness is defined in `docs/candidate-readiness.md` and checks the
accepted baseline hash, strict corpus metadata, and strict device matrix before
any new sound-changing EEL file is justified. The local corpus currently
strict-passes coverage. Android, WSL lab, speaker, wired/USB, and Bluetooth
route setup evidence are complete locally; wired/USB and Bluetooth are recorded
as user-attested physical route evidence rather than automated endpoint-capture
evidence. The candidate-readiness gate should be rerun against `.11` before any
new sound-changing candidate. The next candidate requires a scoped hypothesis,
measured target, edit boundary, and listening target.
