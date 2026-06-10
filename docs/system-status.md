# Axiom System Status

Last updated: 2026-06-09

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
- a 2026-06-08 route reset restored the JDSP capture path and the corrected
  targeted map completed at `+4`, `+10`, and `+12 dB`;
- the corrected map still recorded `fail`, but not because of normal-material
  clipping: normal material stayed unclipped through `+12 dB`, while the gate
  failed on a default `+4 dB` dense-electronic repeatability qualification and
  investigation findings for terminal-pressure observations plus elevated
  RMS retreat;
- a 2026-06-09 confirmatory rerun with the same command repeated the same
  conclusion: no normal-material clipping through `+12 dB`, `fail` caused by
  the default dense-electronic repeatability qualification, and elevated
  RMS-retreat observations at `+10 dB` and `+12 dB`;
- the summarized evidence record is
  `sub-harmonics-follow-up-v4.1.4.11.md`;
- the interpretation record is
  `sub-harmonics-interpretation-v4.1.4.11.md`: no `.12` candidate is justified
  yet; the next step is focused listening around elevated-setting punch,
  practical loudness, bass clarity, limiter pumping, and fatigue;
- the listening target is
  `sub-harmonics-listening-target-v4.1.4.11.md`, with a local-copy JSON
  template at `templates/sub-harmonics-listening-record-v4.1.4.11.json`;
- filtered local A/B packages can now be generated from completed Sub Harmonics
  map render folders, excluding flawed stress material from normal-material
  listening checks.

Current follow-up command, if a confirmatory rerun is needed:

```bash
node tools/axiom-team/bin/axiom-team.mjs map-sub-gain \
  20260603T004349-post-acceptance-v4-1-4-1-0d309b \
  --slider-db 4 --slider-db 10 --slider-db 12 \
  --label-regex 'electronic|hip hop|bass|flawed'
```

Run this only when the JDSP capture route is available and no other real-host
measurement is active. Targeted maps must include the accepted `+4 dB` default
so elevated settings can be compared to the baseline control point.

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

The current full-system readiness review is
`axiom-full-system-review-2026-06-08.md`.

Summary:

- `v4.1.4.11` remains the accepted Core baseline.
- Full Python tests passed with 170 tests.
- Pi doctor, strict corpus metadata, candidate readiness, Codex helper
  readiness, guard checks, skill evals, and Knowledge source audit passed.
- Candidate readiness is `READY`, but no `.12` candidate is justified yet; the
  completed `.11` Sub Harmonics follow-up produced a listening target, not an
  EEL edit boundary.
- The 2026-06-08 corrected targeted rerun and 2026-06-09 confirmatory rerun
  both produced full reports: no normal-material clipping through `+12 dB`,
  but failed gates due to default dense-electronic repeatability qualification
  plus terminal-pressure and elevated RMS-retreat investigation findings.
- Listening records now require structured spatial fields for center image,
  lateral spread, localization blur, depth impression, bass-image coupling, and
  route context.
- Draft PR #12 is open and clean for the Codex/Knowledge hardening batch.
- Axiom Knowledge has six local-source-backed seed notes and a passing source
  audit.

## Current Best Next Actions

1. Review and merge PR #12 only after explicit approval.
2. Run focused listening on accepted `.11` using
   `sub-harmonics-listening-target-v4.1.4.11.md` and the filtered local A/B
   packages before proposing `.12`.
3. Use the structured spatial listening vocabulary for that listening record.
4. Use Knowledge seed notes to support specific test-design questions, not to
   justify DSP changes by themselves.

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
