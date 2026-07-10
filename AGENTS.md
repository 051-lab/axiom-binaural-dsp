# AGENTS.md - AI Agent Operating Instructions

> **axiom-binaural-dsp** | JamesDSP / JDSP4Linux EEL2 enhancement core

Read this file, `docs/architecture.md`, and `docs/JDSP4Linux_Knowledge_Base.md`
before changing EEL code or host configuration.

## Repository State

| Item | Detail |
|------|--------|
| Current accepted baseline | `src/axiom_binaural_dsp_v4.1.4.11.eel` |
| Human-facing baseline label | `Axiom Clean R011` |
| Active listening candidate | none |
| Runtime | JamesDSP / JDSP4Linux EEL2 Liveprog |
| Device policy | Speaker-neutral script; optional crossfeed belongs to the host |
| Limiter policy | No script limiter; JDSP terminal limiter owns peak control |
| Qualified host limiter | enabled, `-1.00 dB` threshold, `60 ms` release, `0 dB` postgain |

`v4.1.4.11` retains the `.10` restrained low-mid width baseline and changes
only the elevated-bass reserve slope above the accepted `+4 dB` Sub Harmonics
default from `0.750 dB/dB` to `0.500 dB/dB`. It was accepted after listening
against `v4.1.4.10`; `.10` remains the previous accepted reference.

Future Axiom Clean EEL iterations should use the `Axiom Clean R012+` release
label and matching `src/axiom_clean_r012.eel` style filenames. Preserve
historical `v4.1.4.x` files as evidence anchors; do not continue that sequence
for new sound-changing candidates. See `docs/versioning-and-naming.md`.

## Current Signal Chain

```text
Input
  -> DC protection
  -> bass harmonic enhancement
  -> low-mid/high-band mid-side width shaping
  -> level-dependent high-frequency exciter
  -> STFT resonance suppression
  -> fixed -1 dB output reserve plus conditional bass-aware reserve
  -> JDSP terminal limiter (host)
  -> Output
```

There is no internal crossfeed path in the accepted baseline. Enable JamesDSP
crossfeed manually for headphone playback only when wanted.

## Strict EEL2 / JDSP Constraints

- Never assign to `$pi`, `$e`, or `$eps`; they are read-only constants.
- Never use `FractionalDelayLineInit`, `pfb_init`, or
  `InitPolyphaseFilterbank`; these APIs are excluded for host stability.
- Never use the `%` modulo operator. Wrap indices explicitly:

```eel2
idx += 1;
idx >= max ? idx = 0;
```

- Use `this.*` only inside `function()` blocks for persistent DSP state.
- Declare function locals using `local(var1 var2 var3)`.
- Initialize all state and memory used by audio processing in `@init`.
- Use only the exact STFT API signatures documented in the knowledge base:
  `stftCheckMemoryRequirement`, `stftInit`, `stftForward`, and `stftBackward`.
- Allocate memory with monotonically advanced flat pointers; blocks must not overlap.
- The final two lines of `@sample` must be:

```eel2
spl0 = out_L;
spl1 = out_R;
```

## Editing Rules

1. Preserve historical `.eel` files. Create a new version for sound-changing DSP work.
2. Treat `src/axiom_binaural_dsp_v4.1.4.11.eel` as the accepted reference until a new version passes qualification and listening acceptance.
3. Keep JDSP host-only stages disabled during Axiom comparison, except the enabled terminal limiter documented above.
4. `presets/axiom-preset.conf` is a full JDSP `audio.conf`-style key/value template, not a slider JSON document.
5. Do not commit captured audio, third-party music, local manifests, or generated test reports. Keep those under `/tmp` or a local data directory.
6. Update `CHANGELOG.md` and relevant documentation with behavioral or qualification changes.
7. For coordinated Pi experimentation, use `scripts/axiom_team.sh`; its state,
   captures, worktrees, and local-material manifest remain outside this repository.

## Validation Workflow

Before accepting DSP behavior or testbench changes:

```bash
scripts/validate_axiom_static.sh src/axiom_binaural_dsp_v4.1.4.10.eel
scripts/validate_axiom_static.sh src/axiom_binaural_dsp_v4.1.4.11.eel
python3 -m unittest discover -s tests -p 'test_*.py'
```

To reproduce the historical `.8` versus `.9` reserve qualification:

```bash
scripts/run_jdsp_wsl_qualification.py \
  src/axiom_binaural_dsp_v4.1.4.8.eel \
  src/axiom_binaural_dsp_v4.1.4.9.eel \
  /tmp/axiom-v48-v49-wsl-qualification
```

The managed workflow applies and restores the selected limiter threshold once per
session. Use it for threshold-sensitive comparisons; standalone render scripts
assume the intended host configuration is already active.

## Documentation Map

| File | Purpose |
|------|---------|
| `AXIOM.md` | Plain-language front door for the Axiom system, current baseline, and agent behavior |
| `README.md` | User setup and testbench entry points |
| `docs/README.md` | Documentation index and category map |
| `docs/system-status.md` | Quick dashboard for accepted baseline, open investigations, and next work |
| `docs/dsp-change-workflow.md` | Plain-language workflow for turning listening goals into scoped DSP changes |
| `docs/archive/README.md` | Archive index for historical reviews, Labs notes, planning docs, and local maps |
| `docs/session-work-log.md` | Source log for session work summaries and generated PDF copies |
| `docs/current-state.md` | Current accepted baseline, host policy, and repo/local state boundary |
| `docs/architecture.md` | Active DSP architecture and host ownership |
| `docs/versioning-and-naming.md` | Future EEL release-label policy and legacy version-ID boundary |
| `docs/axiom-roadmap.md` | 90-day foundations-first roadmap |
| `docs/profile-matrix.md` | Profile status, ownership, allowed changes, and required tests |
| `docs/codex-operating-guide.md` | Codex responsibilities, prohibitions, branch discipline, and review flow |
| `docs/pi-runbooks.md` | Repeatable terminal missions for Pi/Codex sessions |
| `docs/labs-policy.md` | Branch, experiment, artifact, and promotion rules for Labs work |
| `docs/task-backlog.md` | Lightweight issue/task breakdown for workflow architecture |
| `docs/release-gates.md` | Publication, candidate, listening, and accepted-baseline promotion gates |
| `docs/listening-protocol.md` | Listening setup, material selection, comparison, and decision rules |
| `docs/tool-inventory.md` | Tool purpose, JDSP side effects, and artifact safety map |
| `docs/bass-host-limiter-investigation-plan.md` | Bass reserve and JDSP host-limiter investigation plan behind `.11` |
| `docs/accepted-stress-v4.1.4.10.md` | `.10` accepted-setting dense-material stress record |
| `docs/sub-harmonics-map-v4.1.4.10.md` | `.10` elevated Sub Harmonics control-range evidence |
| `docs/reserve-law-screen-v4.1.4.10.md` | `.10` reserve-law screen and full-manifest `0.500 dB/dB` qualification |
| `docs/stage-observability-plan.md` | Diagnostic stage-tap fixture and reporting plan |
| `docs/qualification-v4.1.4.8.md` | Previous `.8` evidence and reproduction record |
| `docs/qualification-v4.1.4.9.md` | Previous `.9` evidence and reproduction record |
| `docs/qualification-v4.1.4.10.md` | Previous accepted `.10` evidence and reproduction record |
| `docs/qualification-v4.1.4.11.md` | Accepted `.11` evidence and reproduction record |
| `docs/JDSP4Linux_Knowledge_Base.md` | EEL2/JDSP runtime and preset reference |
| `docs/engineering-harness.md` | Controlled Pi workflow, gates, and local-state policy |
| `CHANGELOG.md` | Version history and decision record |

Historical reviews, planning records, Labs notes, and local repository maps are
kept under `docs/archive/`. Treat archived files as evidence/history, not active
workflow instructions, unless a task explicitly promotes one back into current
guidance.

*Last updated: v4.1.4.11 accepted baseline - 2026-06-01*
