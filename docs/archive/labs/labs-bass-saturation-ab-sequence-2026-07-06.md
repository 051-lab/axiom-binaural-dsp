# A/B Sequence: Bass-Saturation Labs Fixture

Date: 2026-07-06

Related task: `AX-TASK-044`

## Files

A:

```text
src/labs/axiom_binaural_dsp_v4.1.4.11_width_profile_lab.eel
```

B:

```text
src/labs/axiom_binaural_dsp_v4.1.4.11_width_bass_saturation_lab.eel
```

Use A as the control and B as the test. Do not compare B directly against
accepted `.11` until this pass is complete.

## Fixed Conditions

Keep unchanged for the whole pass:

- output device;
- Windows source endpoint and processed output endpoint;
- player volume and Windows volume;
- JamesDSP postgain and terminal limiter;
- crossfeed state;
- source track and excerpt timestamp.

If any of these change, mark the pass `needs retest`.

## Material Order

Use four short excerpts, about 45 to 90 seconds each:

1. Bass-light piano, vocal, or acoustic material.
2. Electronic or modern pop material.
3. Hip-hop, trap-sub, or kick-forward material.
4. Sustained bass, bass guitar, or upright bass material.

## Switch Pattern

For each excerpt:

1. Play A for 45 to 90 seconds.
2. Load B and replay the same excerpt.
3. Load A again for a short reset check.
4. Load B again only if the first impression was unclear.
5. Write one line: `A preferred`, `B preferred`, `no reliable difference`, or
   `needs retest`.

Avoid long looping on one excerpt. If the difference is not clear after two
passes, record `no reliable difference` or `needs retest`.

## Primary Judgement

Keep B only if it improves bass smoothness, weight, or cohesion while preserving:

- kick punch;
- bass anchoring;
- low-mid clarity;
- energy and aliveness;
- low fatigue.

Reject B if it adds:

- dullness;
- fuzz;
- smear;
- pumping;
- level retreat;
- image movement;
- quicker fatigue.

## Final Classification

Use one of:

- `keep`;
- `reject`;
- `material dependent`;
- `no reliable difference`;
- `needs retest`.

Record the result with
`templates/bass-saturation-listening-record-2026-07-06.json`, then interpret it
with `labs-bass-saturation-post-listening-decision-map-2026-07-06.md`.
