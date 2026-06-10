# Axiom Full-System Readiness Review

Date: 2026-06-08

Scope: evidence-local review of Axiom Core DSP, qualification state,
Pi/JDSP workflow, Codex tooling, Knowledge, documentation, and release posture
on branch `codex/axiom-codex-hardening-knowledge`.

This review is intentionally blunt. It is not a release note, not a listening
acceptance record, and not approval to create `.12`.

## Executive Judgment

Axiom is in a strong but unfinished state.

The system is no longer a loose DSP script. It has an accepted baseline,
hash-anchored policy, qualification records, host-setting ownership, local
material metadata, device readiness, a Pi harness, Codex guardrails, and a
seeded Knowledge base. That is a serious foundation for Audio-DSP engineering
with AI tooling.

The main shortcoming is not infrastructure anymore. The main shortcoming is
open evidence. The accepted `v4.1.4.11` baseline is still carrying a targeted
Sub Harmonics / limiter-pressure follow-up that must be closed before a new
sound-changing candidate is justified. Candidate readiness is `READY`, but
readiness only says the evidence foundation can support candidate discussion.
It does not supply the hypothesis.

The correct next posture is conservative:

- review and merge PR #12 before adding more tooling onto the same branch;
- close the targeted `.11` Sub Harmonics investigation with Pi/JDSP when the
  route is available;
- convert Knowledge sources into test vocabulary only when a concrete Axiom
  question needs it;
- do not create `.12` until the investigation produces a repeatable defect,
  scoped benefit, and listening target.

## Current State

| Area | State |
| --- | --- |
| Accepted baseline | `v4.1.4.11` |
| Accepted script | `src/axiom_binaural_dsp_v4.1.4.11.eel` |
| Accepted SHA-256 | `ad7dd7b33f2e62ff03ae08d7101c7ac333d707baef26b952806990ad979b0b0e` |
| Active candidate | none |
| Current branch | `codex/axiom-codex-hardening-knowledge` |
| Draft PR | #12, open draft, merge state clean |
| DSP/script diffs | none |
| Local Knowledge sources | 6 registered sources, all with local files and repo-safe notes |
| Candidate readiness | `READY`, with the readiness boundary still in force |

## Validation Snapshot

| Check | Result | Meaning |
| --- | --- | --- |
| `python3 -m unittest discover -s tests -p 'test_*.py'` | pass, 170 tests | Python helpers and validation tools are healthy. |
| `python3 tools/axiom-codex/axiom_codex.py ready-check` | pass | Codex helper, command surface, profiles, and eval fixtures are internally consistent. |
| `python3 tools/axiom-codex/axiom_codex.py guard-check` | pass | No current changed paths violate known Axiom guardrails. |
| `python3 tools/axiom-codex/axiom_codex.py skill-eval` | pass, 7 fixtures | Skill behavior fixtures still map to expected helper commands and boundaries. |
| `python3 tools/axiom-codex/axiom_codex.py knowledge-sources` | pass, 6 sources | Local source index entries have local files and matching repo notes. |
| `node tools/axiom-team/bin/axiom-team.mjs doctor` | pass | Accepted baseline hash, toolchain, local material, and route helper are recognized. |
| `node tools/axiom-team/bin/axiom-team.mjs corpus-status --strict-metadata` | pass | Local corpus has 14 tracks and strict metadata coverage. |
| `python3 scripts/evaluate_axiom_candidate_readiness.py` | `READY` | Candidate discussion is allowed only with a scoped hypothesis and listening target. |
| PR #12 metadata | open draft, merge state clean | The Codex/Knowledge batch is reviewable but not merged. |

## Strong Areas

### Core Baseline Discipline

The accepted line is versioned, hash-anchored, and documented. Historical EEL
files are protected by policy and helper guardrails. This is the right shape
for a DSP product line.

### Host Ownership

Axiom Core correctly avoids owning terminal limiting and crossfeed inside the
script. JDSP owns the terminal limiter. Optional headphone crossfeed stays in
the host. This reduces duplicate processing and keeps Core comparison cleaner.

### Qualification Infrastructure

The Pi harness, material manifest, device matrix, readiness gate, and validation
scripts are substantial. The system can now say when a candidate discussion is
allowed and when evidence is still missing.

### Codex/Pi Boundary

Codex has a useful orchestration layer: status, guard checks, role profiles,
Knowledge search, source audits, skill evals, and read-only Pi handoff briefs.
Pi remains the execution layer for real-JDSP and candidate workflows. That
separation is healthy.

### Knowledge Foundation

The Knowledge base now has six local-source-backed notes and an audit command.
The system has enough lawful research context to improve vocabulary and test
design without copying books into git.

## Shortcomings And Required Improvements

### Critical: The `.11` Sub Harmonics Boundary Is Still Open

The system still has one unresolved Core evidence boundary:
`20260603T004349-post-acceptance-v4-1-4-1-0d309b`. The earlier Sub Harmonics
map recorded a failure because the wrapper timed out before the aggregate
report was written. Partial evidence is encouraging, but the boundary is not
closed.

Improvement:

- run the generated `pi-handoff` command only when the JDSP route is available;
- treat the result as evidence, not as a candidate decision;
- update the investigation gate after the run;
- do not create `.12` unless the targeted run shows a repeatable normal-material
  issue with a clear listening target.

### High: Candidate Readiness Can Be Misread

The readiness gate reports `READY`. That is good, but it is easy to misuse.
It means the baseline hash, corpus metadata, and device matrix are ready enough
to evaluate a candidate. It does not mean a candidate should exist.

Improvement:

- keep the wording in future reports explicit: `READY` permits candidate
  discussion only after a scoped hypothesis exists;
- require every proposed candidate to cite the open investigation or diagnostic
  result that justifies it.

### High: Listening Records Need More Structured Spatial Language

Axiom now has strong spatial-hearing source notes, but the listening-record
format has not yet absorbed that vocabulary. Future candidate decisions would
benefit from consistent terms for center image, lateral spread, localization
blur, depth impression, bass-image coupling, and fatigue.

Improvement:

- extend listening-record guidance before the next sound-changing candidate;
- keep human listening authority, but require clearer observation categories.

### High: PR #12 Should Be Merged Before More Tooling Work Accumulates

PR #12 contains a broad but coherent Codex/Knowledge hardening batch. Continuing
to build on the same branch without review increases merge and review risk.

Improvement:

- review PR #12;
- merge only after explicit approval;
- rebase or start a new branch for the next development slice after merge.

### Medium: Knowledge Is Seeded, Not Operationalized

The Knowledge base now has seed source notes, but few concept notes that connect
research to specific Axiom test designs. This is normal for the current stage,
but it limits immediate engineering value.

Improvement:

- create concept notes only from concrete needs, such as spatial listening
  vocabulary or nonlinear enhancement risk;
- avoid turning Knowledge into a dumping ground for book summaries.

### Medium: Native Agent Runtime Is Still Not The Source Of Truth

The repo has a solid Codex helper and skill source, and the local skill is
installed. Native slash commands or subagents are still registry plans rather
than committed runtime integrations. That is acceptable, but it should not be
overstated.

Improvement:

- keep using repo-tracked helper commands as the source of truth;
- add native wrappers only when the runtime mechanism is documented and can
  preserve approval boundaries.

### Medium: Product/Profile Lanes Are Defined But Not Built

Core, Reference, Immersive, Night, Studio Path, Labs, Knowledge, and
Qualification are documented, but only Core is real product behavior today.
This is fine, but public language must stay precise.

Improvement:

- continue saying future profiles are planned lanes, not shipped products;
- do not let profile ambition pull Core into unmeasured changes.

### Low: Documentation Volume Requires Continued Curation

The repo has become documentation-rich. That is useful for agent continuity,
but it can slow down new sessions if the starting path is unclear.

Improvement:

- keep `docs/system-status.md` as the first-read dashboard;
- keep `docs/README.md` current;
- prefer updating existing docs over adding new ones unless the new document has
  a distinct evidence purpose.

## Recommended Next 30/60/90 Days

### Next 30 Days

- Review and merge PR #12 after explicit approval.
- Run the targeted `.11` Sub Harmonics follow-up through Pi/JDSP.
- Update the investigation record based on the targeted run.
- Add structured spatial vocabulary to listening-record guidance.

### Next 60 Days

- Convert one or two Knowledge seed notes into focused concept notes tied to
  Axiom tests.
- Add a small checklist that maps candidate hypotheses to required evidence:
  diagnostic, real-JDSP, listening target, and release impact.
- Consider CI or a single wrapper command for the Codex helper checks after
  PR #12 is merged.

### Next 90 Days

- Decide whether `.11` remains fully closed or whether a `.12` hypothesis is
  justified.
- If `.12` is justified, keep it narrow and candidate-gated through Pi.
- Start Labs examples only when they do not blur the accepted Core line.

## Do Not Do Yet

- Do not create `.12` just because candidate readiness is `READY`.
- Do not edit accepted or historical EEL files in place.
- Do not merge PR #12 without explicit approval.
- Do not run real-JDSP measurements while another real-host run is active.
- Do not commit PDFs, captures, local material manifests, or private paths.
- Do not claim Knowledge sources prove Axiom behavior.

## Proposed Backlog Additions

| ID | Task | Why |
| --- | --- | --- |
| AX-TASK-022 | Close `.11` Sub Harmonics follow-up | Removes the main open Core evidence boundary. |
| AX-TASK-023 | Add structured spatial listening vocabulary | Makes future listening records more consistent and reviewable. |
| AX-TASK-024 | Create Knowledge concept notes from seed sources | Turns bibliography into concrete Axiom test-design support. |
| AX-TASK-025 | Review and merge PR #12 | Keeps the Codex/Knowledge hardening batch from becoming a long-lived branch. |
| AX-TASK-026 | Add a consolidated local review/check command | Reduces friction for future full-system reviews after PR #12 lands. |

## Bottom Line

Axiom is meaningfully stronger than it was before the agentic and Knowledge
work. The danger now is moving too fast because the tooling feels capable. The
best engineering move is still evidence-first: land the current infrastructure,
close the `.11` investigation, improve listening records, then decide whether a
new DSP candidate is actually justified.
