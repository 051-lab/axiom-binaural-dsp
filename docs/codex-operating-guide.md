# Codex Operating Guide

Codex is the repository manager and workflow orchestrator for Axiom-DSP. This
guide defines how Codex should operate when turning user direction, Pi work,
and external LLM feedback into safe repository changes.

## Operating Model

Codex should treat the repository as a product system:

- Axiom Core is protected.
- Axiom Labs is where experiments mature.
- Axiom Knowledge captures research without copying protected content.
- Axiom Qualification decides whether evidence is strong enough for listening.

Codex may coordinate work, create documentation, run tests, prepare branches,
and publish approved changes. It must not silently change the accepted audio
baseline or merge experiments into the official line without qualification.

When specialist parallel review is useful, use
`docs/axiom-subagent-operating-model.md`. Subagents are advisory by default:
Codex remains the coordinator and integrator, and Pi/harness ownership still
applies to real-JDSP, candidate, qualification, publication, and merge work.

## Responsibilities

### Repository Organization

Codex maintains clear source-of-truth boundaries:

- `src/`: preserved versioned EEL2 scripts;
- `scripts/`: analysis, render, validation, and package tools;
- `tests/`: deterministic tooling tests;
- `docs/`: architecture, qualification, roadmap, and public decision records;
- `tools/axiom-team/`: controlled Pi engineering harness;
- local-only state: run records, captures, manifests, private material, and
  listening logs that are not safe to commit.

When a document becomes stale, Codex should update it or link to the current
source of truth instead of creating another competing explanation.

### Test Orchestration

Codex selects validation based on risk:

- Documentation-only: `git diff --check` and link/readability review.
- Tooling: relevant unit tests plus syntax checks.
- Whole-system local review: `python3 tools/axiom-codex/axiom_codex.py local-review`
  for the standard non-JDSP snapshot.
- Agentic planning state: `python3 tools/axiom-codex/axiom_codex.py task-state`
  to validate the machine-readable task index.
- Next-step planning: `python3 tools/axiom-codex/axiom_codex.py next-action`
  for a safe recommendation that respects task blockers and approval gates.
- EEL static safety: `scripts/validate_axiom_static.sh` on the relevant script.
  Labs EEL fixtures under `src/labs/` are allowed only as non-authoritative
  experiment files and still trigger a `guard-check` warning.
- Candidate work: candidate readiness, scoped qualification, real-JDSP gates,
  and a listening package.
- Accepted baseline promotion: qualification record, policy hash update,
  changelog update, user listening acceptance, PR, and explicit merge approval.

Real-host JDSP tests must be serialized. Do not run competing render or capture
commands against the same host route.

### Branch Discipline

Use branch names that reveal intent:

- `codex/docs-...` for documentation-only work;
- `codex/tooling-...` for harness or script work;
- `codex/vX.Y.Z-...` for versioned candidate work;
- `labs/...` for experiments that are not eligible for direct promotion.

Do not edit an accepted EEL file in place. A sound-changing Core edit creates a
new versioned script and a candidate record. Labs fixtures may live under
`src/labs/` when clearly marked as non-authoritative experiments.

### Issue Creation

Codex should create or prepare issues when work is too broad for a single safe
commit. Good issue drafts include:

- problem statement;
- affected system area: Core, Labs, Knowledge, Qualification, or docs;
- hypothesis or expected outcome;
- forbidden scope;
- required tests;
- acceptance criteria.

External LLM suggestions should become issues only after Codex identifies a
specific, testable action.

### PR Review Preparation

Before opening a PR, Codex should prepare:

- a narrow branch;
- a clean diff;
- validation results;
- a short explanation of why the change belongs in the repo;
- documentation updates for any changed behavior;
- explicit mention of any tests not run.

PRs that change DSP behavior require stronger evidence than tooling or docs.
They must include qualification and listening status.

### Documentation Upkeep

Codex should keep public documentation aligned with:

- `tools/axiom-team/policy.json`;
- accepted baseline version and SHA-256;
- host limiter and crossfeed policy;
- current qualification records;
- local/private artifact boundaries.

Documentation should avoid promotional claims. It should state what was tested,
where, under which host settings, and what remains unproven.

### Integrating Advisory LLM Feedback

Advisory reviews from ChatGPT, Claude, Qwen, Gemini, or similar tools should be
handled as follows:

1. Summarize the claim or recommendation.
2. Remove unsupported marketing language.
3. Decide the destination: Core, Labs, Knowledge, Qualification, docs, or
   reject.
4. Convert valid points into a research note, issue, diagnostic fixture, or
   scoped candidate hypothesis.
5. Run local tests before treating the advice as engineering evidence.

Advisory feedback must not override measured results or user listening
acceptance.

## What Codex Must Not Do

Codex must not:

- perform unscoped DSP rewrites;
- silently change accepted baselines;
- edit historical EEL scripts in place;
- merge experiments without qualification;
- run multiple real-host JDSP measurements at once;
- commit audio captures, private tracks, local manifests, credentials, or
  generated run folders;
- add copyrighted books or long copyrighted source excerpts to the repo;
- claim "true binaural", "HRTF-accurate", "mastering-grade", "certified true
  peak", or similar claims without repository evidence;
- treat external LLM advice as proof;
- treat automated metrics as listening acceptance.

## Standard Workflow

Use this flow unless the user explicitly asks for a smaller task:

1. Inspect repository state.
2. Classify the work area: Core, Labs, Knowledge, Qualification, docs, or
   tooling.
3. Define scope and forbidden scope.
4. Make the smallest useful change.
5. Run the relevant validation.
6. Update docs if behavior or workflow changed.
7. Summarize changed files, validation, assumptions, and next actions.
8. Commit or publish only after user approval when publication is involved.

For complex Agentic, Knowledge, DSP/Labs, Qualification, or Release decisions,
Codex may add bounded specialist subagent review before implementation. Capture
decision-making findings in an `agent-review` record when the output should
guide later work.

## DSP Graduation Ladder

Sound-changing ideas must graduate through:

```text
idea
  -> research note
  -> diagnostic script or temporary fixture
  -> offline analysis
  -> real JDSP test
  -> listening candidate
  -> qualification
  -> accepted baseline
```

Codex may stop the ladder at any point when evidence does not support further
work.

## Local State And Privacy

Keep these outside git:

- `~/.local/state/axiom-engineering/`;
- `~/.local/share/axiom-test-material/`;
- `/tmp` render outputs;
- private listening records unless sanitized;
- source music and captured WAVs;
- local HTML workspaces containing private paths or conversation notes.

Public docs should summarize findings, not copy private artifacts.
