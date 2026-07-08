# Labs Listening Target: Bass-Saturation Isolation

Date: 2026-07-06

Fixture:

```text
src/labs/axiom_binaural_dsp_v4.1.4.11_width_bass_saturation_lab.eel
```

Windows/WSL load path:

```text
\\wsl.localhost\Ubuntu\home\soloarch\dsp-dev\axiom-binaural-dsp\src\labs\axiom_binaural_dsp_v4.1.4.11_width_bass_saturation_lab.eel
```

Comparison target:

```text
src/labs/axiom_binaural_dsp_v4.1.4.11_width_profile_lab.eel
```

## Question

Does the interpolated bass-saturation step improve the already preferred width
fixture, or does it add cost without a clear musical gain?

## Listen For

- bass smoothness and weight;
- kick cleanliness and punch;
- bass-image anchoring;
- low-mid clarity;
- overall energy and aliveness;
- listening fatigue over several tracks;
- pumping, level retreat, fuzz, smear, or dullness.

## Decision Labels

- `keep`: the bass step improves the width fixture without obvious cost.
- `reject`: it weakens punch, clarity, energy, or bass anchoring.
- `material dependent`: it helps some bass-forward material but hurts others.
- `no reliable difference`: do not carry the idea forward.

Use `templates/bass-saturation-listening-record-2026-07-06.json` as the local
copy starting point for structured notes.

Use `labs-bass-saturation-ab-sequence-2026-07-06.md` for the exact listening
order.

## Boundary

This is Labs-only. A preferred result does not create `Axiom Clean R012`; it
only identifies a second controlled ingredient toward a later candidate
discussion.
