# Axiom Listening Protocol

Listening remains the final acceptance gate for sound-changing Axiom
candidates. Measurement decides whether a candidate is safe and meaningful
enough to hear; the user decides whether it should be accepted.

This protocol complements `listening-records.md`, which defines the structured
record format and validator.

## When To Listen

Do not begin official candidate listening until:

- candidate readiness has passed or any limitation is documented;
- the candidate has a falsifiable hypothesis;
- the edit boundary is narrow;
- static EEL validation passes;
- relevant offline or fixture evidence exists;
- real-JDSP qualification has passed or returned an explicit investigation
  status that is safe for listening;
- the comparison version and listening target are defined.

Rough exploratory listening is allowed, but it is not acceptance evidence.

## Listening Setup

Before listening, record:

- Axiom version and comparison version;
- device and route;
- RootlessJamesDSP or JDSP4Linux path;
- JDSP limiter threshold, release, and postgain;
- host crossfeed state;
- all Axiom slider values;
- whether the test is speaker, wired/USB, Bluetooth, headphone, or WSL lab.

Qualification comparisons use crossfeed disabled. Headphone crossfeed may be
tested separately as a compatibility or preference check, but it should not be
mixed into the core comparison unless explicitly documented.

## Material Selection

Use material with a job. A candidate does not need every category every time,
but the selected material should match the hypothesis.

| Category | What It Exposes |
| --- | --- |
| Dense electronic or modern pop | limiter pressure, bass density, polish, fatigue. |
| Hip-hop or trap sub bass | sub-harmonic control, kick/bass separation, headroom. |
| Rock or metal | guitars, cymbal edge, congestion, punch. |
| Piano or acoustic material | tone, center image, transient realism. |
| Orchestral or cinematic crescendos | width, density, high-band smoothness. |
| Sibilant vocal or speech | harshness, center stability, intelligibility. |
| Low-level air-bearing material | exciter usefulness and restraint. |
| Flawed or clipped source | robustness and failure behavior, not normal-material rejection. |
| Bass-light material | whether bass processing stays out of the way. |
| Already-wide or mono/narrow material | stereo compatibility and image control. |

Private or streamed material stays in local records. Public docs should
summarize non-private conclusions only.

## Comparison Method

Use a clear comparison target:

- accepted baseline versus candidate;
- accepted baseline versus temporary fixture;
- Core versus profile experiment;
- host setting A/B when testing crossfeed or limiter behavior.

Keep levels as controlled as practical. If a candidate is intentionally louder
or quieter, document that as part of the hypothesis rather than treating it as
an accidental preference boost.

For formal acceptance:

- avoid changing multiple host settings mid-test;
- avoid changing unrelated Axiom sliders mid-test;
- listen for the stated target first, then check for regressions;
- use more than one material class when the change affects a shared stage.

## Observation Fields

At minimum, record observations for:

- bass;
- punch;
- center image;
- lateral spread;
- localization blur;
- depth impression;
- bass-image coupling;
- width;
- air;
- harshness;
- loudness;
- fatigue;
- route context;
- artifacts;
- overall judgment.

Useful extra notes include:

- "better but only because louder";
- "cleaner but less exciting";
- "wider but center weakened";
- "wider but source positions blur";
- "more enveloping but depth collapses";
- "bass stronger but kick softened";
- "bass weight detached from the center image";
- "less harsh but dull";
- "good on headphones, questionable on speakers".

## Decision Rules

Use these decisions:

- `accept`: candidate is preferred and no blocking regression was found.
- `reject`: candidate is worse or has a blocking artifact.
- `needs_retest`: evidence is promising but setup, route, fatigue, or material
  coverage was not reliable enough.
- `no_decision`: exploratory or incomplete listening.

Acceptance requires a written rationale. Rejection requires a written rationale
when possible so future work does not repeat the same mistake.

## Public Summary Boundary

A public qualification summary may include:

- candidate and comparison version;
- route class;
- host settings;
- material classes;
- non-private listening conclusion;
- acceptance or rejection rationale.

Do not publish:

- private song libraries;
- private timestamps;
- local filesystem paths;
- captures or source audio;
- unsupported claims about universal preference or certified measurement.

## Validation

After writing a structured local record, validate it:

```bash
scripts/validate_axiom_listening_record.py \
  ~/.local/state/axiom-engineering/listening-records/example.json \
  --json /tmp/axiom-listening-validation.json \
  --markdown /tmp/axiom-listening-validation.md
```

The validator checks record structure. It does not decide whether the listening
conclusion is correct.
