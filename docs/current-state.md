# Axiom Current State

Last updated: 2026-05-29

## Accepted Baseline

| Item | Value |
| --- | --- |
| Accepted version | `v4.1.4.10` |
| Accepted script | `src/axiom_binaural_dsp_v4.1.4.10.eel` |
| SHA-256 | `2b72288048f3e6a180eb5a0e3d951f34fc463d113bb8d716c03cfda8aeafffc5` |
| Qualification record | `docs/qualification-v4.1.4.10.md` |
| Policy anchor | `tools/axiom-team/policy.json` |

`v4.1.4.10` is the current accepted listening baseline. It keeps the `.9`
reduced bass-reserve behavior and reduces default `150 Hz-4 kHz` low-mid side
width from `1.890x` to `1.701x`.

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

## Public Repo State

Tracked public project state belongs in:

- `src/` for versioned EEL scripts;
- `scripts/` and `tests/` for analysis and verification tooling;
- `docs/` for architecture, qualification records, roadmap, and public
  engineering notes;
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

Follow `docs/axiom-roadmap.md`, continuing Phase 1 measurement foundation work.
Use `docs/tool-inventory.md` before choosing measurement or harness commands.
Use `docs/bass-host-limiter-investigation-plan.md` before any elevated
bass/reserve or host-limiter candidate work. The accepted `.10` bass/reserve
stage capture is recorded in `docs/stage-observability-v4.1.4.10.md`; it
supports the accepted default path rather than an immediate low-end candidate.
The generated low-level exciter probe screen is recorded in
`docs/exciter-probe-screen-v4.1.4.10.md`; floor-aware evaluation supports the
accepted `.10` exciter behavior rather than an immediate `.11` candidate. The
first standalone perceptual-proxy analyzer is recorded in
`docs/perceptual-metrics.md` and is wired into A/B, corpus, private
local-material, and scoped candidate reports as evidence context. Structured
human listening records are defined in `docs/listening-records.md`; full
records should remain local unless sanitized. Corpus material taxonomy and
manifest validation are defined in `docs/corpus-material.md`. Android
validation package generation and RootlessJamesDSP phone-side checks are defined
in `docs/android-validation.md`. Local level-matched A/B listening packages are
defined in `docs/ab-listening-packages.md`. The next sound-changing candidate
should wait until the corpus is populated with broader material coverage.
