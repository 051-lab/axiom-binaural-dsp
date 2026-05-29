# Axiom Candidate Readiness

## Purpose

The readiness gate answers one question: is the project prepared to propose a
new sound-changing candidate?

It does not create a candidate and does not approve DSP changes. It checks
whether the evidence foundations are ready enough to begin a scoped candidate
discussion.

## Command

```bash
scripts/evaluate_axiom_candidate_readiness.py \
  --json /tmp/axiom-candidate-readiness.json \
  --markdown /tmp/axiom-candidate-readiness.md
```

The default policy is `tools/axiom-team/policy.json`. The default material
manifest is the current configured CC0 manifest path, and the default device
matrix path is `~/.local/state/axiom-engineering/device-matrix.json`.
Use `--material-manifest` when testing a local enriched manifest draft before
promoting it to the configured manifest path.

## Required Passes

The report is `READY` only when:

- the accepted baseline hash matches policy;
- the material manifest passes strict metadata and full taxonomy coverage;
- the device matrix passes strict route coverage with complete setup checks.

Any failure or warning blocks candidate creation. This is intentional. A new
DSP candidate should come from a clean evidence foundation, not from momentum.
The current local state may report `BLOCKED` until the enriched corpus metadata
and device matrix are filled in outside the repository.

## Boundary

Readiness is not listening acceptance. After readiness passes, the next
candidate still needs:

- a falsifiable hypothesis;
- a measured target;
- a scoped edit boundary;
- real-host qualification;
- level-controlled listening;
- explicit human acceptance.
