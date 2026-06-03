# Contributing to Axiom Binaural DSP

This repository develops a JamesDSP EEL2 Liveprog enhancement core and the
measurement tools used to qualify changes.

## Start Here

1. Read `AGENTS.md` for mandatory EEL2/JDSP constraints.
2. Read `docs/architecture.md` for the current signal chain and host ownership.
3. Read `docs/JDSP4Linux_Knowledge_Base.md` before using host APIs or preset keys.
4. Preserve accepted source versions; sound-changing work gets a new `.eel` version.
5. Update `CHANGELOG.md` and qualification documentation when a result is accepted.

## Current Baseline

The accepted source is `src/axiom_binaural_dsp_v4.1.4.11.eel`. It is
device-neutral: crossfeed is not part of Axiom. The only terminal limiter in the
qualified chain is JDSP's limiter, enabled at `-1.00 dB` threshold, `60 ms`
release, and `0 dB` postgain.

## What May Change

| Path | Purpose |
|------|---------|
| `src/*.eel` | Versioned EEL2 DSP artifacts |
| `scripts/*.py`, `scripts/*.sh` | Analysis, host render, reload, and qualification tools |
| `tests/*.py` | Deterministic tests for tooling and analysis rules |
| `presets/axiom-preset.conf` | Full JDSP `audio.conf`-style baseline template |
| `docs/*.md`, `README.md`, `CHANGELOG.md` | Architecture, usage, and evidence record |

Do not commit private audio, downloaded program material, local manifests,
capture WAVs, or generated reports.

## EEL2 Requirements

- Never assign to `$pi`, `$e`, or `$eps`.
- Do not use `%`, `FractionalDelayLineInit`, `pfb_init`, or
  `InitPolyphaseFilterbank`.
- Use `this.*` only inside `function()` blocks and declare locals with
  `local(...)`.
- Initialize all processing state in `@init`.
- Keep STFT allocation blocks disjoint and use the documented STFT signatures.
- Keep `spl0 = out_L;` and `spl1 = out_R;` as the final two lines of `@sample`.

## Qualification

Run static and tooling checks before a commit:

```bash
scripts/validate_axiom_static.sh src/axiom_binaural_dsp_v4.1.4.11.eel
python3 -m unittest discover -s tests -p 'test_*.py'
git diff --check
```

To reproduce the historical `.8` versus `.9` reserve qualification:

```bash
scripts/run_jdsp_wsl_qualification.py \
  src/axiom_binaural_dsp_v4.1.4.8.eel \
  src/axiom_binaural_dsp_v4.1.4.9.eel \
  /tmp/axiom-v48-v49-wsl-qualification
```

Use locally controlled or freely licensed material only through manifests kept
outside this repository. Device listening remains the acceptance step after the
measurement suite clears integrity and headroom regressions.

## Pi Engineering Harness

Use `scripts/axiom_team.sh` for agent-coordinated DSP experiments. The harness
creates versioned candidates in external worktrees and permits local commits
only after the real-host qualification gate permits evaluation. It never
replaces device listening acceptance, and push and merge each require a
separate user confirmation. Its full operating policy is documented in
`docs/engineering-harness.md`.

## Labs And Issue Intake

Use `docs/labs-policy.md` for research branches, temporary fixtures, and
experiments that are not ready for Axiom Core. Labs work may explore, but it
does not become accepted behavior without the normal graduation ladder,
qualification, listening acceptance, and PR review.

Use the GitHub issue templates for DSP candidates, Labs experiments, external
LLM review triage, documentation tasks, and qualification/test-suite work.
Each issue should define scope, forbidden scope, evidence, and required tests.

## Release Gates

Use `docs/release-gates.md` before publishing or promoting a change. A
sound-changing candidate requires candidate readiness, scoped qualification,
structured listening acceptance, updated qualification docs, changelog,
policy hash, PR review, and separate merge approval. Use
`docs/listening-protocol.md` and `docs/listening-records.md` for listening
evidence.

## Commit Format

Use Conventional Commits:

```text
type(scope): short imperative summary
```

Typical types are `feat`, `fix`, `perf`, `refactor`, `test`, `docs`, and
`chore`. Typical scopes are `dsp`, `testbench`, `preset`, `docs`, and `host`.

*Maintained by 051-lab - Axiom Binaural DSP v4.1.4.11*
