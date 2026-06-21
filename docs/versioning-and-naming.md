# Axiom Versioning And Naming

## Purpose

This document defines how future Axiom EEL iterations should be named. It
exists to avoid confusion from legacy identifiers such as `v4.1.4.10`, which
can be visually misread as being equivalent to `v4.1.4.1`.

This is a naming policy only. It does not rename historical EEL files, change
DSP behavior, promote a baseline, or alter accepted-baseline policy.

## Historical Files Stay Fixed

Existing EEL filenames remain immutable evidence anchors:

| Human-facing label | Legacy ID | Historical file |
| --- | --- | --- |
| Axiom Clean R011 | `v4.1.4.11` | `src/axiom_binaural_dsp_v4.1.4.11.eel` |
| Axiom Clean R010 | `v4.1.4.10` | `src/axiom_binaural_dsp_v4.1.4.10.eel` |

Do not rename historical EEL files or their qualification records. Existing
docs, reports, policy hashes, local runs, and listening records may reference
the legacy IDs because those names were the source-of-truth identifiers when
the evidence was created.

## Future Naming Rule

Future sound-changing Axiom Clean candidates should use the release-label
scheme:

```text
Axiom Clean R012
Axiom Clean R013
Axiom Clean R014
```

The matching future EEL filenames should use lowercase, zero-padded release
numbers:

```text
src/axiom_clean_r012.eel
src/axiom_clean_r013.eel
src/axiom_clean_r014.eel
```

The next sound-changing candidate after the accepted `v4.1.4.11` baseline
should therefore be `Axiom Clean R012`, not `v4.1.4.12`.

## Display Rule

User-facing docs, player surfaces, status summaries, and future qualification
records should show the readable release label first and the legacy ID only
when needed for historical traceability.

Preferred current-baseline display:

```text
Accepted baseline: Axiom Clean R011
Legacy ID: v4.1.4.11
File: src/axiom_binaural_dsp_v4.1.4.11.eel
```

Preferred future-candidate display:

```text
Candidate: Axiom Clean R012
File: src/axiom_clean_r012.eel
```

## Release And Evidence Rules

- Historical files remain immutable.
- A sound-changing candidate still requires a scoped hypothesis, measurement
  support, listening target, qualification, and human listening acceptance.
- Accepted-baseline promotion still requires updating the policy anchor,
  qualification record, changelog, README, current-state docs, and system
  status dashboard.
- If tooling still expects legacy filename patterns when `Axiom Clean R012` is
  created, update the tooling then rather than continuing the confusing
  `v4.1.4.x` sequence.

## Bottom Line

Use `Axiom Clean R011` as the human-facing name for the current accepted
baseline, while preserving `v4.1.4.11` as its historical legacy ID. Future EEL
iterations should continue as `Axiom Clean R012`, `Axiom Clean R013`, and so on.
