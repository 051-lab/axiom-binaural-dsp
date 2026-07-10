# Labs Listening Summary: Bass-Saturation Fixture

Date: 2026-07-06

Related task: `AX-TASK-044`

Fixture B:

```text
src/labs/axiom_binaural_dsp_v4.1.4.11_width_bass_saturation_lab.eel
```

Comparison A:

```text
src/labs/axiom_binaural_dsp_v4.1.4.11_width_profile_lab.eel
```

## Result

Preliminary user decision: `B preferred`.

Decision label: `keep` as a Labs-supported ingredient.

## Interpretation

The interpolated bass-saturation step should remain in the Labs path as a
supported second ingredient toward the `experimental03` target sound.

This does not create `Axiom Clean R012`, does not promote a candidate, and does
not change the accepted `Axiom Clean R011` baseline.

## Evidence Boundary

This summary records the user's preference for B. It is not yet a full
structured listening record because material-specific notes, route details,
crossfeed state, and per-excerpt observations have not been captured in the
JSON record template.

Before candidate discussion, record or reconstruct:

- output route and device;
- crossfeed state;
- material classes tested;
- whether B remained preferred across centered, dense, and bass-forward
  material;
- notes on kick punch, bass anchoring, low-mid clarity, energy/aliveness,
  fatigue, pumping, level retreat, fuzz, smear, dullness, and image movement.

## Next Step

Do not add another DSP ingredient yet. The next engineering step is a combined
ingredient review:

```text
accepted .11
  versus
width-profile Labs fixture
  versus
width-plus-bass-saturation Labs fixture
```

That review should decide whether the supported Labs ingredients justify a
separate `Axiom Clean R012` candidate-readiness plan.
