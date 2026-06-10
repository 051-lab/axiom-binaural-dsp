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
| AX-TASK-018 | Initial implementation complete | Define Axiom Codex command surface | Codex | `tools/axiom-codex/command_surface.json` and `command-surface` helper | Repeated workflows such as status, ready-check, role review, Knowledge lookup, Pi handoff, guard check, skill eval, and session-log update have clear trigger names, inputs, outputs, and safety boundaries. |
| AX-TASK-019 | Initial implementation complete | Create role-specific Codex agent profiles | Codex | `tools/axiom-codex/agent_profiles/` and `agent-profiles` helper | DSP architecture, EEL safety, measurement, qualification, release, tooling, research, safety, implementation, and coordination roles map to the existing role registry and have limited responsibilities. |
| AX-TASK-020 | Initial implementation complete | Add automated guardrails for unsafe Axiom actions | Codex | `guard-check` helper and unit tests | Historical EEL edits, private artifact paths, source audio, captured WAVs, local manifests, credentials, and unsupported baseline changes are blocked or flagged before publication. |
| AX-TASK-021 | Initial implementation complete | Add Axiom skill behavior evals | Codex | `tools/axiom-codex/skill_eval_cases.json` and `skill-eval` helper | The Axiom skill source is checked against representative prompts for status inspection, DSP-safety refusal, Pi handoff, Knowledge lookup, release-gate review, private-artifact handling, and session-log refresh. |
| AX-TASK-022 | Listening package prepared | Close `.11` Sub Harmonics follow-up | Qualification | Updated investigation gate, summarized evidence, and local listening package workflow | The corrected and confirmatory `+4 dB`, `+10 dB`, and `+12 dB` Sub Harmonics maps completed through Pi/JDSP and are summarized in `docs/sub-harmonics-follow-up-v4.1.4.11.md`. `docs/sub-harmonics-interpretation-v4.1.4.11.md` keeps `.11` accepted and blocks `.12` for now. `docs/sub-harmonics-listening-target-v4.1.4.11.md` defines the focused accepted-`.11` listening check, including local filtered A/B package generation. |
| AX-TASK-023 | Complete | Add structured spatial listening vocabulary | Qualification | Listening-record guidance update | Listening records distinguish center image, lateral spread, localization blur, depth impression, bass-image coupling, fatigue, and route context. |
| AX-TASK-024 | Complete | Create Knowledge concept notes from seed sources | Knowledge | Short concept notes tied to Axiom questions | Seed bibliography now has focused concept notes for spatial listening vocabulary, elevated bass/headroom tradeoffs, stage isolation, and profile-scope boundaries without copying source text or claiming research proves Axiom behavior. |
| AX-TASK-025 | Complete | Review and merge PR #12 | Repository | Merged Codex/Knowledge hardening PR | PR #12 was reviewed, validation passed, and the PR was merged after explicit approval. |
| AX-TASK-026 | Initial implementation complete | Add consolidated local review/check command | Codex | `local-review` helper command | Future full-system reviews can run the standard local evidence snapshot with one safe, non-JDSP command that covers git state, accepted baseline, changed paths, guard-check, ready-check, Knowledge audit, Python tests, Node harness tests, and recommended next action. |
| AX-TASK-027 | Initial implementation complete | Add machine-readable task state | Codex | `tools/axiom-codex/task_state.json` and `task-state` helper | Agentic planning can validate and summarize task status, blocked state, approval needs, and next actions without parsing only Markdown tables. |
| AX-TASK-028 | Initial implementation complete | Add next-action helper | Codex | `next-action` helper command | Codex can recommend the next safe Axiom work item from task-state metadata, current working-tree state, blockers, and approval gates without running JDSP or bypassing human decisions. |

## Current Priority

Recommended next actions:

1. Keep this backlog synchronized when workflow or DSP gates change.
2. Use `docs/axiom-full-system-review-2026-06-08.md` as the current readiness
   review checkpoint.
3. Use the locally installed `$axiom-engineering` skill for new Axiom Codex
   sessions.
4. Treat `AX-TASK-018` through `AX-TASK-021` as initial infrastructure; future
   work can add native runtime wrappers only when a supported Codex command or
   subagent mechanism is available.
5. Run focused accepted-`.11` listening from the filtered `+4` versus `+10`
   and `+4` versus `+12` local A/B packages before proposing a `.12`
   hypothesis.
6. Address the remaining `AX-TASK-022` listening work before proposing `.12`;
   use `task-state` and `next-action` as the machine-readable planning source
   for future helper commands.

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
- `AX-TASK-018` through `AX-TASK-021` have initial repo-tracked
  implementations: command registry, Codex role profiles, guard-check
  preflight, and deterministic skill behavior eval fixtures.
- `AX-TASK-022` through `AX-TASK-028` come from the 2026-06-08 full-system
  readiness review and represent the next improvement set before any `.12`
  candidate; `AX-TASK-023` is complete, and `AX-TASK-022` now has a completed
  follow-up map, interpretation record, focused listening target, and local-copy
  listening-record template. `AX-TASK-026` and `AX-TASK-027` now provide the
  first command-backed local review and task-state foundation. `AX-TASK-028`
  adds the first command-backed next-action recommendation.
- `AX-TASK-024` is complete with concept notes under
  `docs/knowledge/concepts/` for spatial vocabulary, elevated bass/headroom
  tradeoffs, stage isolation, and profile-scope boundaries.
- `AX-TASK-025` is complete: PR #12 merged the Codex/Knowledge hardening and
  Sub Harmonics follow-up batch after explicit approval.

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
