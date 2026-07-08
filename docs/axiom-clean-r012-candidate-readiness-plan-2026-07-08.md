# Axiom Clean R012 Candidate-Readiness Plan

Date: 2026-07-08

Related task: `AX-TASK-046`

## Purpose

This plan defines what would be required before creating an official
`Axiom Clean R012` candidate from the two currently supported Labs ingredients:

```text
width-profile change
  plus
interpolated bass-saturation change
```

This document does not create a candidate, does not alter the accepted
baseline, and does not approve promotion.

## Current Baseline

Accepted baseline:

```text
Axiom Clean R011
src/axiom_binaural_dsp_v4.1.4.11.eel
```

Supported Labs ingredients:

```text
src/labs/axiom_binaural_dsp_v4.1.4.11_width_profile_lab.eel
src/labs/axiom_binaural_dsp_v4.1.4.11_width_bass_saturation_lab.eel
```

## Candidate Hypothesis

An `Axiom Clean R012` candidate may be justified if the combined width plus
bass-saturation result can preserve the accepted `.11` safety and host policy
while improving musical coherence toward the preferred `experimental03` target.

Expected audible direction:

- more coherent stereo width than accepted `.11`;
- smoother or fuller generated bass than the width-only fixture;
- clean kick impact;
- stable bass-image anchoring;
- no added fatigue, pumping, dullness, smear, fuzz, image movement, or level
  retreat.

## Candidate Boundary

Allowed candidate changes:

- start from accepted `.11`;
- set the global side-width default to the supported width value;
- add only the supported interpolated generated-sub saturation arithmetic;
- preserve accepted bass extraction filters and harmonic high-pass filters;
- preserve accepted exciter, STFT, output reserve, host limiter ownership, and
  crossfeed ownership.

Forbidden candidate changes:

- no direct promotion of `experimental03`;
- no LFO or modulation behavior;
- no neuro, entrainment, dopamine, reward, or medical-style claims;
- no parameter smoothing imported from the experimental script;
- no STFT release changes;
- no output reserve changes;
- no internal limiter;
- no accepted or historical EEL edits in place.

## Naming

If a candidate is created after explicit approval, use:

```text
Candidate: Axiom Clean R012
File: src/axiom_clean_r012.eel
```

Do not create `src/axiom_binaural_dsp_v4.1.4.12.eel`.

## Required Evidence Before Candidate Creation

Candidate creation should not proceed until these are true or explicitly
documented as limitations:

- accepted `.11` static validation passes;
- width fixture static validation passes;
- width-plus-bass-saturation fixture static validation passes;
- structured or reconstructed listening notes capture route, device, crossfeed
  state, material classes, and artifact observations;
- candidate-readiness status is reviewed, including any local manifest or device
  limitations;
- real-JDSP qualification scope is selected;
- user gives explicit approval to create the candidate file.

## Proposed Validation Commands

```bash
scripts/validate_axiom_static.sh src/axiom_binaural_dsp_v4.1.4.11.eel
scripts/validate_axiom_static.sh src/labs/axiom_binaural_dsp_v4.1.4.11_width_profile_lab.eel
scripts/validate_axiom_static.sh src/labs/axiom_binaural_dsp_v4.1.4.11_width_bass_saturation_lab.eel
python3 -m unittest tests.test_axiom_codex_helper.AxiomCodexHelperTests
python3 tools/axiom-codex/axiom_codex.py guard-check
python3 tools/axiom-codex/axiom_codex.py ready-check
```

Candidate-readiness command, when the required local material/device state is
available:

```bash
scripts/evaluate_axiom_candidate_readiness.py \
  --json /tmp/axiom-r012-candidate-readiness.json \
  --markdown /tmp/axiom-r012-candidate-readiness.md
```

## Candidate-Creation Gate

Creating `src/axiom_clean_r012.eel` requires explicit user approval after this
plan is reviewed.

If approved later, the candidate should be created as a new file from accepted
`.11`, applying only the two supported Labs ingredients. The resulting candidate
must then pass static validation before any qualification or listening work.

## Standstill Decision

For the audit halt, stop here.

The project has a clear candidate-readiness plan, no active candidate, no
accepted-baseline change, and no pending DSP implementation that must be
completed before the next project shift.
