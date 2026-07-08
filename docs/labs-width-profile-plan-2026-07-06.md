# Labs Plan: Width-Profile Isolation

Date: 2026-07-06

Related task: `AX-TASK-043`

Baseline: `Axiom Clean R011` / `src/axiom_binaural_dsp_v4.1.4.11.eel`

Source intake: `labs-experimental03-review-2026-07-06.md`

Status: Fixture created. The fixture is Labs-only and is not an official
candidate.

## Observation

The current informal preference for `experimental03` may be caused by its
narrower effective width behavior rather than by the rest of its experimental
changes. Width is the safest first variable to isolate because it can be tested
without changing the bass harmonic generator, STFT logic, output reserve law,
or host-limiter policy.

## Hypothesis

A narrower default low-mid/high-band width profile can improve perceived center
stability and reduce fatigue while preserving the clarity and engagement of
the accepted `.11` baseline.

## Allowed Changes

- Create a Labs-only copy from the accepted `.11` baseline.
- Change only the width-profile defaults or width-law constants needed for the
  test.
- Preserve the accepted signal-chain order.
- Preserve the accepted output reserve behavior.
- Preserve the final `@sample` writeback lines.
- Preserve host-owned crossfeed and terminal limiter policy.

## Forbidden Changes

- No changes to bass harmonic generation.
- No changes to STFT suppression.
- No modulation/LFO additions.
- No parameter-smoothing changes.
- No internal limiter.
- No neuro, entrainment, reward, dopamine, medical, or wellness claims.
- No promotion to `Axiom Clean R012` until the Labs result justifies candidate
  work and the user approves promotion.

## Fixture

Created fixture:

```text
src/labs/axiom_binaural_dsp_v4.1.4.11_width_profile_lab.eel
```

It starts as a direct copy of `.11` and changes only the global side-width
default from `135` to `100`.

Effective default width products:

```text
Low-mid side product: 1.701 -> 1.260
High side product:    1.485 -> 1.100
```

## Test Focus

Listen for:

- center vocal/kick/snare stability;
- low-mid spread versus blur;
- high-frequency openness versus shimmer;
- bass image staying anchored;
- fatigue over repeated listening;
- mono compatibility concerns;
- whether the change still feels engaging compared with `.11`.

## Minimum Validation Before Listening

```bash
scripts/validate_axiom_static.sh src/axiom_binaural_dsp_v4.1.4.11.eel
scripts/validate_axiom_static.sh src/labs/axiom_binaural_dsp_v4.1.4.11_width_profile_lab.eel
```

Both checks passed on 2026-07-06.

If an offline render/metric harness is available for the selected route, run a
short width-focused screen before real listening. Do not treat offline metrics
as acceptance.

## Listening Method

Compare accepted `.11` against the width-only Labs fixture with the same host
route and the same JDSP terminal limiter settings. Keep optional crossfeed
state fixed for the entire comparison.

Suggested material classes:

- centered vocal or piano;
- dense electronic;
- hip-hop or kick-forward material;
- upright/electric bass material;
- bright cymbal or acoustic material.

Use `labs-width-profile-listening-target-2026-07-06.md` for the focused
listening questions.

## Decision Gate

Possible outcomes:

- stop: narrower width weakens image, clarity, or engagement;
- continue Labs: result is promising but needs a better fixture or broader
  listening;
- create candidate: width-only change clearly improves the target behavior and
  does not introduce fatigue, image drift, or validation issues;
- document no action: preference appears host-specific or not repeatable.

Creating an official candidate requires explicit approval and a new
`Axiom Clean R012` candidate plan.

## Safety Check

- Accepted EEL scripts must not be edited in place.
- Captures, source music, manifests, and private paths must stay out of git.
- Claims must stay limited to the evidence gathered for this width-only test.
