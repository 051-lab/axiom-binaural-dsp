# Axiom Operating System Implementation Plan

This is the ordered work plan for making the AI development ecosystem real
inside the repository. It is the practical companion to
`ai-development-ecosystem.md`, `codex-operating-guide.md`, and
`axiom-system-roadmap.md`.

## Working Order

### 1. Make The Operating Framework Official

Purpose:

- Give Codex, Pi, external LLM reviewers, and future contributors one shared
  operating model.

Implementation:

- Keep `docs/ai-development-ecosystem.md` as the role and flow spec.
- Keep `docs/codex-operating-guide.md` as the Codex behavior spec.
- Keep `docs/axiom-system-roadmap.md` as the product/profile boundary map.
- Keep `docs/task-backlog.md` as the lightweight task ledger.
- Link all four from `docs/README.md` and `AGENTS.md`.

Done when:

- A fresh agent can find the operating rules from `docs/README.md`.
- Current-facing docs identify `v4.1.4.11` as the accepted baseline.
- No EEL behavior changes are included in this documentation pass.

### 2. Create The Workflow Intake Layer

Purpose:

- Ensure new ideas enter the project as scoped work instead of loose chat
  history.

Implementation:

- Add GitHub issue templates for:
  - DSP candidate proposals;
  - Labs experiments;
  - external LLM review triage;
  - documentation tasks;
  - qualification or test-suite tasks.
- Each template must capture scope, forbidden scope, evidence, required tests,
  and promotion criteria.

Done when:

- A user or agent can open the right issue type without inventing structure.
- Broad DSP ideas are forced into hypothesis and evidence fields.

### 3. Formalize Axiom Labs

Purpose:

- Keep experimentation active without weakening Axiom Core.

Implementation:

- Add a Labs policy covering:
  - branch naming;
  - experiment templates;
  - allowed and forbidden changes;
  - local artifact boundaries;
  - promotion path from Labs to Core.

Done when:

- A Labs experiment cannot be confused with an accepted candidate.
- Multi-variable experiments are allowed only when clearly marked as research.

### 4. Build Axiom Knowledge Safely

Purpose:

- Let the project benefit from DSP, hearing, music, and audio-engineering
  research without committing protected source material.

Implementation:

- Create a bibliography and research-note structure.
- Store citations, short summaries, concept maps, and Axiom-specific questions.
- Keep books, copied excerpts, private library paths, and copyrighted source
  material outside git.

Done when:

- Knowledge notes can inform tests without becoming unsupported evidence.

### 5. Define Profile Matrix And Promotion Requirements

Purpose:

- Make Core, Reference, Immersive, Night, Studio Path, Labs, Knowledge, and
  Qualification concrete enough for planning.

Implementation:

- Create a matrix with:
  - owner or operating authority;
  - current status;
  - allowed changes;
  - forbidden changes;
  - required tests before promotion.

Done when:

- Future profile work has a destination and gate before code changes start.

Initial status:

- Implemented as `docs/profile-matrix.md`.

### 6. Strengthen Listening And Release Protocols

Purpose:

- Make human listening evidence easier to compare across versions and devices.

Implementation:

- Extend the listening protocol with:
  - material categories;
  - route/device settings;
  - level handling;
  - fatigue and artifact fields;
  - accepted/rejected decision format.
- Add official release gate checklists for accepted EEL scripts.

Done when:

- A candidate cannot reach the accepted baseline without static checks,
  qualification, listening acceptance, changelog, qualification docs, policy
  hash, PR, and merge approval.

Initial status:

- Listening setup and decision rules are implemented as
  `docs/listening-protocol.md`.
- Publication and accepted-baseline promotion gates are implemented as
  `docs/release-gates.md`.

### 7. Improve Pi Runbooks

Purpose:

- Let Pi sessions act like a repeatable execution team rather than ad hoc
  terminal windows.

Implementation:

- Add runbooks for:
  - baseline audit;
  - candidate investigation;
  - Labs experiment;
  - qualification run;
  - advisory-review triage;
  - repository housekeeping.

Done when:

- A Pi session can be started with a narrow mission and return concrete
  evidence without needing extensive context recovery.

Initial status:

- Implemented as `docs/pi-runbooks.md`.

### 8. Add A System Status Dashboard

Purpose:

- Give every agent one current-state page before choosing work.

Implementation:

- Add or generate a status document covering:
  - accepted baseline;
  - active candidate;
  - open investigations;
  - latest qualification state;
  - roadmap status;
  - recommended next work.

Done when:

- A fresh agent can answer "what should we do next?" without reading every
  document in the repository.

Initial status:

- Implemented as `docs/system-status.md`.

## Current First Target

The first implementation target is the workflow intake layer plus Labs policy.
That gives the system controlled entry points for new ideas, advisory reviews,
and experiments before any new DSP work is attempted.
