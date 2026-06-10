# Axiom Full-State Assessment

Date: 2026-06-04

Scope: current `main` worktree after the operating-system foundation merge,
post-merge reconciliation cleanup, session-log cover work, agentic blueprint,
and local Axiom Codex skill/helper v1.

This assessment is a state record, not a release note. It separates accepted
facts from open risks so the next work can be chosen without guessing.

## Executive Judgment

Axiom is currently strongest as a conservative, measurement-guided Core DSP
line with a real accepted baseline: `v4.1.4.11`. The system has moved from
one-off EEL iteration into a repository-managed product workflow with
qualification records, host-setting policy, Pi execution tooling, listening
protocols, and now a local Codex-side agentic blueprint.

The next risk is not lack of ideas. The next risk is overbuilding before the
accepted Core has been completely characterized. The correct posture is:

- keep `v4.1.4.11` as the accepted baseline;
- do not create `.12` until there is a scoped, falsifiable hypothesis;
- finish the open elevated Sub Harmonics / limiter-pressure follow-up when the
  JDSP route is available;
- install or publish the local Codex skill only after explicit approval;
- populate Axiom Knowledge with lawful summaries before relying on it for
  research support.

## Current Accepted Core

| Item | State |
| --- | --- |
| Accepted version | `v4.1.4.11` |
| Accepted script | `src/axiom_binaural_dsp_v4.1.4.11.eel` |
| Accepted SHA-256 | `ad7dd7b33f2e62ff03ae08d7101c7ac333d707baef26b952806990ad979b0b0e` |
| Qualification record | `docs/qualification-v4.1.4.11.md` |
| Policy anchor | `tools/axiom-team/policy.json` |
| Active candidate | none |

The accepted `.11` change is narrow: it reduces the elevated-bass reserve
slope above the default `+4 dB` Sub Harmonics setting from `0.750 dB/dB` to
`0.500 dB/dB`. It does not alter the default `+4 dB` path, spatial width,
bass-generation topology, exciter behavior, STFT behavior, host-limiter
ownership, crossfeed ownership, or slider ranges.

## Host Baseline

| Host Setting | Accepted Qualification Value |
| --- | --- |
| JDSP master processing | enabled |
| Master limiter threshold | `-1.00 dB` |
| Master limiter release | `60 ms` |
| Master postgain | `0 dB` |
| Crossfeed during qualification | disabled |

The JDSP limiter remains part of the accepted listening environment. Axiom Core
delegates terminal limiting to the host and avoids internal limiter ownership.
That design is coherent, but it means any future claim about loudness,
headroom, or clipping must specify the host settings used during validation.

## Validation Snapshot

Commands run for this assessment:

| Check | Result | Meaning |
| --- | --- | --- |
| `scripts/validate_axiom_static.sh src/axiom_binaural_dsp_v4.1.4.11.eel` | pass | EEL2/JDSP static policy holds for the accepted script. |
| `python3 -m unittest discover -s tests -p 'test_*.py'` | pass, 159 tests | Python analysis, package, qualification, and validation helpers are healthy. |
| `npm test` in `tools/axiom-team` | pass, 22 tests | Pi harness policy, guard, and command tests are healthy. |
| `node tools/axiom-team/bin/axiom-team.mjs doctor` | pass | Baseline hash, route helper, material manifest, tools, and repo state are recognized. |
| `node tools/axiom-team/bin/axiom-team.mjs corpus-status --strict-metadata` | pass | Local material manifest validates with 14 tracks and required metadata coverage. |
| `python3 scripts/evaluate_axiom_candidate_readiness.py` | ready | A new candidate may be considered only with a scoped hypothesis and target. |
| `python3 tools/axiom-codex/axiom_codex.py ready-check` | pass | Local Codex helper sees clean safe checks and no `src/` or `scripts/` diffs. |
| `git diff --check` | pass | Current local text diffs have no whitespace errors. |

Important boundary: `candidate-readiness` being ready does not mean a new DSP
candidate should be created. It means the repository has the baseline, corpus,
and device metadata needed to evaluate a candidate if one becomes justified.

## Strongest Parts Of The System

### Core DSP Discipline

The accepted line now has versioned scripts, hash-anchored policy, qualification
records, and no in-place mutation of historical EEL files. That is the right
shape for a product DSP line.

### Host Ownership Clarity

The architecture has stopped fighting JDSP. Crossfeed is delegated to JDSP when
the listener wants it, and terminal limiting is delegated to the JDSP host
instead of being duplicated inside Axiom. This keeps Axiom Core cleaner and
easier to test.

### Measurement And Qualification Harness

The repo now has static checks, offline analysis scripts, material-manifest
validation, Android/device validation docs, listening package tooling, and a Pi
harness that enforces candidate and qualification discipline. The test suite is
not just cosmetic; it has already shaped the accepted `.8` through `.11` line.

### Operating-System Foundation

The repository now documents Codex, Pi, external reviewer, Knowledge, Labs, and
Qualification responsibilities. This makes the project much less dependent on
chat memory.

### Agentic Layer v1

The local Axiom Codex skill source and helper CLI now exist in repo form. They
can summarize status, run safe readiness checks, scaffold role reviews, and
query repo-safe Knowledge notes. This is the first practical step toward a
native Axiom agentic engineering layer.

## Weak Points And Improvements

### 1. The Open `.11` Sub Harmonics Boundary Is Still Unclosed

Weak point:

The post-acceptance Sub Harmonics map still has an investigation record because
the old one-hour wrapper timeout stopped the full sweep before the aggregate
report was written. Partial evidence is encouraging, but it is not a closed
qualification boundary.

Improve it:

Run the targeted map with the newer options and longer timeout when the JDSP
route is available:

```bash
node tools/axiom-team/bin/axiom-team.mjs map-sub-gain \
  20260603T004349-post-acceptance-v4-1-4-1-0d309b \
  --slider-db 4 --slider-db 10 --slider-db 12 \
  --label-regex 'electronic|hip hop|bass|flawed'
```

Do not treat this as a confirmed audio defect unless the targeted run shows a
repeatable normal-material failure.

### 2. Listening Evidence Is Strong But Not Yet Blind Or Calibrated

Weak point:

The human listening authority is essential, but most acceptance notes are not
blind, not level-calibrated against a fixed SPL target, and not always captured
as structured per-track records.

Improve it:

Keep the user's final listening authority, but add more structured records for
future candidates: track class, route, gain, fatigue, artifact, bass, vocal,
stage, and accept/reject notes. Do this especially for any `.12` or profile
candidate.

### 3. The Corpus Is Useful But Still Small

Weak point:

The strict local corpus has 14 tracks with good category coverage, but it is
still a small dataset. It cannot represent all modern commercial masters,
badly mastered files, headphones, speakers, Bluetooth codecs, or phone routes.

Improve it:

Add lawful material over time and keep the manifest metadata strict. New
material should target missing failure modes rather than simply adding more
music.

### 4. Host Coupling Remains A Real Engineering Constraint

Weak point:

JDSP host settings, route stability, Android behavior, and WSL-to-Windows audio
state can change the observed result. That is unavoidable, but it means Axiom
cannot make host-independent loudness or clipping claims.

Improve it:

Keep host settings in every qualification record. Serialize real-JDSP tests.
Treat route instability as a blocker, not a measurement result.

### 5. Agentic Layer Is Source-Ready, Not Installed Runtime

Weak point:

The repo now contains a Codex skill source and helper CLI, but the skill is not
installed under `~/.codex/skills/axiom-engineering`. Native Codex slash
commands are not implemented. The current state is a valid v1 source package,
not a fully active agent team.

Improve it:

After explicit approval, run:

```bash
python3 tools/install_axiom_codex_skill.py --install
```

Then validate that Codex can load the skill in a fresh session. Keep Pi as the
execution layer for real-JDSP workflows.

### 6. Knowledge Is Structured But Mostly Empty

Weak point:

Axiom Knowledge has policy, schema, and templates, but not enough lawful
source notes yet to materially guide DSP decisions.

Improve it:

Start with a small, high-quality bibliography set. Each note should include
citation, short summary, relevant Axiom concepts, possible test ideas, and no
copyrighted source text.

### 7. Documentation Is Powerful But Could Become Heavy

Weak point:

The repo now has many docs. This is good for governance, but it can slow down
new agents if the source of truth is not obvious.

Improve it:

Keep `docs/system-status.md` as the first-read dashboard. Keep
`docs/README.md` as the map. Avoid adding new docs when an existing status,
policy, or evidence record can be updated cleanly.

### 8. Local Worktree Contains A Large Uncommitted Batch

Weak point:

The current local changes are docs/tooling only, but they are broad. Leaving
them uncommitted while starting new work increases review complexity.

Improve it:

When the user is ready, review and commit the local agentic/docs batch before
starting another major implementation track.

## Current System By Layer

### Axiom Core

State: accepted and stable at `v4.1.4.11`.

Best next action: keep it unchanged until the targeted `.11` Sub Harmonics
follow-up is closed or a better scoped hypothesis appears.

### Axiom Qualification

State: strong. Static checks, Python tests, Pi harness tests, strict material
metadata, candidate readiness, and release gates are all present.

Best next action: close the open elevated-bass map and continue adding
structured listening records.

### Axiom Labs

State: policy and templates exist. No active Labs experiment is promoted into
Core.

Best next action: use Labs only for bounded hypotheses, not broad rewrites.

### Axiom Knowledge

State: safe structure exists. Content population remains the work.

Best next action: add the first real source notes and keep private books,
copies, and library paths out of git.

### Axiom Agentic Engineering

State: local v1 source exists. It includes skill source, references, helper
CLI, install helper, and blueprint PDF.

Best next action: review and optionally install after explicit approval. Do not
pretend it is a fully autonomous engineering team yet.

### Repository Housekeeping

State: organized, but carrying a broad local docs/tooling batch.

Best next action: commit/publish this batch after review, then return to DSP or
Knowledge work.

## What Not To Do Next

- Do not create `.12` just because readiness passes.
- Do not alter `v4.1.4.11` in place.
- Do not install the Codex skill without explicit approval.
- Do not merge experiments into Core without qualification.
- Do not add copyrighted books, long excerpts, private source paths, or source
  audio to the repo.
- Do not claim true binaural accuracy, mastering-grade proof, HRTF accuracy, or
  true-peak certification without repository evidence.

## Recommended Next Work Order

1. Review this assessment and the local agentic/docs batch.
2. Commit/publish the local docs/tooling batch when approved.
3. Install the Axiom Codex skill locally only after explicit approval.
4. Run the targeted `.11` Sub Harmonics map when the JDSP route is available.
5. Add the first Axiom Knowledge source notes.
6. Use a multi-role `agent-review` before any sound-changing candidate.
7. Create `.12` only if the evidence points to one narrow, testable change.

## Bottom Line

Axiom is in a good engineering state, but the right next move is consolidation,
not feature expansion. The DSP Core is accepted. The workflow foundation is
real. The agentic layer is now source-ready. The remaining work is to close the
known `.11` measurement boundary, activate the agentic layer carefully, and
populate Knowledge with lawful material that improves test design without
weakening evidence standards.
