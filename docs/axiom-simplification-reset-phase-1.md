# Axiom Simplification Reset: Phase 1 Audit

Date: 2026-07-10
Status: Audit complete; restructuring not started
Scope: Repository organization, operating model, project state, and external-state boundaries

## Purpose

Axiom exists to turn natural-language descriptions of desired sound into
exceptional JamesDSP effects. DSP quality, controlled experimentation, and
human listening authority are the primary work. Repository infrastructure is
useful only when it makes that work safer, clearer, or more reproducible.

This Phase 1 record inventories the current repository and proposes a concrete
simplification sequence. It makes no sound-changing DSP edit, does not promote
or reject a candidate, and does not perform the broad moves proposed below.

## Executive Findings

1. The accepted baseline is consistent: `Axiom Clean R011`,
   `src/axiom_binaural_dsp_v4.1.4.11.eel`, SHA-256
   `ad7dd7b33f2e62ff03ae08d7101c7ac333d707baef26b952806990ad979b0b0e`.
2. Candidate state is contradictory. `src/axiom_clean_r012.eel` exists on
   `main` and `CHANGELOG.md` calls it the official listening candidate, but
   active guidance, policy, task state, and helper output say no candidate
   exists.
3. R012 passes static validation but has no repository qualification record,
   listening record, candidate task, policy entry, or recorded candidate-state
   transition. It is not accepted behavior.
4. The operating layer is much larger than the current DSP need: ten Codex
   profiles, the same ten Pi roles, ten specialist skill packages plus an
   umbrella skill, 21 helper commands, 47 closed or parked tasks, and a second
   Pi state machine.
5. Active documentation still has 54 top-level files. Several are historical
   evidence, but roadmap, state, status, overview, agent, task, and workflow
   documents compete for orientation.
6. External private material and generated captures correctly remain outside
   git, but the Windows controller is a project-owned external workspace. Its
   source, ownership, version, and relationship to this repository are not
   represented by a repository-owned manifest.
7. The system asks the user to understand agents, Pi handoffs, task IDs,
   helper registries, worktrees, evidence catalogs, and several gate documents
   before asking for a sound change. That reverses the intended priority.

## Candidate-State Verification

### Accepted DSP

| Item | Verified state | Sources |
| --- | --- | --- |
| Label | `Axiom Clean R011` | `AGENTS.md`, `AXIOM.md`, status docs |
| File | `src/axiom_binaural_dsp_v4.1.4.11.eel` | policy and status docs |
| SHA-256 | `ad7dd7b33f2e62ff03ae08d7101c7ac333d707baef26b952806990ad979b0b0e` | computed hash and policy |
| Qualification | accepted | `docs/qualification-v4.1.4.11.md` |
| Host terminal stage | limiter enabled, `-1.00 dB`, `60 ms`, `0 dB` postgain | policy and active docs |

No source examined promotes R012 to the accepted baseline. R011 therefore
remains the only accepted behavior.

### Candidate DSP

| Source | What it says |
| --- | --- |
| `src/axiom_clean_r012.eel` | R012 is a candidate with unity global width and interpolated bass saturation. |
| `CHANGELOG.md` | R012 is the official listening candidate and does not replace R011. |
| Git history | Commit `fef71a5` added the candidate to `main` on 2026-07-09. |
| Static validator | R012 is recognized as an R011-family script and passes static checks. |
| `AXIOM.md` | No official candidate exists; R012 is future work. |
| `docs/system-status.md` | No candidate exists and R012 must not be created without approval. |
| `docs/dsp-change-workflow.md` | R012 is not created. |
| Candidate-readiness plan | Creation requires explicit approval; the audit halt stops before creation. |
| `tools/axiom-team/policy.json` | Records only the accepted baseline; it has no active-candidate field. |
| `tools/axiom-codex/task_state.json` | All tasks are closed or parked; no R012 qualification or listening task exists. |
| `status-summary` | Reports no active candidate because it parses the stale status document. |
| Qualification documents | No R012 qualification document exists. |
| Session log | Stops at the pre-candidate reset and does not record R012 creation. |

The R012 file differs from the supported combined Labs fixture only in its
`desc:` line. Relative to accepted R011, its sound-changing boundary is:

- default global side width `135% -> 100%`;
- interpolated generated-sub saturation state and arithmetic.

Static validity is not qualification or listening acceptance. Until the owner
reconciles the missing approval/state transition, R012 must be described
literally as a **committed, statically valid, unqualified candidate file with
conflicting governance records**.

### Labs State

Two Labs EEL fixtures remain under `src/labs/`: the width-profile fixture and
the width-plus-bass-saturation fixture. Their plans and listening summaries are
archived. Both ingredients were recorded as Labs-supported, and the combined
fixture became the DSP basis of R012. There is no open Labs task or active Labs
experiment. These fixtures are provenance, not accepted behavior.

### Next Legitimate DSP Action

Do not create another candidate or change sound. First ask the project owner to
choose and record one of two states:

1. R012 creation was authorized: register it as the active unqualified
   candidate, add qualification/listening work, and align active docs and
   machine state.
2. R012 creation was not authorized: retain the Git history, withdraw the file
   from active candidate status through a deliberate repository change, and
   return to the owner-approved hypothesis gate.

If state 1 is confirmed, the next DSP-facing action is serialized R012
qualification followed by a listening comparison against R011. Measurements
may determine listening eligibility; only the owner may accept the sound.

## Repository Inventory

The classifications below describe intended disposition, not moves performed
during Phase 1.

### 1. Core And Authoritative

| Area | Contents | Simplification disposition |
| --- | --- | --- |
| Product intent | `AXIOM.md` | Make this the user-facing front door. |
| Agent safety | `AGENTS.md` | Reduce to immutable EEL/JDSP constraints, authority, and required checks. |
| Setup | `README.md` | Keep installation and the shortest usable commands. |
| Project state | proposed `axiom-state.json` | One machine-readable record for accepted, candidate, Labs, host, and next action. |
| DSP architecture | `docs/architecture.md` | Keep current chain and host ownership; archive long version history. |
| DSP workflow | `docs/dsp-change-workflow.md` | Keep one simple idea-to-acceptance path. |
| Release rules | `docs/release-gates.md` | Merge into the workflow or retain as its single gate appendix. |
| Runtime reference | `docs/JDSP4Linux_Knowledge_Base.md` | Keep as on-demand technical reference. |
| DSP source | accepted file, active candidate, `src/labs/` fixtures | Mark accepted, candidate, Labs, and historical state explicitly. |
| Host template | `presets/axiom-preset.conf` | Keep as the host configuration template. |
| Essential validation | static validator and focused render/qualification entry points | Present through one wrapper or short documented sequence. |
| Tests | tests for retained validation and qualification tools | Keep tests paired with active tools. |
| Decision history | `CHANGELOG.md` and qualification summaries | Keep concise decisions; archive superseded detail. |

### 2. Useful Support

- Deterministic stimuli, corpus, perceptual metrics, device, Android, WSL,
  route, and listening-package tools.
- `tools/axiom-player/` if the local player is still used for listening.
- `docs/knowledge/` repo-safe research notes and templates.
- Listening-record, corpus, device-matrix, and package documentation.
- Historical fixtures required to reproduce accepted qualification.
- One umbrella Axiom skill containing Lead workflow plus DSP and Qualification
  capability guidance.
- The Pi/JDSP harness if it remains the reliable serialized real-host runner.

Support tools should be discoverable from an index by task, not presented to
the user as required concepts.

### 3. Historical

- Legacy EEL scripts before R011.
- Version-specific screens, audits, investigation plans, and qualification
  records for superseded baselines.
- Completed Labs plans, listening targets, summaries, and decision maps.
- Old architecture decisions, progression reviews, roadmaps, blueprints, and
  system assessments.
- The 47 completed/parked Agentic task records after a compact final export.
- The session work log and generated PDF after useful decisions are summarized.
- Obsolete WSL, route, or controller guides that no longer match the active
  host setup.

The existing `docs/archive/` categories are a sound start. Add qualification,
investigations, and legacy-workflow categories so active `docs/` contains only
current guidance.

### 4. Duplicated Or Conflicting

- `AXIOM.md`, `docs/system-status.md`, `docs/current-state.md`,
  `docs/axiom-roadmap.md`, and `docs/axiom-system-overview.html` all describe
  current state with different age and detail.
- `docs/task-backlog.md` and `tools/axiom-codex/task_state.json` duplicate task
  state; neither records the committed candidate.
- `tools/axiom-team/policy.json` stores accepted state while status documents
  independently restate it.
- Ten Codex profiles duplicate ten Pi roles, then ten specialist skill packages
  repeat the same responsibilities again.
- `docs/codex-operating-guide.md`, the subagent model, skill references, Pi
  prompts, and `AGENTS.md` repeat authority and handoff rules.
- `status-summary`, `local-review`, `ready-check`, `guard-check`,
  `agentic-audit`, `task-state`, and `next-action` overlap in orientation and
  validation while validating one another's registries.
- The Python helper and Node/Pi harness each model gates, roles, candidate
  state, and handoffs.
- R012 existence conflicts with every pre-candidate active status source listed
  above.
- `tools/axiom-team/policy.json` limits candidate paths to legacy
  `src/axiom_binaural_dsp_v*.eel`, excluding `src/axiom_clean_r012.eel`.

### 5. Generated Or Local-Only

- Audio, captures, excerpts, private manifests, credentials, run folders, and
  raw evidence bundles.
- `__pycache__/`, `.pyc`, `.local-screenshots/`, and runtime state under
  `~/.config` or `~/.local/state`.
- `docs/knowledge/pdfs/` and `source-index.local.json`.
- Generated readiness, device, listening, and qualification reports under
  `/tmp` or a configured evidence root.
- `docs/session-work-log.pdf` and generated overview HTML/PDF artifacts.
- Google Drive copies and built controller packages.

Generated artifacts may be linked by sanitized manifest entries or summarized
in a reviewed qualification record. Their presence must never change
authoritative project state.

### 6. Unclear Purpose

- `docs/axiom-player.md`, `tools/axiom-player/`, and player start scripts.
- `docs/axiom-system-overview.html`, its assets, and local screenshots.
- `docs/axiom-notes.html`, which is local/untracked but still referenced by
  active roadmap documents.
- `LOCAL_PUBLISHING_WORKFLOW.md` versus the Pi publication state machine.
- General-purpose PDF and cover-art generators.
- Agentic review/evidence/Knowledge command families in the monolithic helper.
- Specialized one-off screen scripts after their decisions are closed.
- `.agents/`, `.codex/`, and installed-skill scaffolding if one umbrella skill
  covers current work.

Unclear does not mean delete. Phase 2 should record usage, owner, replacement,
and archive/delete decisions.

## Obsolete Or Excessive Workflow Findings

### Competing Sources Of Truth

Accepted state is copied into policy, AGENTS, AXIOM, status, current-state,
architecture, release docs, changelog, task state, and helper output. The helper
reads prose from `docs/system-status.md`, so it can report false machine status
when code and Git history disagree. Machine state must be primary; prose should
render or link to it rather than restating mutable values.

### Commands And Tools

The 21-command helper mixes project orientation, Agentic validation, Knowledge
indexing, evidence ingestion, Pi handoff, and session-log generation. The
primary workflow needs a status read, a validation entry point, and a
qualification entry point. Knowledge and evidence import may remain support
utilities. Profile registries, command registries, skill evals, and next-action
computation should not block DSP readiness.

The script directory contains many version-specific screens. Preserve tools
needed to reproduce accepted evidence, but archive or consolidate closed
screens behind shared render/compare behavior.

### Agent Roles

- coordinator + implementation lead + release steward -> **Axiom Lead**;
- DSP architect + EEL engineer + signal researcher -> **DSP Specialist**;
- measurement engineer + qualification lead + safety auditor ->
  **Qualification Specialist**;
- tooling engineer -> normal implementation capability when needed.

Permanent mirrored role documents and separate installable skills are not
needed. Temporary read-only subagents remain available for genuinely parallel
or specialist analysis, but create no authority or persistent state.

### External Workspaces

1. **Project-owned source:** The Windows Axiom Controller currently lives in
   `JamesDSP4Windows_Decluttered/AxiomConsoleHarness`. If it remains part of
   Axiom, move maintained source here in a later phase, or use an explicitly
   versioned separate repository referenced by a tracked component manifest.
2. **Third-party/runtime source:** JDSP configuration and the Airwindows
   checkout should remain external. Track version/provenance and setup only.
3. **Private/generated evidence:** Music, manifests, captures, listening
   records, device matrices, and reports remain local. Track a schema and a
   sanitized manifest containing artifact type, producing command,
   source/candidate hashes, host settings, timestamp, and optional content
   hash, never private paths or audio.

## Minimal Operating Model

### Authority

- **Project owner:** supplies natural-language sound goals, approves candidate
  creation when required, directs listening, accepts or rejects sound, and
  authorizes release.
- **Axiom Lead:** the single user-facing role. It translates the goal,
  maintains scope/state, invokes capabilities, and presents one next decision.
- **DSP Specialist capability:** designs the smallest hypothesis, reviews EEL2
  safety, implements approved candidate/Labs scope, and defines listening risk.
- **Qualification Specialist capability:** chooses proportional static,
  offline, real-host, and listening checks; reports uncertainty; never converts
  a metric into listening acceptance.
- **Optional capability/subagent:** research, host debugging, tooling, or
  independent review only when needed. Add no permanent role unless a distinct
  recurring responsibility cannot fit the three roles above.

### Authoritative State

Create one tracked file, provisionally `axiom-state.json`, with a small reviewed
schema:

```json
{
  "accepted": {
    "label": "Axiom Clean R011",
    "file": "src/axiom_binaural_dsp_v4.1.4.11.eel",
    "sha256": "ad7dd7b33f2e62ff03ae08d7101c7ac333d707baef26b952806990ad979b0b0e",
    "qualification": "docs/qualification-v4.1.4.11.md"
  },
  "candidate": {
    "label": "Axiom Clean R012",
    "file": "src/axiom_clean_r012.eel",
    "status": "unqualified",
    "qualification": null,
    "listening": "not_started"
  },
  "labs": [],
  "hostProfile": "jdsp-terminal-limiter-r011",
  "nextAction": "owner_candidate_state_confirmation"
}
```

This example captures the physically observed candidate but is not adopted
until the owner confirms its governance state. The final file should include a
schema version and stable project state only, not task history or local paths.

### New-Session Path

1. `AXIOM.md` for purpose, owner authority, and natural-language entry.
2. `axiom-state.json` for exact current state.
3. `docs/dsp-change-workflow.md` for a sound change.
4. Load `AGENTS.md`, architecture, JDSP reference, or qualification details
   only when the task touches those areas.

`docs/README.md` remains a categorized reference index, not another status
document.

### Simple DSP Change Workflow

```text
owner describes desired sound
  -> Lead restates goal, comparison, and forbidden artifacts
  -> DSP Specialist proposes one smallest testable hypothesis
  -> choose Labs or candidate scope
  -> implement a new file; never edit accepted/history in place
  -> Qualification Specialist runs proportional checks
  -> owner listens against the accepted baseline
  -> owner rejects, iterates, or accepts
  -> Lead updates state, qualification summary, and changelog
```

Infrastructure work enters this flow only when the current experiment cannot
be performed safely or reproducibly without it.

### Archive Policy

- Active docs answer current purpose, state, workflow, architecture, and
  release rules.
- Completed plans, investigations, superseded qualification detail, roadmaps,
  agentic designs, and narrative logs move under `docs/archive/<category>/`.
- Archive entries get a one-line index record: date, former role, reason
  archived, and current replacement.
- Archived documents are never loaded as instructions by default.
- Git history preserves obsolete generated artifacts and scaffolding; not every
  historical output needs a permanent tracked copy.

### External And Generated Evidence Policy

- Maintained Axiom source and schemas live here or in an explicitly versioned
  component repository named by a tracked manifest.
- Host configuration, third-party checkouts, private audio, captures, and raw
  reports remain external.
- A tracked schema defines sanitized local evidence manifests; instances stay
  ignored.
- Qualification summaries record hashes, versions, host settings, material
  classes, result, uncertainty, and listening status, but no private paths or
  copyrighted media.
- Generated HTML, PDF, screenshots, packages, caches, and reports are rebuilt
  outputs, not sources of truth.

## Concrete Reset Plan

### Gate 0: Reconcile Candidate State

- Confirm or withdraw R012 as the active unqualified candidate.
- Record the decision once in the new state source.
- Align AXIOM, status output, changelog wording, and qualification work.
- Do not change R012 DSP content during reconciliation.

### Phase 2: Establish One State Source

1. Add and validate the minimal `axiom-state.json` schema.
2. Make status tooling read only that file and verify referenced hashes.
3. Remove mutable baseline/candidate values from prose where a link suffices.
4. Retire task JSON and backlog from active planning after a historical export.
5. Reduce helper orientation to one `status` command.

### Phase 3: Collapse The Operating Layer

1. Replace mirrored profiles, Pi roles, and specialist skills with one Axiom
   Lead guide containing DSP and Qualification capability sections.
2. Keep optional subagent guidance as a short policy, not a role registry.
3. Remove Agentic contract, profile, command-surface, skill-eval, review-state,
   and next-action checks from normal readiness.
4. If the Pi harness remains, reduce it to host serialization, qualification,
   evidence output, and release safeguards, not parallel planning.

### Phase 4: Reduce Active Documentation

1. Keep the new-session path defined above.
2. Merge current-state and release duplication into state plus workflow.
3. Archive superseded roadmaps, screens, host guides, and narrative logs.
4. Mark technical references on-demand and historical evidence as archive.
5. Remove generated PDF/HTML/screenshots from authoritative navigation and
   decide whether they need to remain tracked.

### Phase 5: Consolidate Tools And External Boundaries

1. Identify active entry points from current use and reproduction needs.
2. Group version-specific screens as historical or consolidate shared logic.
3. Decide player and Windows controller ownership; bring source under version
   control or register a versioned component repository.
4. Add the sanitized external-evidence manifest schema and ignore instances.
5. Remove caches, generated artifacts, stale installers, and abandoned wrappers
   only after replacement paths are verified.

### Phase 6: Validate The Reset

The reset is complete when a fresh session can:

1. read purpose and exact state in two files;
2. accept a natural-language sound goal without exposing internal machinery;
3. create one controlled Labs fixture or candidate through the simple flow;
4. run static and proportional qualification through clear entry points;
5. present an A/B listening decision to the owner;
6. update one state file without synchronizing competing documents;
7. reproduce accepted evidence without undocumented neighboring directories.

## Phase 1 Stop Point

This audit is the end of Phase 1. Broad restructuring, tool removal, source
moves, candidate-state adoption, and controller migration require separate
reviewed work. No sound-changing DSP work is authorized by this plan.

## Phase 2A Resolution Note

On 2026-07-10, the project owner confirmed that R012 candidate creation was
authorized. `axiom-state.json` now records R011 as accepted and R012 as the
active unqualified listening candidate with qualification and listening
pending and promotion not approved. The contradictions above remain preserved
as Phase 1 findings; use the state file and current active documents for
operational truth.
