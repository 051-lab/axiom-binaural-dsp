# Labs Review: Experimental03 EEL Intake

Date: 2026-07-06

Related task: `AX-TASK-043`

Baseline: `Axiom Clean R011` / `src/axiom_binaural_dsp_v4.1.4.11.eel`

Reviewed artifact: `axiom-liveprog-experimental03.eel`

Status: Labs intake only. This is not an accepted baseline, active listening
candidate, or `Axiom Clean R012` candidate.

## Observation

The `experimental03` script has been useful for informal listening and may
sound preferable to the accepted `.11` baseline in the current host setup. It
also contains several multi-variable changes from `.11`, so any perceived
improvement cannot be attributed to one stage without further isolation.

## Initial Static Result

The accepted `.11` baseline passed the static EEL validator. The
`experimental03` script did not pass the same static gate.

Observed validator failures:

- missing required sequential memory-allocation topology pattern;
- missing reference limiter attack coefficient;
- missing reference limiter gain smoothing coefficient.

The limiter failures do not mean a script limiter should be added. The current
Axiom policy remains unchanged: JDSP terminal limiter owns peak control, and
Core EEL files must not add an internal limiter.

## Important Differences From `.11`

`experimental03` is not an apples-to-apples comparison against `.11`.

- It forces different effective startup defaults in `@init`.
- It narrows the low-mid and high-width behavior compared with the accepted
  default `.11` profile.
- It adds parameter smoothing, but the coefficient is applied in the wrong
  direction for a 20 ms one-pole glide.
- It adds low-frequency and high-frequency modulation behavior that can affect
  stereo image stability, fatigue, and perceived motion.
- It adds an interpolated bass-saturation branch that may be worth isolating,
  but the current wording overstates it as rigorous oversampling.
- It adds crest-aware STFT release behavior that may be worth testing as a
  separate hypothesis.
- It uses neuro/entrainment/reward-oriented language that is not appropriate
  for Axiom Core claims.

## Professional Assessment

`experimental03` is a useful Labs source, not a replacement for `.11`.

The likely reason it may sound better is not proven to be a new architecture.
The most plausible contributors are its narrower effective width defaults,
changed bass-harmonic behavior, and added modulation. Those changes may improve
some material while also increasing the risk of image movement, shimmer,
fatigue, or harder-to-interpret qualification results.

## Extractable Hypotheses

Only one hypothesis should be tested at a time.

1. Width profile:
   A narrower default width law may sound more coherent than the accepted `.11`
   default on the current host/headphone route.

2. Bass saturation:
   The interpolated bass harmonic branch may improve weight or smoothness
   without the elevated-setting fatigue observed in the `.11` Sub Harmonics
   follow-up.

3. Crest-adaptive STFT release:
   Crest-sensitive release behavior may reduce resonance-control artifacts
   without dulling transient material.

## Forbidden Scope

- Do not edit `src/axiom_binaural_dsp_v4.1.4.11.eel` in place.
- Do not create `Axiom Clean R012` from the whole `experimental03` script.
- Do not retain neuro, entrainment, dopamine, reward, or medical-style claims
  in any Core-facing Axiom script or release note.
- Do not compare multi-variable Labs scripts as if they prove a single DSP
  improvement.
- Do not commit private runtime folders, listening captures, or local manifests.

## Recommended Next Step

Create a controlled Labs experiment for the width-profile hypothesis first.
That is the lowest-risk and most immediately testable explanation for the
reported preference. If it survives static validation and focused listening,
then the bass-saturation and crest-adaptive STFT ideas can be evaluated as
separate follow-up Labs experiments.

The initial plan is recorded in `labs-width-profile-plan-2026-07-06.md`.
The first fixture is
`src/labs/axiom_binaural_dsp_v4.1.4.11_width_profile_lab.eel`.

No Core candidate should be created until the selected hypothesis has:

- a sanitized Labs note;
- a one-variable fixture or candidate branch;
- static EEL validation;
- a defined listening target;
- explicit user approval for promotion beyond Labs.

## Decision

Continue Labs. Do not promote `experimental03` directly.
