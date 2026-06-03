# Axiom Labs Policy

Axiom Labs is the controlled research space for ideas that are not ready for
Axiom Core. Labs exists so the project can explore aggressively without making
the accepted baseline unstable.

## Purpose

Use Labs for:

- temporary DSP fixtures;
- branch-only experiments;
- diagnostic scripts;
- external LLM critique triage;
- research notes that need measurement;
- profile concepts such as Reference, Immersive, Night, or Studio Path.

Labs work is not accepted product behavior. A Labs result becomes eligible for
Core only after it passes the graduation ladder.

## Branch Naming

Use clear branch prefixes:

| Branch Pattern | Use |
| --- | --- |
| `labs/<topic>` | Research-only experiments that may not become a candidate. |
| `codex/labs-<topic>` | Codex-managed Labs documentation or tooling work. |
| `codex/vX.Y.Z-<topic>` | Versioned candidate work after a Labs result justifies promotion. |

Do not use accepted-version names for Labs-only work unless a versioned
candidate has been created through the normal candidate workflow.

## Experiment Record

Every Labs experiment should record:

- observation or idea;
- hypothesis;
- changed variables;
- forbidden scope;
- files or fixtures touched;
- tests run;
- result;
- decision: stop, continue Labs, create candidate, or document no action.

Use the Labs issue template or a short Markdown note before creating a
sound-changing candidate.

## Allowed Work

Labs may include:

- temporary EEL fixtures outside accepted historical scripts;
- controlled copies of accepted scripts for measurement;
- isolated changes to one stage for screening;
- broad research branches when clearly marked as non-candidate work;
- scripts and reports that improve understanding of stage behavior.

## Forbidden Work

Labs must not:

- edit accepted or historical EEL scripts in place;
- merge sound-changing work directly into Core;
- publish a profile as official without qualification and listening acceptance;
- hide multi-variable changes inside a narrow candidate;
- commit captured audio, source music, private manifests, credentials, or local
  run folders;
- commit copyrighted books or long copyrighted excerpts;
- make claims stronger than repository evidence supports.

## Promotion Path

Labs work can move toward Core only through:

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

Promotion requires:

- candidate readiness or an explicitly documented readiness limitation;
- static EEL validation;
- scoped qualification matching the changed stage;
- structured listening package;
- explicit user acceptance;
- qualification document;
- changelog update;
- `tools/axiom-team/policy.json` update when the accepted baseline changes;
- PR review and separate merge approval.

## Stop Conditions

Stop or defer a Labs experiment when:

- the hypothesis is not testable;
- the change affects too many variables to interpret;
- measurement cannot distinguish the claimed effect;
- it requires unsupported host APIs;
- it increases risk without a clear user-facing benefit;
- it would require private or copyrighted material in the public repo.

Stopping a Labs experiment is a valid engineering result. Record why it stopped
so the project does not repeat the same path blindly.
