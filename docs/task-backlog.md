# Axiom Task Backlog

This backlog turns the AI ecosystem and system-roadmap documents into concrete
repository work. Items are lightweight task briefs; create GitHub issues when a
task is ready for scheduling or delegation.

## Backlog

| ID | Status | Task | Area | Output | Acceptance Criteria |
| --- | --- | --- | --- | --- | --- |
| AX-TASK-001 | Complete | Formalize Axiom Core identity | Core | Core policy note or README section | Accepted baseline, host ownership, and no-in-place-edit rules are visible from the starting docs. |
| AX-TASK-002 | Complete | Create Labs branch policy | Labs | Branch policy doc or CONTRIBUTING section | Labs branches have naming, scope, artifact, and promotion rules. |
| AX-TASK-003 | Seed notes added | Create Knowledge Base bibliography notes | Knowledge | `docs/knowledge/` seed source notes | Notes contain citations and summaries only, with no copyrighted book contents or private paths. |
| AX-TASK-004 | Complete | Create profile matrix | System | Profile matrix doc or table | Core, Reference, Immersive, Night, Studio Path, Labs, Knowledge, and Qualification are mapped to owner, status, allowed changes, and tests. |
| AX-TASK-005 | Complete | Add listening protocol | Qualification | Listening protocol doc or extension to `listening-records.md` | Protocol defines material choice, level handling, device route, fatigue notes, comparison target, and acceptance decision format. |
| AX-TASK-006 | Complete | Document advisory LLM review flow | Codex | Review-flow doc or operating-guide section | External LLM feedback has a repeatable path from critique to issue, research note, fixture, or rejection. |
| AX-TASK-007 | Complete | Define candidate graduation ladder | Qualification | Candidate ladder doc or roadmap section | Every DSP idea must pass idea, note, fixture, offline analysis, real-JDSP test, listening candidate, qualification, and acceptance stages. |
| AX-TASK-008 | Complete | Define release gates for official scripts | Core | Release gate checklist | Promotion requires qualification doc, changelog, policy hash, listening acceptance, PR, and merge approval. |
| AX-TASK-009 | Complete | Sync stale baseline references | Docs | Documentation cleanup PR | No current-facing doc identifies `.10` or earlier as the accepted baseline. |
| AX-TASK-010 | Complete | Add targeted Sub Harmonics map docs | Qualification | Harness command documentation | `map-sub-gain` targeted options are documented for CLI and Pi use. |
| AX-TASK-011 | Complete | Create Labs experiment template | Labs | Markdown template | Experiments record hypothesis, changed variables, forbidden scope, tests, result, and promotion decision. |
| AX-TASK-012 | Complete | Create external-review triage template | Codex | Markdown template | Advisory reviews are summarized into claim, evidence need, action, and disposition. |
| AX-TASK-013 | Complete | Define local-only artifact policy checklist | Qualification | Checklist or docs addition | Captures, source music, manifests, credentials, local HTML, and generated reports have clear storage rules. |
| AX-TASK-014 | Complete | Create profile-specific test requirements | Qualification | Matrix or per-profile checklist | Each future profile has required static, offline, real-host, and listening checks before promotion. |
| AX-TASK-015 | Complete | Build issue templates for DSP candidates and docs work | Repository | `.github/ISSUE_TEMPLATE/` updates | Issues capture scope, forbidden scope, evidence, tests, and release impact. |
| AX-TASK-016 | Complete | Add system status dashboard | Repository | `docs/system-status.md` | A fresh agent can see accepted baseline, active candidate, open investigations, roadmap state, and next work. |
| AX-TASK-017 | Complete | Add Pi runbooks | Harness | `docs/pi-runbooks.md` | Pi/Codex sessions have repeatable missions for audit, investigations, Labs, qualification, advisory triage, housekeeping, and publication. |
| AX-TASK-018 | Complete | Define Axiom Codex command surface | Codex | `tools/axiom-codex/command_surface.json` and `command-surface` helper | Repeated workflows have clear triggers, inputs, outputs, and boundaries; `agentic-audit` validates registry/runtime synchronization and aliases. |
| AX-TASK-019 | Complete | Create role-specific Codex agent profiles | Codex | `tools/axiom-codex/agent_profiles/` and `agent-profiles` helper | Ten bounded roles map to tracked Pi role sources; required sections and mappings fail closed under `agentic-audit`. |
| AX-TASK-020 | Complete | Add automated guardrails for unsafe Axiom actions | Codex | `guard-check` helper and unit tests | Historical EEL edits, private artifacts, audio, manifests, credentials, policy changes, and private path leaks are blocked or flagged with adversarial regression coverage. |
| AX-TASK-021 | Complete | Add Axiom skill behavior evals | Codex | `tools/axiom-codex/skill_eval_cases.json` and `skill-eval` helper | Seven representative safety and workflow fixtures validate command mappings and required behavior terms; malformed fixtures fail contract validation. |
| AX-TASK-022 | Complete: watch item | Close `.11` Sub Harmonics follow-up | Qualification | Measurement summary, blinded listening result, and validated local record | Blinded listening split `+4` versus `+10` 2-2 and preferred `+4` over `+12` 4-0. Combined preference was `+4` in six of eight comparisons. Keep `Axiom Clean R011` accepted; no `R012` candidate is justified. |
| AX-TASK-023 | Complete | Add structured spatial listening vocabulary | Qualification | Listening-record guidance update | Listening records distinguish center image, lateral spread, localization blur, depth impression, bass-image coupling, fatigue, and route context. |
| AX-TASK-024 | Complete | Create Knowledge concept notes from seed sources | Knowledge | Short concept notes tied to Axiom questions | Seed bibliography now has focused concept notes for spatial listening vocabulary, elevated bass/headroom tradeoffs, stage isolation, and profile-scope boundaries without copying source text or claiming research proves Axiom behavior. |
| AX-TASK-025 | Complete | Review and merge PR #12 | Repository | Merged Codex/Knowledge hardening PR | PR #12 was reviewed, validation passed, and the PR was merged after explicit approval. |
| AX-TASK-026 | Complete | Add consolidated local review/check command | Codex | `local-review` helper command | The standard non-JDSP evidence snapshot covers git state, baseline, changes, guard, readiness, Agentic contracts, Knowledge, Python tests, Node tests, and recommended action. |
| AX-TASK-027 | Complete | Add machine-readable task state | Codex | `tools/axiom-codex/task_state.json` and `task-state` helper | Task metadata validates and reports status, phase, blockers, approvals, and next actions without parsing only Markdown tables. |
| AX-TASK-028 | Complete | Add next-action helper | Codex | `next-action` helper command | Planning accounts for task metadata, dirty trees, evidence, blockers, approvals, and explicit maintenance opt-in without running JDSP or granting decisions. |
| AX-TASK-029 | Complete | Add Airwindows Knowledge intake workflow | Knowledge | Source note, concept taxonomy, indexing, audit, and query discovery | Airwindows is indexed as local-only canonical metadata with pinned provenance, strict field/path auditing, automatic safe query discovery, and clean-room boundaries without vendoring code or creating a candidate. |
| AX-TASK-030 | Initial implementation complete | Add qualification evidence ingestion | Agentic Layer | `evidence-ingest` helper and normalized local evidence bundle | Windows soak and manual-recovery JSON reports can be converted into compact, source-hashed evidence records without exposing private paths by default or treating automation as listening acceptance. |
| AX-TASK-031 | Initial implementation complete | Connect qualification evidence to Agentic status | Agentic Layer | `evidence-status` helper plus optional `--evidence` status/next-action input | Codex can validate and summarize a normalized bundle during orientation, and failed or investigative evidence can block dependent planning without granting automated acceptance. |
| AX-TASK-032 | Initial implementation complete | Add automatic local evidence discovery | Agentic Layer | `evidence-catalog` helper and local-only default directory configuration | Codex can inventory normalized bundles, choose the newest valid one, and automatically include it in routine status and next-action orientation without hardcoded private paths. |
| AX-TASK-033 | Complete | Reconcile current local change batch | Repository | Findings-first reconciliation report and local commit groups | Player path containment and dependency setup are complete, historical `.10` is restored, validation passes, and the approved local commit series is prepared without publishing. |
| AX-TASK-034 | Complete | Add Agentic Layer contract audit | Agentic Layer | `agentic-audit` helper and blocking `ready-check` integration | Command registry/runtime mappings, aliases, JDSP approval flags, profile structure, role sources, and skill-eval fixtures fail closed when their contracts drift. |
| AX-TASK-035 | Complete | Add validated multi-role review records | Agentic Layer | `agent-review --json` and `--output` record generation | Multi-role reviews now have schema versioning, role-source links, decision enums, evidence boundaries, validation checks, and machine-readable output without claiming the draft is evidence. |
| AX-TASK-036 | Complete | Add maintenance-aware next-action planning | Agentic Layer | `next-action --include-maintenance` | Agentic maintenance tasks stay excluded by default, but can be selected explicitly while preserving dirty-tree, evidence, blocker, and approval-gate protections. |
| AX-TASK-037 | Complete | Graduate foundational Agentic contracts | Agentic Layer | Reconciled task state for `AX-TASK-018` through `021` | Command, profile, guardrail, and behavior-eval foundations meet their original acceptance criteria and pass hardened contract, regression, and guard checks. |
| AX-TASK-038 | Complete | Graduate Agentic planning stack | Agentic Layer | Reconciled task state for `AX-TASK-026` through `028` | Local review, machine-readable task state, and next-action planning meet their acceptance criteria and operate together under regression and safety checks. |
| AX-TASK-039 | Complete | Harden and graduate Airwindows Knowledge intake | Knowledge | Automatic index discovery and stricter metadata audit | The real 541-effect index passes pinned-commit, upstream URL, MIT license, canonical-effect, safe-field, relative-path, and checkout-drift checks; queries auto-discover it with explicit opt-out. |

## Current Priority

Recommended next actions:

1. Keep this backlog synchronized when workflow or DSP gates change.
2. Use `docs/axiom-full-system-review-2026-06-08.md` as the current readiness
   review checkpoint.
3. Use the locally installed `$axiom-engineering` skill for new Axiom Codex
   sessions.
4. Use `agentic-audit` as the blocking contract check for `AX-TASK-018`
   through `AX-TASK-021`; add native runtime wrappers only when a supported
   Codex command or subagent mechanism is available.
5. Keep the completed `.11` Sub Harmonics result as a watch item and require a
   new repeatable normal-material problem before proposing `Axiom Clean R012`.
6. Use `task-state` and `next-action` as the machine-readable planning source
   for future helper commands.
7. Use `agent-review --json` or `--output` when a task needs structured role
   findings before implementation or publication review.
8. Use `next-action --include-maintenance` only when intentionally continuing
   Agentic hardening; leave default `next-action` conservative for normal
   planning.

## Progress Notes

- `AX-TASK-001` is implemented across `AGENTS.md`, `CONTRIBUTING.md`,
  `docs/current-state.md`, `docs/profile-matrix.md`, and
  `docs/release-gates.md`.
- `AX-TASK-002` is implemented as `docs/labs-policy.md`; future work may add
  examples after the first real Labs branch.
- `AX-TASK-003` has its initial structure in `docs/knowledge/README.md` and six
  local-source-backed seed notes under `docs/knowledge/`.
- `AX-TASK-004` is implemented as `docs/profile-matrix.md`.
- `AX-TASK-005` is implemented as `docs/listening-protocol.md`; the structured
  record format remains in `docs/listening-records.md`.
- `AX-TASK-006` is implemented in `docs/codex-operating-guide.md`; the issue
  template `external_llm_review.yml` provides the intake form.
- `AX-TASK-007` is implemented across `docs/ai-development-ecosystem.md`,
  `docs/codex-operating-guide.md`, and
  `docs/axiom-operating-system-implementation-plan.md`.
- `AX-TASK-008` is implemented as `docs/release-gates.md`.
- `AX-TASK-009` has a current-facing stale-baseline scan passing locally.
- `AX-TASK-010` is documented in `docs/engineering-harness.md`.
- `AX-TASK-011` has a reusable Markdown template at
  `docs/templates/labs-experiment.md`.
- `AX-TASK-012` has a reusable Markdown template at
  `docs/templates/external-review-triage.md`.
- `AX-TASK-013` is implemented across `docs/codex-operating-guide.md`,
  `docs/labs-policy.md`, `docs/listening-protocol.md`,
  `docs/release-gates.md`, `docs/engineering-harness.md`, and
  `docs/tool-inventory.md`.
- `AX-TASK-015` is implemented with GitHub issue forms under
  `.github/ISSUE_TEMPLATE/`.
- `AX-TASK-016` is implemented as `docs/system-status.md`.
- `AX-TASK-014` is implemented through the required-test columns in
  `docs/profile-matrix.md`.
- `AX-TASK-017` is implemented as `docs/pi-runbooks.md`.
- `AX-TASK-018` through `AX-TASK-021` are complete. Their command registry,
  Codex role profiles, guard-check preflight, and deterministic behavior evals
  now have strict contract validation and adversarial regression coverage.
- `AX-TASK-022` through `AX-TASK-028` come from the 2026-06-08 full-system
  readiness review and represent the next improvement set before any
  `Axiom Clean R012` candidate; `AX-TASK-023` is complete, and `AX-TASK-022`
  now has a completed follow-up map, interpretation record, focused listening
  target, and local-copy listening-record template. `AX-TASK-026` and
  `AX-TASK-027` now provide the first command-backed local review and
  task-state foundation. `AX-TASK-028` adds the first command-backed
  next-action recommendation.
- `AX-TASK-024` is complete with concept notes under
  `docs/knowledge/concepts/` for spatial vocabulary, elevated bass/headroom
  tradeoffs, stage isolation, and profile-scope boundaries.
- `AX-TASK-025` is complete: PR #12 merged the Codex/Knowledge hardening and
  Sub Harmonics follow-up batch after explicit approval.
- `AX-TASK-029` adds Airwindows as an external open-source Knowledge pool with
  repo-safe provenance, a concept taxonomy, local-only canonical metadata
  indexing, automatic query discovery, and strict metadata audits.
- `AX-TASK-030` adds the first Agentic Layer evidence adapter. It normalizes
  Windows host soak and recovery qualification results while preserving the
  distinction between raw report status, interpreted environment warnings, and
  human listening acceptance.
- `AX-TASK-031` makes normalized evidence queryable through `evidence-status`
  and optionally visible to `status-summary` and `next-action`.
- `AX-TASK-032` adds local evidence discovery and a private configuration
  pointer so routine orientation no longer requires a bundle path.
- `AX-TASK-033` is complete: the Player blockers are resolved, historical
  `.10` is restored, and the approved commit series exists locally.
- `AX-TASK-034` hardens `AX-TASK-018` through `AX-TASK-021` with strict
  command, runtime-mapping, profile, approval-boundary, and skill-eval
  contracts. `ready-check` now fails when those contracts drift.
- `AX-TASK-035` replaces the free-form `agent-review` scaffold with a
  validated review-record model that can be rendered as Markdown or emitted as
  JSON for future orchestration.
- `AX-TASK-036` adds explicit maintenance-aware planning so `next-action` can
  guide ongoing Agentic hardening without treating all initial-maintenance work
  as generally actionable.
- `AX-TASK-037` graduates the four foundational Agentic tasks after their
  original acceptance criteria and hardened contract checks passed.
- `AX-TASK-038` graduates the local-review, task-state, and next-action
  planning stack after command-level and regression validation passed.
- `AX-TASK-039` graduates the Airwindows intake after hardening top-level
  metadata checks and automatic standard-index discovery.

## Graduation Checklist For Sound-Changing Work

Before a new EEL candidate is created, verify:

- accepted baseline hash matches `tools/axiom-team/policy.json`;
- strict corpus readiness passes;
- device readiness passes or the limitation is explicitly documented;
- hypothesis is falsifiable;
- changed variables are narrow;
- forbidden scope is written down;
- diagnostic or fixture evidence exists;
- real-JDSP qualification target is selected;
- listening package and listening target are defined.
