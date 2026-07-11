# Axiom Task Backlog

This backlog turns the AI ecosystem and system-roadmap documents into concrete
repository work. Items are lightweight task briefs; create GitHub issues when a
task is ready for scheduling or delegation.

## Backlog

| ID | Status | Task | Area | Output | Acceptance Criteria |
| --- | --- | --- | --- | --- | --- |
| AX-TASK-001 | Complete | Formalize Axiom Core identity | Core | Core policy note or README section | Accepted baseline, host ownership, and no-in-place-edit rules are visible from the starting docs. |
| AX-TASK-002 | Complete | Create Labs branch policy | Labs | Branch policy doc or CONTRIBUTING section | Labs branches have naming, scope, artifact, and promotion rules. |
| AX-TASK-003 | Parked: seed notes added | Create Knowledge Base bibliography notes | Knowledge | `docs/knowledge/` seed source notes | Seed notes and selected concept notes exist; further Knowledge expansion is parked and is not an audit blocker. |
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
| AX-TASK-030 | Complete | Add qualification evidence ingestion | Agentic Layer | `evidence-ingest` helper and normalized local evidence bundle | Windows soak and manual-recovery reports convert into source-hashed, path-safe records with explicit automation/listening boundaries and fail-closed unsupported schemas. |
| AX-TASK-031 | Complete | Connect qualification evidence to Agentic status | Agentic Layer | `evidence-status` plus status/next-action integration | Validated bundle decisions appear in routine orientation; failed or investigative evidence blocks dependent planning without granting acceptance. |
| AX-TASK-032 | Complete | Add automatic local evidence discovery | Agentic Layer | `evidence-catalog` and local-only default configuration | The newest valid bundle is discovered automatically, private paths stay hidden, configured-state reporting is truthful, and explicit evidence opt-out remains available. |
| AX-TASK-033 | Complete | Reconcile current local change batch | Repository | Findings-first reconciliation report and local commit groups | Player path containment and dependency setup are complete, historical `.10` is restored, validation passes, and the approved local commit series is prepared without publishing. |
| AX-TASK-034 | Complete | Add Agentic Layer contract audit | Agentic Layer | `agentic-audit` helper and blocking `ready-check` integration | Command registry/runtime mappings, aliases, JDSP approval flags, profile structure, role sources, and skill-eval fixtures fail closed when their contracts drift. |
| AX-TASK-035 | Complete | Add validated multi-role review records | Agentic Layer | `agent-review --json` and `--output` record generation | Multi-role reviews now have schema versioning, role-source links, decision enums, evidence boundaries, validation checks, and machine-readable output without claiming the draft is evidence. |
| AX-TASK-036 | Complete | Add maintenance-aware next-action planning | Agentic Layer | `next-action --include-maintenance` | Agentic maintenance tasks stay excluded by default, but can be selected explicitly while preserving dirty-tree, evidence, blocker, and approval-gate protections. |
| AX-TASK-037 | Complete | Graduate foundational Agentic contracts | Agentic Layer | Reconciled task state for `AX-TASK-018` through `021` | Command, profile, guardrail, and behavior-eval foundations meet their original acceptance criteria and pass hardened contract, regression, and guard checks. |
| AX-TASK-038 | Complete | Graduate Agentic planning stack | Agentic Layer | Reconciled task state for `AX-TASK-026` through `028` | Local review, machine-readable task state, and next-action planning meet their acceptance criteria and operate together under regression and safety checks. |
| AX-TASK-039 | Complete | Harden and graduate Airwindows Knowledge intake | Knowledge | Automatic index discovery and stricter metadata audit | The real 541-effect index passes pinned-commit, upstream URL, MIT license, canonical-effect, safe-field, relative-path, and checkout-drift checks; queries auto-discover it with explicit opt-out. |
| AX-TASK-040 | Complete | Harden and graduate qualification evidence stack | Agentic Layer | Reconciled ingestion, status, and discovery workflow | The real Windows host bundle validates with two source-hashed records, automatic orientation works, configured-directory state is accurate, and evidence remains distinct from listening or release approval. |
| AX-TASK-041 | Complete | Complete Agentic review-record lifecycle | Agentic Layer | `agent-review-status` and `next-action --review` | Completed review records require scope, findings, evidence references, and non-draft decisions; private paths fail validation; bounded decisions inform planning without granting JDSP, publication, candidate, merge, or baseline authority. |
| AX-TASK-042 | Complete | Add bounded subagent operating model | Agentic Layer | Subagent workflow doc plus optional review provenance validation | Codex remains coordinator/integrator, subagents are advisory by default, Pi keeps real-JDSP/candidate/publication ownership, and review records can capture safe subagent provenance without raw transcripts or private paths. |
| AX-TASK-043 | Complete: Labs-supported | Triage experimental03 into controlled Labs hypotheses | Labs | `docs/archive/labs/` records, `templates/width-profile-listening-record-2026-07-06.json`, and `src/labs/axiom_binaural_dsp_v4.1.4.11_width_profile_lab.eel` | The width-profile step is documented as a Labs-supported contributor toward the `experimental03` target without promotion to `Axiom Clean R012`. |
| AX-TASK-044 | Complete: Labs-supported | Isolate experimental03 bass-saturation contribution | Labs | `docs/archive/labs/` records and `src/labs/axiom_binaural_dsp_v4.1.4.11_width_bass_saturation_lab.eel` | The bass-harmonic/saturation idea is isolated separately from width, STFT, modulation, and smoothing; B was selected as a Labs-supported ingredient without candidate or baseline promotion. |
| AX-TASK-045 | Complete | Review supported experimental03 ingredients together | Labs | `docs/archive/labs/labs-supported-ingredients-review-2026-07-06.md` | The combined width plus bass-saturation result is reviewed against accepted `.11`, unsafe `experimental03` ideas remain excluded, and the next step is candidate-readiness planning rather than candidate creation. |
| AX-TASK-046 | Complete: plan only | Prepare Axiom Clean R012 candidate-readiness plan | Qualification | `axiom-clean-r012-candidate-readiness-plan-2026-07-08.md` | The plan defines the exact hypothesis, filename policy, static checks, listening-record needs, real-JDSP scope, and approval gates before any official candidate is created. |
| AX-TASK-047 | Complete | Simplify active Axiom system guidance | Docs | `AXIOM.md`, `docs/dsp-change-workflow.md`, `docs/archive/README.md`, and updated status/index docs | A fresh agent or user can start from one plain-language front door, historical docs are archived, and no DSP/candidate state changes were made. |

## Current Priority

Recommended next actions:

1. Use `AXIOM.md` as the plain-language entry point for what Axiom is and what
   agents should optimize for.
2. Treat `axiom-state.json` as operational truth: R011 is accepted and R012 is
   the active unqualified candidate.
3. Plan scoped R012 qualification without modifying R011 or R012 DSP.
4. Use `task-state`, `next-action`, `guard-check`, and `ready-check` as views or
   validators of the authoritative state, not separate project-state sources.
5. Use archived Labs/review/planning documents as history only unless a future
   task intentionally promotes them back into active guidance.

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
- `AX-TASK-007` is implemented across `docs/codex-operating-guide.md` and
  historical planning records now stored under `docs/archive/planning/`.
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
- `AX-TASK-040` graduates `AX-TASK-030` through `032` after real-bundle
  ingestion, validation, status integration, discovery, and local configuration
  checks passed.
- `AX-TASK-041` and `AX-TASK-042` complete the first review-record lifecycle
  and subagent workflow boundary. Future real subagent runs can be represented
  with optional safe provenance metadata while remaining non-authoritative
  planning artifacts.
- `AX-TASK-043` starts the next Knowledge-driven Labs lane by reviewing
  `experimental03` against the accepted `.11` baseline and defining a
  width-profile isolation plan and Labs fixture before any `Axiom Clean R012`
  work.
- `AX-TASK-043` is complete as a Labs-supported width result. The width step
  should remain a supported ingredient, not an accepted baseline.
- `AX-TASK-044` is complete as a Labs-supported bass-saturation result. B, the
  width-plus-bass-saturation fixture, was selected as preferred over the
  width-only fixture, but no candidate or accepted-baseline promotion has been
  made.
- `AX-TASK-045` reviews both supported `experimental03` ingredients together
  and concludes that candidate-readiness planning is justified, while candidate
  creation remains gated behind a separate approved plan.
- `AX-TASK-046` is planned as that candidate-readiness bridge for a possible
  `Axiom Clean R012`; it is now complete as a plan-only gate.
- The 2026-07-08 audit standstill parks `AX-TASK-003`, closes `AX-TASK-046`,
  and intentionally stops before candidate creation.
- `AX-TASK-047` simplifies the active guidance layer after the user-identified
  complexity problem: `AXIOM.md` is now the front door, DSP change work has a
  short workflow, and historical reviews/plans/Labs notes are archived.
- On 2026-07-10 the owner confirmed that subsequent R012 candidate creation was
  authorized. This backlog remains historical task metadata; current candidate
  state and next action come from `axiom-state.json`.

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
