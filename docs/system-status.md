# Axiom System Status

Last updated: 2026-07-10

This is the short dashboard for the Axiom repo. Start here when choosing work,
then use `../AXIOM.md` for the plain-language system intent and
`dsp-change-workflow.md` for DSP change flow.

## Current State

| Item | Value |
| --- | --- |
| Accepted baseline | `Axiom Clean R011` |
| Accepted script | `src/axiom_binaural_dsp_v4.1.4.11.eel` |
| Accepted SHA-256 | `ad7dd7b33f2e62ff03ae08d7101c7ac333d707baef26b952806990ad979b0b0e` |
| Active candidate | `Axiom Clean R012` |
| Candidate script | `src/axiom_clean_r012.eel` |
| Candidate SHA-256 | `774e3d601b471f98b1818ee4ba424abf9e71a494f4a5a228d45c3d6af3ce070d` |
| Candidate status | `active_unqualified_listening_candidate` |
| Candidate static validation | `passed` |
| Candidate qualification plan | `complete` |
| Candidate qualification execution | `pending` |
| Candidate listening | `pending` |
| Candidate promotion | `not_approved` |
| Runtime target | JamesDSP / JDSP4Linux EEL2 Liveprog |
| Host limiter | enabled, `-1.00 dB` threshold, `60 ms` release, `0 dB` postgain |

`v4.1.4.11` remains the accepted listening baseline. It keeps the `.10`
restrained low-mid width baseline and changes only the elevated-bass reserve
slope above the default `+4 dB` Sub Harmonics setting from `0.750 dB/dB` to
`0.500 dB/dB`.

## Active Direction

The current project direction is simplification and clarity:

- make the main repo the source of truth for Axiom system knowledge;
- keep external folders as local runtime/workspace support unless a file is
  intentionally brought into the repo;
- keep active guidance short and actionable;
- archive old reviews, plans, and Labs notes when they are historical rather
  than current instructions;
- return DSP work to natural-language sound goals, one controlled hypothesis at
  a time.

The owner authorized R012 candidate creation. The file exists and passes static
validation. Qualification planning is complete; qualification execution and
listening remain pending; promotion and accepted baseline replacement are not
approved. `axiom-state.json` is authoritative.

## Active Candidate

`Axiom Clean R012` is the active unqualified listening candidate:

```text
src/axiom_clean_r012.eel
```

Its scoped changes are global side-width default normalization from `135%` to
`100%` and interpolated generated-sub saturation arithmetic. It is not
qualified, listening-accepted, promoted, or accepted. Do not modify its DSP
while state reconciliation or qualification planning is in progress.

## Current DSP Inputs

The `experimental03` work produced two Labs-supported ingredients:

- lower default width relative to accepted `.11`;
- modified bass-harmonic/saturation arithmetic.

Those ingredients are useful input, not accepted behavior. The detailed records
are now archived under `archive/labs/`. They are provenance for the existing
R012 candidate, not active Labs work. The next action is qualification planning,
not another sound-changing step.

## Current Signal Chain

```text
Input
  -> DC protection
  -> low-mid/high-band mid-side width shaping
  -> additive bass harmonic enhancement
  -> level-dependent high-frequency exciter
  -> STFT resonance suppression
  -> fixed -1 dB output reserve plus conditional bass-aware reserve
  -> JDSP terminal limiter (host)
  -> Output
```

Crossfeed is host-owned. Enable JamesDSP crossfeed manually for headphone
playback when wanted; do not add an internal crossfeed path to the accepted
Axiom script without a separate approved candidate.

## Current Open Investigation

None requiring active implementation.

The completed `.11` Sub Harmonics follow-up remains a historical watch item.
The active work boundary is review of `qualification-r012-plan.md`; R011 remains
accepted unless R012 later passes qualification, receives explicit owner
listening acceptance, and completes the separate promotion gate.

## Repo Boundaries

| Area | Current Role |
| --- | --- |
| `AXIOM.md` | Plain-language front door and system intent |
| `src/` | Accepted and historical EEL scripts |
| `src/labs/` | Non-authoritative DSP fixtures |
| `docs/` | Active architecture, workflow, qualification, and knowledge docs |
| `docs/archive/` | Historical reviews, Labs notes, planning docs, and local maps |
| `docs/knowledge/` | Repo-safe source notes and concept notes |
| `tools/axiom-codex/` | Helper CLI, task state, guardrails, and review tooling |
| `tools/axiom-team/` | Pi/qualification harness |

Local-only captures, private source material, generated evidence bundles, and
runtime controller state must stay outside the repo unless a sanitized summary
is intentionally added.

## Agentic Layer

The Agentic Layer is usable as a repository workflow layer, but should now serve
the simplified Axiom process instead of driving complexity for its own sake.

Current stable helper commands:

```bash
python3 tools/axiom-codex/axiom_codex.py status-summary
python3 tools/axiom-codex/axiom_codex.py task-state
python3 tools/axiom-codex/axiom_codex.py next-action
python3 tools/axiom-codex/axiom_codex.py guard-check
python3 tools/axiom-codex/axiom_codex.py ready-check
```

Subagents and advisory LLMs are optional support. They do not own candidate
approval, release decisions, accepted-baseline changes, or real-JDSP evidence.

## Native Windows Listening Host

The Axiom JamesDSP Controller lives outside this repo in the local
`JamesDSP4Windows_Decluttered/AxiomConsoleHarness` workspace. It is a Windows
WASAPI host for listening and testing Axiom through JamesDSP. It does not
change the accepted Axiom EEL baseline.

Known controller status:

- VB-CABLE route to physical output works;
- Axiom EEL and test EEL scripts can be loaded and heard;
- routing/recovery, tray/startup, telemetry, packaging, and soak tooling have
  been developed locally;
- full external distribution still needs trusted signing and a final
  power-stable overnight installed gate.

## Best Next Actions

1. Review and approve `qualification-r012-plan.md`.
2. After approval, run serialized technical qualification against accepted
   R011 without changing either DSP file.
3. Do not begin listening acceptance, promotion, or R013 work during technical
   qualification.
4. Prefer moving stale docs into `docs/archive/` over adding another competing
   system explanation.

## Refresh Commands

Use these commands when updating this dashboard:

```bash
git status -sb
python3 tools/axiom-codex/axiom_codex.py task-state
python3 tools/axiom-codex/axiom_codex.py next-action --json
python3 tools/axiom-codex/axiom_codex.py guard-check
python3 tools/axiom-codex/axiom_codex.py ready-check
scripts/validate_axiom_static.sh src/axiom_binaural_dsp_v4.1.4.11.eel
```
