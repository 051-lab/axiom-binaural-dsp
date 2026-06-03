# Axiom System Status

Last updated: 2026-06-03

This is the quick-start dashboard for Codex, Pi sessions, and future agents.
Read this before choosing new work. It summarizes the current accepted line,
active investigations, operating-system rollout, and the next recommended
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

## Operating-System Rollout

The AI development ecosystem is being converted from the local
`axiom-idea.html` brainstorm into repository workflow:

| Layer | Status | Document |
| --- | --- | --- |
| Role and flow spec | drafted | `ai-development-ecosystem.md` |
| Codex operating guide | drafted | `codex-operating-guide.md` |
| Product/profile roadmap | drafted | `axiom-system-roadmap.md` |
| Ordered implementation plan | drafted | `axiom-operating-system-implementation-plan.md` |
| Labs policy | drafted | `labs-policy.md` |
| Knowledge structure | drafted | `knowledge/README.md` |
| Labs/review templates | drafted | `templates/` |
| GitHub issue forms | drafted | `.github/ISSUE_TEMPLATE/` |
| Pi runbooks | drafted | `pi-runbooks.md` |

These docs and templates are workflow infrastructure. They do not change DSP
behavior.

## Current Best Next Actions

1. Review and publish the documentation/workflow foundation as a docs-focused
   PR.
2. Rerun the targeted `.11` Sub Harmonics map after publication if the JDSP
   route is available.
3. Build concrete examples only after the first real Labs experiment or
   Knowledge note exists.
4. Do not create a sound-changing candidate until candidate readiness and a
   scoped hypothesis justify it.

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
