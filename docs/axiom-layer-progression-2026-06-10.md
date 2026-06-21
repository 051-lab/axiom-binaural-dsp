# Axiom Layer Progression Review

Date: 2026-06-10

Scope: durable progress tracker for the major layers that make up the Axiom
system. This is not a listening acceptance record, not a release note, and not
approval to create a new DSP candidate.

## Purpose

This document records where each Axiom layer currently stands so future Codex,
Pi, and human review sessions can see progression over time. It is meant to
answer: what has been built, what is still incomplete, and what should be
protected as the system grows.

## Layer Summary

| Layer | Current Maturity | Current Direction |
| --- | --- | --- |
| Human Authority Layer | strong | Keep user approval and listening authority explicit. |
| Core DSP Layer | strong but open investigation remains | Protect `v4.1.4.11` while closing the Sub Harmonics follow-up. |
| Qualification Layer | strong | Continue evidence-first candidate gating. |
| Pi Execution Layer | strong | Keep real-JDSP and candidate workflows serialized through the harness. |
| Codex Orchestration Layer | strong and improving | Use repo-tracked helper commands, guardrails, and skill workflow as the source of truth. |
| Agentic Layer | medium-strong foundation | Convert blueprint and role structure into repeatable review workflows. |
| Knowledge Layer | seeded | Use source-backed notes for vocabulary and test design, not proof. |
| Labs/Product Profile Layer | planned | Keep future lanes separate from accepted Core behavior. |
| Documentation/Continuity Layer | strong but needs curation | Keep the start path clear and avoid duplicate documents. |
| Release/Publication Layer | strong gates, conservative posture | Require explicit approval for publish, merge, and baseline promotion. |

## Completeness Snapshot

These percentages are engineering-readiness estimates, not mathematical proof.
They combine implemented capability, evidence coverage, repeatability,
documentation quality, and remaining blocked work as of 2026-06-10.

| Layer | Estimated Complete | Why It Is Not Higher |
| --- | ---: | --- |
| Human Authority Layer | 90% | Approval and listening authority are clear, but final listening records still need consistent completion during each investigation. |
| Core DSP Layer | 82% | `v4.1.4.11` is accepted and protected, but the elevated Sub Harmonics follow-up remains open. |
| Qualification Layer | 86% | Gates, records, corpus metadata, and A/B package workflow exist; the current open investigation still needs a final listening decision. |
| Pi Execution Layer | 84% | Harness and runbooks are strong, but real-JDSP work still depends on route availability and serialized host state. |
| Codex Orchestration Layer | 82% | Helper commands, skill workflow, guard checks, and task guidance are useful; native slash-command wrappers and richer machine-readable review outputs are not complete. |
| Agentic Layer | 68% | Blueprint, roles, and operating boundaries exist, but repeatable multi-role review artifacts are still being formalized. |
| Knowledge Layer | 60% | Source-backed seed notes and concept notes exist, but Knowledge is not yet deeply operationalized into routine test design. |
| Labs/Product Profile Layer | 35% | Lanes are defined, but most profiles remain planned rather than built behavior. |
| Documentation/Continuity Layer | 85% | The repo has strong continuity docs, but the volume requires ongoing curation and dashboard freshness. |
| Release/Publication Layer | 80% | Gates and approval rules are strong; publication flow should continue to be exercised conservatively through real PR cycles. |

Overall system completeness estimate: **75%**.

The system is past the loose-prototype stage. The main remaining work is not
more documentation for its own sake; it is closing open evidence loops,
formalizing repeatable Agentic Layer reviews, and keeping future product lanes
separate from accepted Core DSP behavior.

## Human Authority Layer

Current state:

- The user remains the product authority, listening authority, and approval
  gate for candidate creation, publication, merges, and accepted-baseline
  promotion.
- Human listening remains the deciding source for perceived quality. Metrics,
  Knowledge notes, and external LLM feedback do not replace it.
- The current Sub Harmonics listening pass has user observations captured
  locally, but no final decision has been made.

Progress:

- Approval boundaries are documented across `AGENTS.md`, release gates, the
  Codex operating guide, and the agentic blueprint.
- The workflow now distinguishes candidate readiness from candidate
  justification.

Open needs:

- Keep local listening observations structured enough to support later review.
- Make every sound-changing next step trace back to a user-approved hypothesis.

## Core DSP Layer

Current state:

- Accepted baseline: `v4.1.4.11`.
- Accepted script: `src/axiom_binaural_dsp_v4.1.4.11.eel`.
- Active candidate: none.
- The current open technical question is the `.11` Sub Harmonics / limiter
  pressure follow-up at elevated `+10 dB` and `+12 dB` settings.

Progress:

- The accepted line is versioned, hash-anchored, documented, and protected from
  in-place historical edits.
- `v4.1.4.11` narrowed the elevated Sub Harmonics reserve slope while preserving
  the accepted `+4 dB` default behavior.
- Follow-up measurements show no normal-material clipping through `+12 dB`, but
  they do show elevated-setting tradeoff signals that require listening context.

Open needs:

- Close or escalate the Sub Harmonics follow-up based on focused listening.
- Do not create `Axiom Clean R012` unless the listening result becomes a
  repeatable, scoped problem with a clear target.

## Qualification Layer

Current state:

- Candidate readiness is available as a formal gate.
- Strict corpus metadata, device readiness, qualification records, listening
  records, and evidence documents exist.
- The latest full-system review found the infrastructure strong, but the Core
  evidence boundary still open.

Progress:

- Axiom can now tell the difference between "ready to evaluate a candidate" and
  "a candidate is justified."
- Listening-record structure has started to absorb spatial and fatigue
  vocabulary.
- A/B listening packages can be generated from completed render folders while
  excluding flawed stress material.

Open needs:

- Keep readiness language explicit so `READY` is not mistaken for approval.
- Use focused listening to decide whether elevated Sub Harmonics behavior is
  acceptable, needs guidance, or justifies a new candidate.

## Pi Execution Layer

Current state:

- Pi remains the execution layer for real-JDSP measurements, candidate creation,
  qualification, publication, and merge workflows.
- Real-JDSP work must remain serialized because the host audio route is shared
  mutable state.

Progress:

- The `tools/axiom-team/` harness, runbooks, role files, and Pi command flow
  give real-host work a controlled path.
- Targeted Sub Harmonics mapping can be reproduced with explicit slider values
  and material filtering.

Open needs:

- Continue using Pi only when the JDSP route is available and no competing
  real-host run is active.
- Keep captures, reports, local manifests, and private audio out of git unless
  they are sanitized summaries.

## Codex Orchestration Layer

Current state:

- Codex is the repo orchestration layer: it reads state, plans work, updates
  docs, runs safe checks, prepares reviewable changes, and delegates real-host
  work to Pi.
- The helper CLI now exposes practical commands such as `status-summary`,
  `next-action`, guard checks, readiness checks, local review, Knowledge source
  audit, and task-state inspection.
- The local Axiom Codex skill is installed and active for Axiom work.

Progress:

- Codex now has a clearer operating boundary than a generic coding assistant.
- Helper outputs keep current baseline, open investigations, and next actions
  visible.
- Guardrails reduce the risk of accidental private artifact commits or unsafe
  DSP edits.

Open needs:

- Keep repo-tracked helper commands as the source of truth.
- Add native slash-command wrappers only if the Codex runtime exposes a stable
  mechanism that preserves approval gates.
- Continue turning repeated manual review steps into narrow helper commands
  only when the behavior is stable.

## Agentic Layer

Current state:

- The Agentic Layer has a strong blueprint and role model, but it is not yet a
  fully autonomous multi-agent runtime.
- Specialist responsibilities are defined for coordination, DSP architecture,
  EEL safety, measurement, qualification, safety audit, tooling, signal
  research, and release stewardship.
- Current operation is practical: Codex uses these roles as review structure,
  while Pi handles constrained execution.

Progress:

- The Axiom Agentic Engineering Blueprint defines the target operating model.
- Role and handoff concepts are reflected in the local skill and helper CLI.
- Full-system review work has already been shaped by the multi-role mindset:
  findings first, evidence needs, explicit boundaries, and no unsupported
  candidate creation.

Open needs:

- Turn role structure into repeatable review outputs for common situations:
  candidate hypothesis review, EEL safety review, measurement review,
  listening-readiness review, Knowledge-claim triage, and release review.
- Add machine-readable review artifacts only where they improve continuity.
- Avoid pretending the agentic layer can replace human listening or approval.

## Knowledge Layer

Current state:

- The Knowledge base has local-source-backed seed notes and concept notes.
- It includes source-index policy, repo-safe notes, and local-only handling for
  private books and PDFs.
- Knowledge is explicitly advisory: it improves vocabulary, test design, and
  reasoning quality, but it does not prove Axiom behavior.

Progress:

- The system now has lawful notes for audio-DSP, plugin engineering, sound
  reproduction, and spatial hearing sources.
- Concept notes have begun connecting research context to concrete Axiom
  concerns, including spatial listening vocabulary and elevated-bass headroom
  tradeoffs.
- Source audits help keep local files and repo notes aligned without committing
  copyrighted content.

Open needs:

- Continue adding concept notes only from real engineering questions.
- Use Knowledge to design better listening and measurement prompts.
- Keep private PDFs, book files, and raw source material outside git.

## Labs And Product Profile Layer

Current state:

- Core is the only accepted product behavior today.
- Reference, Immersive, Night, Studio Path, Labs, Knowledge, and Qualification
  lanes are defined as roadmap/profile concepts, not shipped DSP products.

Progress:

- Profile ownership and allowed-change boundaries are documented.
- Labs policy gives exploratory work a place that does not contaminate Core.

Open needs:

- Keep product/profile language precise.
- Do not let future profile ambition drive unmeasured Core changes.
- Promote Labs work only through evidence, qualification, and explicit approval.

## Documentation And Continuity Layer

Current state:

- Axiom is documentation-rich: system status, current state, architecture,
  qualification records, listening protocol, task backlog, runbooks, Knowledge,
  and full-system reviews are all present.
- `docs/system-status.md` remains the first-read dashboard.

Progress:

- Documentation now supports long-session recovery and multi-day continuity.
- Session logs, full-system reviews, and generated PDFs help preserve context.

Open needs:

- Keep `docs/README.md` and `docs/system-status.md` current.
- Prefer updating existing docs unless a new document has a distinct evidence
  or tracking purpose.
- Use this layer progression review as the continuity tracker for system-layer
  maturity.

## Release And Publication Layer

Current state:

- Publication, merge, accepted-baseline promotion, and stronger public claims
  require explicit approval.
- Release gates and guard checks are in place.

Progress:

- PR and merge discipline is now part of the operating model.
- The system distinguishes public repo state from local-only evidence and
  private artifacts.

Open needs:

- Keep release actions separate from ordinary docs/tooling edits.
- Do not make stronger claims than the current evidence supports.

## Current Highest-Value Next Moves

1. Finish the focused Sub Harmonics listening decision for `+4`, `+10`, and
   `+12 dB`.
2. Use that listening result to either close the `.11` follow-up, keep it as a
   watch item, or define a narrow `Axiom Clean R012` hypothesis.
3. Build the next Agentic Layer improvement around repeatable review artifacts,
   not autonomous DSP changes.
4. Keep Knowledge work tied to active engineering questions.
5. Keep this progression review updated after major layer changes.

## Bottom Line

Axiom now has the shape of a controlled audio-DSP engineering system: Core DSP,
qualification, Pi execution, Codex orchestration, Knowledge, documentation, and
approval gates all exist as recognizable layers. The Agentic Layer is no longer
just an idea, but it is still a structured operating framework rather than an
autonomous engineering runtime. The right next step is to keep tightening the
loop between evidence, listening, role-based review, and conservative candidate
decisions.
