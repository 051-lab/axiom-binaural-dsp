# Axiom Release Gates

This document defines what must be true before repository changes are
published or promoted. It separates documentation, tooling, Labs, candidate,
and accepted-baseline gates.

## Gate Levels

| Level | Scope | May Change DSP Sound? | Required Approval |
| --- | --- | --- | --- |
| Documentation | Public docs, templates, issue forms | No | Normal review |
| Tooling | Scripts, tests, harness, generators | No, unless explicitly a render path change | Normal review plus relevant tests |
| Labs | Research branches, fixtures, diagnostics | Not accepted behavior | Review as research |
| Candidate | New versioned EEL script for listening | Yes | Qualification plus user listening |
| Accepted Baseline | Policy update and official promotion | Yes | Explicit user acceptance, PR, merge approval |

## Documentation Gate

Required:

- `git diff --check`;
- relative links resolve where possible;
- no private paths unless intentionally local-only and documented;
- no copied protected content;
- no claims stronger than evidence supports;
- docs index updated when a durable document is added.

Documentation changes do not require EEL validation unless they change DSP
instructions or accepted-baseline references.

## Tooling Gate

Required:

- relevant syntax checks;
- relevant unit tests;
- no untracked local artifacts committed accidentally;
- clear side-effect documentation when a tool touches JDSP, Pulse, files, or
  host settings;
- generated reports and captures stay local unless summarized.

For real-host runners, document whether the command is serialized and whether
it mutates JDSP settings.

## Labs Gate

Required:

- Labs issue or experiment note;
- hypothesis and changed variables;
- forbidden scope;
- branch or fixture clearly marked as Labs;
- local artifact boundary;
- result and decision: stop, continue Labs, create candidate, or no action.

Labs work cannot update `tools/axiom-team/policy.json` as an accepted baseline
change and cannot overwrite historical EEL files.

## Candidate Creation Gate

Required before creating a sound-changing candidate:

- accepted baseline hash matches policy;
- candidate readiness has passed or limitations are explicitly documented;
- hypothesis is falsifiable;
- edit boundary is scoped;
- listening target is defined;
- diagnostic or fixture evidence exists;
- required tests are known.

Candidate creation must make a new versioned EEL file. Do not edit the accepted
baseline or historical versions in place.

## Candidate Qualification Gate

Required before formal listening:

- static EEL validation passes;
- tooling tests relevant to the changed path pass;
- real-JDSP qualification passes or returns a safe explicit investigation
  status;
- local listening package or comparison plan exists;
- any expected differences are documented;
- any non-passing measurement is explained before listening.

Measurement does not replace listening. It decides whether listening is worth
doing.

## Listening Acceptance Gate

Required before promotion:

- structured listening record or sanitized summary;
- comparison version identified;
- host settings recorded;
- route/device class recorded;
- material classes documented;
- acceptance or rejection rationale written by the user.

If the decision is `needs_retest` or `no_decision`, the candidate cannot be
promoted.

## Accepted-Baseline Promotion Gate

Required before merging an official accepted script:

- versioned EEL candidate file;
- qualification document for the new version;
- `CHANGELOG.md` update;
- `tools/axiom-team/policy.json` updated to the new accepted path and SHA-256;
- README, `AGENTS.md`, and current-state docs updated if baseline references
  change;
- host policy documented;
- explicit user acceptance;
- PR review;
- separate merge approval.

After merge:

- local `main` should fast-forward to `origin/main`;
- the active Liveprog symlink or deployment helper may be updated locally;
- the system status dashboard should be refreshed;
- old candidates remain preserved as historical artifacts.

## Stop Conditions

Stop the release path when:

- scope expands beyond the issue or candidate hypothesis;
- a real-host measurement clips normal material unexpectedly;
- the route or capture is silent or unreliable;
- candidate readiness is blocked and the limitation is not documented;
- user listening rejects the candidate;
- publication would include private audio, manifests, captures, credentials, or
  protected source text.
