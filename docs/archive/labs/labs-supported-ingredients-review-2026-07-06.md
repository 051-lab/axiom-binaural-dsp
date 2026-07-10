# Labs Review: Supported Experimental03 Ingredients

Date: 2026-07-06

Related task: `AX-TASK-045`

## Scope

Review the current supported Labs ingredients before deciding whether Axiom
should move toward an `Axiom Clean R012` candidate-readiness plan.

Reviewed chain:

```text
accepted .11
  -> width-profile Labs fixture
  -> width-plus-bass-saturation Labs fixture
```

## Inputs

Accepted baseline:

```text
src/axiom_binaural_dsp_v4.1.4.11.eel
```

Supported width ingredient:

```text
src/labs/axiom_binaural_dsp_v4.1.4.11_width_profile_lab.eel
```

Supported width plus bass-saturation ingredient:

```text
src/labs/axiom_binaural_dsp_v4.1.4.11_width_bass_saturation_lab.eel
```

Source review:

- `labs-experimental03-review-2026-07-06.md`
- `labs-width-profile-listening-summary-2026-07-06.md`
- `labs-bass-saturation-listening-summary-2026-07-06.md`

## Findings

### Width

The width-profile fixture changed only the global side-width default from `135`
to `100`. Preliminary listening classified it as `width lab preferred` because
it moved accepted `.11` toward the desired `experimental03` direction.

This is a clean, low-risk ingredient because it does not add new state,
modulation, STFT behavior, limiter behavior, or host-policy changes.

### Bass Saturation

The width-plus-bass-saturation fixture started from the supported width fixture
and changed only the generated-sub saturation arithmetic. B was selected over
the width-only fixture and is now Labs-supported.

This is a plausible second ingredient, but it carries more risk than the width
change because bass harmonic behavior can affect punch, fatigue, low-mid
clarity, perceived loudness, and limiter interaction.

### Rejected Or Deferred Experimental03 Ideas

The following `experimental03` ideas remain excluded from candidate planning:

- LFO/modulation behavior;
- neuro, entrainment, dopamine, reward, or medical-style claims;
- parameter smoothing from the experimental script;
- STFT release changes;
- output reserve changes;
- internal limiting;
- direct promotion of the full experimental script.

## Decision

The supported Labs ingredients justify a separate `Axiom Clean R012`
candidate-readiness plan.

They do not yet justify creating, promoting, or accepting an official candidate.

## Required Before Candidate Creation

- Write a candidate-readiness plan that defines the exact combined hypothesis.
- Preserve the accepted `.11` baseline unchanged.
- Use the `Axiom Clean R012` naming policy instead of continuing the
  `v4.1.4.x` sequence.
- Re-run static validation on accepted `.11` and both Labs fixtures.
- Capture or reconstruct a structured listening record for the combined result,
  including route, output device, crossfeed state, material classes, and
  artifact notes.
- Define real-JDSP qualification scope before creating any official candidate.
- Get explicit user approval before candidate creation.

## Recommendation

Move next to `AX-TASK-046`: prepare an `Axiom Clean R012` candidate-readiness
plan for the combined width plus bass-saturation idea.

Do not add crest-adaptive STFT, modulation, smoothing, or another DSP ingredient
until the current two supported ingredients have been reviewed through the
candidate-readiness gate.
