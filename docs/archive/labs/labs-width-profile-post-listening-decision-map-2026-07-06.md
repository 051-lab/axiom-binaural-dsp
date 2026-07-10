# Labs Decision Map: Width-Profile Listening Result

Date: 2026-07-06

Related task: `AX-TASK-043`

Fixture:

```text
src/labs/axiom_binaural_dsp_v4.1.4.11_width_profile_lab.eel
```

Comparison:

```text
accepted v4.1.4.11 / Axiom Clean R011
```

This map defines what to do after the controlled listening pass. It does not
promote the Labs fixture, create `Axiom Clean R012`, or change the accepted
baseline.

## Required Input

Before making a decision, capture:

- route and output device;
- crossfeed state;
- at least three material classes;
- whether `.11`, the width fixture, or neither was preferred per material;
- fatigue, image stability, bass anchoring, and perceived energy notes;
- any artifacts, dullness, shimmer, or image movement.

Use `templates/width-profile-listening-record-2026-07-06.json` as the local
record starting point.

## Decision Outcomes

### `.11 preferred`

Action:

- stop this width-profile path;
- keep `Axiom Clean R011` accepted;
- do not create an `R012` candidate;
- summarize why the narrower global width lost.

Interpretation:

The `experimental03` preference was probably not explained by the isolated
global-width change, or the isolated change lost too much energy/space.

### `width lab preferred`

Action:

- keep the result in Labs;
- create a follow-up measurement/listening plan;
- do not promote directly;
- consider a candidate-readiness check before proposing `Axiom Clean R012`.

Required follow-up before candidate discussion:

- static validation remains passing;
- local record validates;
- no reported fatigue or image instability;
- preference holds across at least centered, dense, and bass-forward material;
- host/crossfeed state is documented.

Interpretation:

The width-profile hypothesis has support, but still needs broader evidence
before it can become a candidate.

2026-07-06 preliminary outcome:

- User confirmed that the width Labs fixture moves accepted `.11` toward the
  desired `experimental03` direction.
- The result is recorded in
  `labs-width-profile-listening-summary-2026-07-06.md`.
- Continue Labs by isolating the next `experimental03` ingredient rather than
  promoting the fixture.

### `material dependent`

Action:

- keep in Labs;
- identify which material classes prefer `.11` versus the width fixture;
- consider a second width fixture only if the pattern is specific and useful.

Possible follow-up:

- test a middle global width value between `100` and `135`;
- test low-mid-only width reduction instead of global-width reduction;
- stop if the pattern looks route-specific or inconsistent.

Interpretation:

The one-variable change is informative but not candidate-ready.

### `no reliable difference`

Action:

- document no action;
- keep `.11` accepted;
- do not spend candidate effort on this exact width value;
- move to the next extracted `experimental03` hypothesis only if still useful.

Interpretation:

The isolated global-width change is not a strong explanation for the
`experimental03` preference.

### `stop this path`

Action:

- close `AX-TASK-043` as a stopped Labs path;
- preserve the review and fixture as evidence;
- do not create more width fixtures unless new evidence appears.

Interpretation:

The width idea is either harmful, too small, too host-specific, or not worth
continued Axiom Core effort.

## Candidate Boundary

An official candidate requires a separate step:

- candidate-readiness status reviewed;
- candidate hypothesis written;
- candidate filename uses the `Axiom Clean R012+` naming policy;
- real-JDSP qualification scope selected;
- listening target prepared;
- explicit user approval before promotion work.

The Labs fixture itself must not be renamed into the accepted line.
