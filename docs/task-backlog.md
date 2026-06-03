# Axiom Task Backlog

This backlog turns the AI ecosystem and system-roadmap documents into concrete
repository work. Items are lightweight task briefs; create GitHub issues when a
task is ready for scheduling or delegation.

## Backlog

| ID | Task | Area | Output | Acceptance Criteria |
| --- | --- | --- | --- | --- |
| AX-TASK-001 | Formalize Axiom Core identity | Core | Core policy note or README section | Accepted baseline, host ownership, and no-in-place-edit rules are visible from the starting docs. |
| AX-TASK-002 | Create Labs branch policy | Labs | Branch policy doc or CONTRIBUTING section | Labs branches have naming, scope, artifact, and promotion rules. |
| AX-TASK-003 | Create Knowledge Base bibliography notes | Knowledge | `docs/knowledge/` index or bibliography doc | Notes contain citations and summaries only, with no copyrighted book contents or private paths. |
| AX-TASK-004 | Create profile matrix | System | Profile matrix doc or table | Core, Reference, Immersive, Night, Studio Path, Labs, Knowledge, and Qualification are mapped to owner, status, allowed changes, and tests. |
| AX-TASK-005 | Add listening protocol | Qualification | Listening protocol doc or extension to `listening-records.md` | Protocol defines material choice, level handling, device route, fatigue notes, comparison target, and acceptance decision format. |
| AX-TASK-006 | Document advisory LLM review flow | Codex | Review-flow doc or operating-guide section | External LLM feedback has a repeatable path from critique to issue, research note, fixture, or rejection. |
| AX-TASK-007 | Define candidate graduation ladder | Qualification | Candidate ladder doc or roadmap section | Every DSP idea must pass idea, note, fixture, offline analysis, real-JDSP test, listening candidate, qualification, and acceptance stages. |
| AX-TASK-008 | Define release gates for official scripts | Core | Release gate checklist | Promotion requires qualification doc, changelog, policy hash, listening acceptance, PR, and merge approval. |
| AX-TASK-009 | Sync stale baseline references | Docs | Documentation cleanup PR | No current-facing doc identifies `.10` or earlier as the accepted baseline. |
| AX-TASK-010 | Add targeted Sub Harmonics map docs | Qualification | Harness command documentation | `map-sub-gain` targeted options are documented for CLI and Pi use. |
| AX-TASK-011 | Create Labs experiment template | Labs | Markdown template | Experiments record hypothesis, changed variables, forbidden scope, tests, result, and promotion decision. |
| AX-TASK-012 | Create external-review triage template | Codex | Markdown template | Advisory reviews are summarized into claim, evidence need, action, and disposition. |
| AX-TASK-013 | Define local-only artifact policy checklist | Qualification | Checklist or docs addition | Captures, source music, manifests, credentials, local HTML, and generated reports have clear storage rules. |
| AX-TASK-014 | Create profile-specific test requirements | Qualification | Matrix or per-profile checklist | Each future profile has required static, offline, real-host, and listening checks before promotion. |
| AX-TASK-015 | Build issue templates for DSP candidates and docs work | Repository | `.github/ISSUE_TEMPLATE/` updates | Issues capture scope, forbidden scope, evidence, tests, and release impact. |
| AX-TASK-016 | Add system status dashboard | Repository | `docs/system-status.md` | A fresh agent can see accepted baseline, active candidate, open investigations, roadmap state, and next work. |
| AX-TASK-017 | Add Pi runbooks | Harness | `docs/pi-runbooks.md` | Pi/Codex sessions have repeatable missions for audit, investigations, Labs, qualification, advisory triage, housekeeping, and publication. |

## Immediate Priority

Recommended next actions:

1. Commit and publish the documentation and workflow-intake changes after
   review.
2. Commit initial Knowledge, Labs, and external-review templates after review.
3. Add concrete examples only after the first real Knowledge note or Labs
   experiment exists.

## Progress Notes

- `AX-TASK-002` is implemented as `docs/labs-policy.md`; future work may add
  examples after the first real Labs branch.
- `AX-TASK-003` has its initial structure in `docs/knowledge/README.md`.
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
- `AX-TASK-015` is implemented with GitHub issue forms under
  `.github/ISSUE_TEMPLATE/`.
- `AX-TASK-016` is implemented as `docs/system-status.md`.
- `AX-TASK-014` is implemented through the required-test columns in
  `docs/profile-matrix.md`.
- `AX-TASK-017` is implemented as `docs/pi-runbooks.md`.

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
