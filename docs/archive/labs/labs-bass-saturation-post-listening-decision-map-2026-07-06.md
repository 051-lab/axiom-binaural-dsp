# Labs Decision Map: Bass-Saturation Listening Result

Date: 2026-07-06

Related task: `AX-TASK-044`

Fixture:

```text
src/labs/axiom_binaural_dsp_v4.1.4.11_width_bass_saturation_lab.eel
```

Comparison:

```text
src/labs/axiom_binaural_dsp_v4.1.4.11_width_profile_lab.eel
```

This map defines what to do after the controlled listening pass. It does not
promote the Labs fixture, create `Axiom Clean R012`, or change the accepted
baseline.

## Required Input

Before making a decision, capture:

- route and output device;
- crossfeed state;
- at least three material classes, with bass-forward material included;
- whether the width fixture, bass-saturation fixture, or neither was preferred
  per material;
- bass smoothness, kick punch, bass-image anchoring, perceived energy, and
  fatigue notes;
- any pumping, level retreat, fuzz, smear, dullness, or image movement.

Use `templates/bass-saturation-listening-record-2026-07-06.json` as the local
record starting point.

## Decision Outcomes

### `keep`

Action:

- keep the bass-saturation result in Labs;
- summarize the listening result in a dedicated Labs summary;
- do not promote directly;
- prepare a combined-ingredient review before any `Axiom Clean R012` discussion.

Required follow-up before candidate discussion:

- static validation remains passing;
- local listening record validates;
- no reported fatigue, pumping, image movement, or bass smear;
- preference holds across at least centered, dense, and bass-forward material;
- the combined width plus bass-saturation change is reviewed against accepted
  `.11`, not only against the width fixture.

Interpretation:

The interpolated saturation idea has support as a second controlled ingredient
toward the `experimental03` target, but it is still Labs-only.

### `reject`

Action:

- stop this bass-saturation path;
- keep the width fixture as the only supported `experimental03` ingredient so
  far;
- do not create an `R012` candidate from this bass change;
- summarize why the bass idea lost.

Interpretation:

The bass-saturation change either weakens punch, clarity, anchoring, energy, or
comfort enough that it should not be carried forward.

### `material dependent`

Action:

- keep in Labs;
- identify which material classes prefer the bass fixture and which reject it;
- do not create a candidate until the pattern is specific and repeatable;
- consider whether the result suggests a control/profile idea rather than a
  new fixed Core default.

Possible follow-up:

- test a lighter midpoint blend;
- test the bass idea only at elevated Sub Harmonics settings;
- stop if the pattern looks route-specific or inconsistent.

Interpretation:

The bass idea may be useful, but it is not fixed-default candidate material
without more constraint.

### `no reliable difference`

Action:

- document no action;
- do not spend candidate effort on this exact saturation change;
- keep the width fixture as the only supported `experimental03` ingredient so
  far;
- move to another extracted hypothesis only if still useful.

Interpretation:

The isolated bass-saturation change is not a strong explanation for the
`experimental03` preference.

### `needs retest`

Action:

- keep `AX-TASK-044` in listening-prep;
- document what made the pass inconclusive;
- repeat only after route, level, source, or fatigue conditions are corrected.

Interpretation:

No technical or listening conclusion should be drawn from the pass.

## Candidate Boundary

An official candidate requires a separate step:

- candidate-readiness status reviewed;
- combined hypothesis written;
- candidate filename uses the `Axiom Clean R012+` naming policy;
- real-JDSP qualification scope selected;
- listening target prepared;
- explicit user approval before promotion work.

The Labs fixture itself must not be renamed into the accepted line.
