# Axiom System Status

Last updated: 2026-06-07

This is the quick-start dashboard for Codex, Pi sessions, and future agents.
Read this before choosing new work. It summarizes the current accepted line,
active investigations, operating-system state, and the next recommended
tasks.

## Accepted Baseline

| Item | Value |
| --- | --- |
| Accepted version | `v4.1.4.11` |
| Accepted script | `src/axiom_binaural_dsp_v4.1.4.11.eel` |
| SHA-256 | `ad7dd7b33f2e62ff03ae08d7101c7ac333d707baef26b952806990ad979b0b0e` |
| Qualification record | `qualification-v4.1.4.11.md` |
| Policy anchor | `../tools/axiom-team/policy.json` |

`v4.1.4.11` is the current accepted listening baseline. It keeps the `.10`
restrained low-mid width baseline and changes only the elevated-bass reserve
slope above the default `+4 dB` Sub Harmonics setting from `0.750 dB/dB` to
`0.500 dB/dB`.

## Active Candidate

None.

No sound-changing `.12` or v5 candidate should be created until the candidate
readiness gate passes and a new scoped hypothesis has measurement support.

## Host Baseline

| Host Setting | Accepted Qualification Value |
| --- | --- |
| JDSP master processing | enabled |
| Master limiter threshold | `-1.00 dB` |
| Master limiter release | `60 ms` |
| Master postgain | `0 dB` |
| Crossfeed during qualification | disabled |

JamesDSP crossfeed may be enabled manually for headphone listening, but it is
not part of the measured Axiom comparison baseline.

## Current Open Investigation

| Run | Status | Meaning |
| --- | --- | --- |
| `20260603T004349-post-acceptance-v4-1-4-1-0d309b` | `investigating` | Post-acceptance `.11` dense-material limiter pressure and elevated Sub Harmonics range audit. |

Known result:

- accepted-setting dense-material stress: `pass_with_investigation`;
- Sub Harmonics map: recorded `fail` because the old one-hour wrapper timeout
  stopped the full sweep before the aggregate report was written;
- completed partial evidence showed normal material stayed unclipped through
  the completed `+4`, `+6`, `+8`, and partial `+10 dB` cases;
- the follow-up should use the newer targeted map options and longer timeout
  before treating this as an audio defect.

Recommended follow-up:

```bash
node tools/axiom-team/bin/axiom-team.mjs map-sub-gain \
  20260603T004349-post-acceptance-v4-1-4-1-0d309b \
  --slider-db 10 --slider-db 12 \
  --label-regex 'electronic|hip hop|bass|flawed'
```

Run this only when the JDSP route is available and no other real-host
measurement is active.

## Operating-System Foundation

The AI development ecosystem has been converted from the local
`axiom-idea.html` brainstorm into repository workflow. The foundation merged in
PR #10 as commit `c498688`.

| Layer | Status | Document |
| --- | --- | --- |
| Role and flow spec | merged | `ai-development-ecosystem.md` |
| Codex operating guide | merged | `codex-operating-guide.md` |
| Product/profile roadmap | merged | `axiom-system-roadmap.md` |
| Ordered implementation plan | complete | `axiom-operating-system-implementation-plan.md` |
| Labs policy | merged | `labs-policy.md` |
| Knowledge structure | initial structure merged | `knowledge/README.md` |
| Labs/review templates | merged | `templates/` |
| GitHub issue forms | merged | `.github/ISSUE_TEMPLATE/` |
| Pi runbooks | merged | `pi-runbooks.md` |
| Session work log PDF workflow | merged | `session-work-log.md`, `session-work-log.pdf` |
| Agentic engineering blueprint | local v1 source-ready | `axiom-agentic-engineering-blueprint.md` |
| Axiom Codex skill | local v1 installed | `~/.codex/skills/axiom-engineering` from `../tools/codex-skills/axiom-engineering/` |
| Axiom Codex helper CLI | local v2 source-ready | `../tools/axiom-codex/axiom_codex.py` |

These docs and templates are workflow infrastructure. They do not change DSP
behavior. Larger product lanes such as Axiom Reference, Immersive, Night, and
Studio Path are defined but not built as official products.

## Latest Assessment

The current full-system assessment is
`axiom-full-state-assessment-2026-06-04.md`.

Summary:

- `v4.1.4.11` remains the accepted Core baseline.
- The local validation snapshot passed static EEL, Python unit, Pi harness,
  doctor, strict corpus metadata, candidate readiness, Codex helper readiness,
  and whitespace checks.
- Candidate readiness is available for a future scoped hypothesis, but no
  `.12` candidate is currently justified.
- The local Axiom Codex skill is installed in this machine's Codex runtime;
  helper tooling remains repo-tracked under `tools/`.
- Initial Codex-layer hardening is implemented with a command registry,
  Codex-specific role profiles, guard preflights, and deterministic skill
  behavior eval fixtures.
- Axiom Knowledge has safe structure and six local-source-backed seed notes for
  spatial hearing, digital audio effects, implementation patterns, reproduction
  accuracy, and audio-programming background.

## Current Best Next Actions

1. Use `$axiom-engineering` in fresh Codex sessions for Axiom work.
2. Use `python3 tools/axiom-codex/axiom_codex.py command-surface`,
   `agent-profiles`, `guard-check`, and `skill-eval` as the current
   Codex-layer hardening surface.
3. Rerun the targeted `.11` Sub Harmonics map if the JDSP route is available.
4. Use the Knowledge seed notes to refine listening vocabulary, DSP-stage
   review, implementation translation, and test-design questions before adding
   any new DSP claims.

## Refresh Commands

Use these commands when updating this dashboard:

```bash
git status -sb
node tools/axiom-team/bin/axiom-team.mjs doctor
node tools/axiom-team/bin/axiom-team.mjs status
scripts/evaluate_axiom_candidate_readiness.py \
  --json /tmp/axiom-candidate-readiness.json \
  --markdown /tmp/axiom-candidate-readiness.md
```

Generated reports and captures remain local unless a sanitized summary is
explicitly added to `docs/`.
