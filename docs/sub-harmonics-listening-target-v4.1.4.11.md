# v4.1.4.11 Sub Harmonics Listening Target

Date: 2026-06-21

## Purpose

This is a focused listening target for accepted `v4.1.4.11`. It does not create
`.12`, approve a candidate, or change the accepted baseline.

Use it to decide whether the completed `.11` Sub Harmonics follow-up should be
closed as a watch item or turned into a narrow future `.12` hypothesis.

Status: completed. The 2026-06-21 outcome was `watch_item`; no candidate was
created.

## Source Evidence

- Measurement summary: `sub-harmonics-follow-up-v4.1.4.11.md`
- Interpretation record: `sub-harmonics-interpretation-v4.1.4.11.md`
- Listening record template:
  `templates/sub-harmonics-listening-record-v4.1.4.11.json`

The measurement found no normal-material clipping through `+12 dB`, but it did
find elevated-setting RMS retreat plus terminal-pressure observations. The
listening task is to decide whether that tradeoff is audibly harmful.

## Setup

Use accepted `.11` only:

```text
src/axiom_binaural_dsp_v4.1.4.11.eel
JDSP limiter threshold: -1.00 dB
JDSP limiter release: 60 ms
JDSP postgain: 0.00 dB
Crossfeed during qualification: disabled
```

Compare these Sub Harmonics settings:

```text
+4 dB  accepted default control point
+10 dB elevated stress point
+12 dB elevated stress point
```

Keep all other Axiom sliders at accepted defaults unless the listening record
explicitly says otherwise.

## Listening Question

```text
At elevated Sub Harmonics Gain, does accepted .11 audibly trade too much punch,
practical loudness, or bass clarity for headroom on normal material?
```

## Material Priorities

Use local material that exposes the measured risk:

- dense electronic or modern pop for limiter pressure, low-end density, and
  fatigue;
- hip-hop or trap-sub for kick/sub separation and practical loudness;
- acoustic/upright bass or bass-centered material for bass-image attachment;
- bass-light material to check whether elevated settings unnecessarily pull
  broadband level down;
- flawed-source material only as a robustness note, not as a rejection basis.

Keep private titles, timestamps, and full records outside public git unless
they are sanitized.

## What To Listen For

Record observations for:

- kick softening;
- bass blur;
- low-end crowding;
- bass weight detaching from the center or main image;
- practical loudness retreat after fair listening-level handling;
- limiter pumping or breathing;
- short-session fatigue;
- center-image instability;
- lateral spread or localization blur changes;
- whether elevated settings feel better only because of added bass weight, or
  worse because punch and clarity retreat.

## Decision Outcomes

Use one of these outcomes in the local listening record:

- `close_without_candidate`: no repeatable normal-material defect was heard;
- `watch_item`: observations are mixed, route-specific, or fatigue-limited;
- `candidate_hypothesis_needed`: repeatable defect heard at `+10/+12 dB` and
  a narrow `.12` hypothesis should be drafted;
- `needs_retest`: setup, route, level handling, or material coverage was not
  reliable enough.

Do not create `.12` unless listening supports
`candidate_hypothesis_needed`.

## Local Record Workflow

Copy the template to local state and edit the copy:

```bash
mkdir -p ~/.local/state/axiom-engineering/listening-records
cp docs/templates/sub-harmonics-listening-record-v4.1.4.11.json \
  ~/.local/state/axiom-engineering/listening-records/sub-harmonics-v4.1.4.11-local.json
```

After filling it in, validate the local record:

```bash
scripts/validate_axiom_listening_record.py \
  ~/.local/state/axiom-engineering/listening-records/sub-harmonics-v4.1.4.11-local.json \
  --json /tmp/axiom-sub-harmonics-listening-validation.json \
  --markdown /tmp/axiom-sub-harmonics-listening-record.md
```

Public docs should summarize only sanitized material classes, route class,
decision, and non-private rationale.

## Optional A/B Package Workflow

If a completed Sub Harmonics map already exists, build local A/B packages from
the processed render folders instead of switching sliders manually during
listening. Keep the generated package outside git because it contains processed
audio.

Example shape:

```bash
scripts/build_axiom_ab_listening_package.py \
  /path/to/sub-slider-map/slider_4db \
  /path/to/sub-slider-map/slider_10db \
  ~/.local/state/axiom-engineering/listening-packages/sub-harmonics-v4.1.4.11/+4-vs-+10 \
  --label sub-harmonics-v4.1.4.11-plus4-vs-plus10 \
  --include-regex 'render_1\.wav$' \
  --exclude-regex 'flawed'

scripts/build_axiom_ab_listening_package.py \
  /path/to/sub-slider-map/slider_4db \
  /path/to/sub-slider-map/slider_12db \
  ~/.local/state/axiom-engineering/listening-packages/sub-harmonics-v4.1.4.11/+4-vs-+12 \
  --label sub-harmonics-v4.1.4.11-plus4-vs-plus12 \
  --include-regex 'render_1\.wav$' \
  --exclude-regex 'flawed'
```

Use the package markdown for the blinded A/B slot assignments and recommended
gain values. Excluding `flawed` keeps intentional stress material out of the
normal-material listening decision.
