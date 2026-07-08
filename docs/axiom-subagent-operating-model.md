# Axiom Subagent Operating Model

This document defines how Codex should use specialist subagents while working
on Axiom. Subagents are a review and parallel-analysis tool. They do not own
Axiom authority, accepted baselines, JDSP host state, publication, or merge
decisions.

## Persistent Specialist Skills

The repo tracks installable Codex specialist skills under
`tools/codex-skills/`:

- `axiom-coordinator`
- `axiom-safety-auditor`
- `axiom-tooling-engineer`
- `axiom-signal-researcher`
- `axiom-dsp-architect`
- `axiom-eel-engineer`
- `axiom-measurement-engineer`
- `axiom-qualification-lead`
- `axiom-release-steward`
- `axiom-implementation-lead`

Install or refresh the umbrella Axiom skill and all specialists with:

```bash
python3 tools/install_axiom_codex_skill.py --all-axiom-skills --install --force
```

Restart Codex after installation so the CLI can discover the new skill/agent
cards. These persistent skills are the named Axiom specialists the CLI can
load. Runtime parallel work still depends on Codex's available subagent
execution mechanism; when spawning runtime agents, assign these specialist
roles explicitly in the prompt and record their output through
`agent-review` when the findings guide later work.

## Authority Model

Codex remains the coordinator and integrator:

- inspect current repo and local planning state;
- choose the narrowest useful specialist lane;
- merge specialist findings into a single decision record;
- make repository edits only after checking scope and forbidden scope;
- route real-JDSP, candidate, publication, merge, and accepted-baseline work to
  the normal gated workflow.

Subagents remain advisory unless Codex explicitly assigns a narrow worker task.
Their output must be checked against repository policy, tests, and evidence
before it changes docs, tooling, or implementation.

Pi and the harness remain the execution owner for real-JDSP measurements,
candidate creation, qualification, publication, and merge workflow.

## Default Continue Macro

When the user says "continue" or asks what is next, Codex should use this
orientation sequence:

1. Run or inspect the equivalent of `status-summary`, `task-state`,
   `next-action`, and `git status -sb`.
2. If the tree is dirty, finish, test, or review the current change batch
   before starting unrelated work.
3. Classify the lane: Knowledge, Controller/tooling, DSP/Labs, Qualification,
   Release, or general docs.
4. Spawn at most two or three read-only specialists when parallel review would
   materially improve the decision.
5. Capture decision-making findings in an `agent-review` record when the task
   affects architecture, safety, qualification, publication, or follow-on work.
6. End with one of these outcomes: `continue`, `delegate-to-Pi`,
   `needs-user-approval`, or `stop`.

## Role Routing

Use the smallest set of specialists that covers the risk.

| Lane | Required Specialists | Optional Specialists |
| --- | --- | --- |
| General coordination | Coordinator, Safety Auditor | Release Steward |
| Knowledge intake | Signal Researcher, Knowledge Curator, Safety Auditor | DSP Architecture Lead |
| DSP idea or Labs hypothesis | DSP Architecture Lead, EEL Engineer, Measurement Engineer, Safety Auditor | Qualification Lead |
| Controller or helper tooling | Tooling Engineer, Safety Auditor | Release Steward, Host/Controller reviewer |
| Qualification evidence | Measurement Engineer, Qualification Lead, Safety Auditor | Tooling Engineer |
| Release or publication | Release Steward, Safety Auditor, Qualification Lead | Coordinator |

If a named specialist profile does not exist yet, map the work to the closest
tracked Codex profile and state the mapping in the review record.

## Worker Permissions

Default subagent mode is read-only analysis. Worker mode is allowed only when
Codex gives a narrow file ownership boundary and the task cannot overlap with
another active edit.

Subagents must not:

- edit accepted or historical EEL files;
- create or promote candidates;
- run real-JDSP captures or host-route tests;
- change policy baselines;
- publish, merge, or push;
- store raw transcripts, private paths, source audio, local manifests, or
  copyrighted source text in repo files.

## Review Record Provenance

`agent-review` records may include optional provenance metadata for real
subagent-backed reviews:

- top-level `reviewRun` records the run id, orchestration runtime, safe input
  references, and optional context hash;
- per-role `subagent` records the specialist status, runtime, prompt/result
  hashes, and an opaque transcript reference;
- findings, evidence needed, evidence references, and decisions remain in the
  canonical role fields.

Review records must store hashes and opaque IDs only. They must not store raw
conversation transcripts, private file paths, local evidence paths, or direct
copies of source material.

## Forbidden Scope

Subagent workflow must not be used to bypass Axiom gates. These actions still
require the normal owner and approval path:

- accepted-baseline edits or promotions;
- historical EEL edits;
- new sound-changing candidates;
- real-JDSP measurements;
- concurrent host measurements;
- release, publication, PR, push, or merge;
- policy changes;
- private artifact or Knowledge-source ingestion into git;
- treating research, metrics, or subagent agreement as listening acceptance.

## Validation

For Agentic Layer changes involving subagents, run the focused helper tests and
contract checks:

```bash
python3 -m unittest tests.test_axiom_codex_helper.AxiomCodexHelperTests
python3 tools/axiom-codex/axiom_codex.py agentic-audit
python3 tools/axiom-codex/axiom_codex.py ready-check
python3 tools/axiom-codex/axiom_codex.py guard-check
```

Run broader tests when the implementation touches shared helper behavior.
