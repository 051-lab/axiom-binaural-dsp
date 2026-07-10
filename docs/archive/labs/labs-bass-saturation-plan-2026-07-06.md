# Labs Plan: Bass-Saturation Isolation

Date: 2026-07-06

Related task: `AX-TASK-044`

Baseline:

- accepted baseline: `src/axiom_binaural_dsp_v4.1.4.11.eel`
- supported Labs ingredient:
  `src/labs/axiom_binaural_dsp_v4.1.4.11_width_profile_lab.eel`

Source intake:

- `labs-experimental03-review-2026-07-06.md`
- `labs-width-profile-listening-summary-2026-07-06.md`

Status: Fixture ready for controlled listening.

## Decision

The next `experimental03` ingredient to isolate is the bass saturation behavior,
not modulation, smoothing, or STFT release.

## Why This Step

The width-profile step is now Labs-supported. The next most plausible contributor
to the `experimental03` target sound is its altered bass harmonic generation.

This should be tested before crest-adaptive STFT or LFO/modulation behavior
because:

- bass weight and smoothness are central to Axiom's perceived character;
- the saturation change can be isolated inside one existing stage;
- it can preserve host limiter ownership and the accepted reserve law;
- modulation carries higher risk for fatigue, image movement, and ambiguous
  listening results.

## What `experimental03` Changed

The accepted `.11` bass stage saturates the current extracted sub sample:

```text
sat = (sub * drive) / (1.0 + abs(sub * drive))
```

`experimental03` computes a midpoint between the previous and current extracted
sub sample, saturates both the midpoint and current sample, then averages those
two saturated values.

This is useful as an idea, but it should not be described as rigorous
oversampling unless a true upsample/filter/downsample structure exists.

## Allowed Changes

- Start from the supported width-profile Labs fixture.
- Add only the interpolated bass-saturation state and arithmetic needed for the
  generated harmonic branch.
- Preserve the accepted bass extraction and harmonic high-pass filters.
- Preserve `slider1` behavior and the accepted output reserve law.
- Preserve the final `@sample` writeback lines.
- Preserve host-owned crossfeed and terminal limiter policy.

## Forbidden Changes

- No theta, alpha, euphoria, brainwave, dopamine, entrainment, or medical-style
  modulation.
- No LFOs.
- No parameter smoothing.
- No STFT changes.
- No exciter changes.
- No output reserve changes.
- No internal limiter.
- No accepted or historical EEL edits in place.
- No claim that this is true oversampling.

## Fixture

Created fixture:

```text
src/labs/axiom_binaural_dsp_v4.1.4.11_width_bass_saturation_lab.eel
```

The fixture differs from the width-profile Labs fixture only in:

- `desc` label;
- added previous-sample/midpoint bass-stage state variables;
- generated-sub saturation arithmetic.

It preserves the accepted extraction filters, harmonic high-pass filters,
reserve law, host limiter ownership, and final `@sample` writeback lines.

Static validation passed on 2026-07-06.

Listening instructions are in
`labs-bass-saturation-listening-target-2026-07-06.md`.

## Listening Question

Does the interpolated saturation step add useful bass smoothness, weight, or
cohesion while preserving:

- clean kick impact;
- bass-image anchoring;
- energy/aliveness;
- low fatigue;
- no pumping or level retreat;
- no added fuzz, smear, or dullness?

## Decision Outcomes

- `keep`: bass saturation improves the supported width fixture without obvious
  cost.
- `reject`: bass saturation weakens punch, clarity, energy, or bass anchoring.
- `material dependent`: bass saturation helps some bass-forward material but
  hurts other classes.
- `no reliable difference`: do not carry the idea forward.

## Candidate Boundary

Even if this bass step is preferred, it remains Labs-only. Candidate discussion
requires a separate `Axiom Clean R012` plan, candidate-readiness review, scoped
qualification, and explicit user approval.
