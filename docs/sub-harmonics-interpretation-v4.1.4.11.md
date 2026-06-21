# v4.1.4.11 Sub Harmonics Follow-Up Interpretation

Date: 2026-06-21

## Status

No `.12` DSP listening candidate is justified from the completed `.11` follow-up
alone. `src/axiom_binaural_dsp_v4.1.4.11.eel` remains the accepted baseline.

The `.11` Sub Harmonics investigation is closed as a watch item. Focused
blinded listening did not justify an EEL change.

## Question

The completed follow-up asked whether accepted `.11` has a repeatable
normal-material failure at elevated `Sub Harmonics Gain`, or whether the
remaining signal is a user-control tradeoff that should only become candidate
work if it is audible.

The focused map tested:

- accepted default `+4 dB`;
- elevated `+10 dB`;
- elevated `+12 dB`;
- dense electronic, hip-hop/trap-sub, bass-oriented, and flawed-source stress
  material;
- JDSP terminal limiter at the accepted `-1.00 dB` threshold.

Temporary external fixtures changed only the `Sub Harmonics Gain (dB)` default.
The accepted `.11` EEL file was not edited.

## Measured Result

The harness gate recorded `FAIL`, but the failure does not prove an unsafe
accepted default.

Important findings:

- normal material stayed unclipped through the tested `+12 dB` setting;
- flawed-source clipping appeared only on the declared flawed-source stress
  item and is not a normal-material rejection;
- the default `+4 dB` dense electronic item did not qualify repeated level
  metrics within spread policy, so the evidence is not clean enough to close
  the topic as fully settled;
- `+10 dB` and `+12 dB` showed repeatable RMS retreat on hip-hop/trap-sub and
  bass-light material;
- terminal-pressure observation findings occurred at tested slider settings.

See `sub-harmonics-follow-up-v4.1.4.11.md` for the summarized measurement
table and range findings.

## Decision

Do not create `.12` yet.

The evidence narrows the concern to elevated-control feel rather than
normal-material clipping. A candidate would be premature unless listening
confirms that the measured RMS retreat is audible as a musical defect.

A 2026-06-09 confirmatory rerun did not change this decision. It again found
no normal-material clipping through `+12 dB`, repeated the default `+4 dB`
dense-electronic measurement qualification failure, and repeated the elevated
`+10 dB`/`+12 dB` RMS-retreat concern on hip-hop/trap-sub and bass-light
material.

Keep these boundaries:

- no accepted or historical EEL edits;
- no `.12` file without a falsifiable hypothesis;
- no reserve-law candidate from metrics alone;
- no baseline-status change;
- no claim that elevated `Sub Harmonics Gain` is broken globally.

## 2026-06-21 Blinded Listening Result

The prepared gain-adjusted A/B packages compared the accepted `+4 dB` control
point against `+10 dB` and `+12 dB` across four normal-material classes.

| Comparison | Bass-light piano | Dense electronic | Hip-hop | Upright bass | Summary |
| --- | --- | --- | --- | --- | --- |
| `+4` vs `+10` | `+4` | `+10` | `+10` | `+4` | split 2-2 |
| `+4` vs `+12` | `+4` | `+4` | `+4` | `+4` | `+4` preferred 4-0 |

Combined, the accepted `+4 dB` setting was preferred in six of eight blinded
comparisons. Earlier observations found that `+10/+12 dB` could add bass
weight while preserving clarity and clean kick impact, but could also reduce
aliveness, increase short-session fatigue, and introduce slight pumping.

Interpretation:

- `+10 dB` is material-dependent rather than consistently defective;
- `+12 dB` is consistently less preferred than the accepted default in this
  package;
- the result supports user-control guidance and a watch item, not a new reserve
  law or `Axiom Clean R012` candidate;
- the accepted `+4 dB` default and accepted `.11` baseline remain unchanged.

The full structured record remains local because it contains route context.
Its validator status is `pass`.

## Listening Target (Completed)

Use accepted `.11` only. This is not candidate acceptance listening.

Compare the accepted `+4 dB` control point against `+10 dB` and `+12 dB` on
material that exposes low-end density and punch.

Primary listening question:

```text
At elevated Sub Harmonics Gain, does accepted .11 audibly trade too much punch,
practical loudness, or bass clarity for headroom on normal material?
```

Listen for:

- kick softening;
- bass blur or bass detached from the main image;
- low-end crowding;
- perceived level retreat after matching normal listening level as fairly as
  practical;
- limiter pumping or breathing;
- short-session fatigue;
- center-image or bass-image instability.

Use structured listening fields from `listening-records.md`, especially:

- `bass`;
- `punch`;
- `center_image`;
- `lateral_spread`;
- `localization_blur`;
- `depth_impression`;
- `bass_image_coupling`;
- `loudness`;
- `fatigue`;
- `route_context`;
- `artifacts`;
- `overall`.

Material priorities:

- dense electronic or modern pop;
- hip-hop/trap-sub;
- acoustic or upright bass where bass-image attachment is obvious;
- bass-light material to check whether elevated settings unnecessarily pull
  broadband level down;
- flawed-source material only as a robustness/stress note, not as a rejection
  basis.

## Candidate Trigger

Only draft a `.12` hypothesis if listening finds a repeatable normal-material
defect at elevated settings.

A valid future hypothesis would look like:

```text
At +10 dB or +12 dB Sub Harmonics Gain, accepted .11 may over-retreat
broadband RMS/P95 energy on specific material, causing audible kick softening
or bass-image blur without providing a useful listener benefit.
```

That hypothesis would still need:

- a scoped edit boundary, likely limited to elevated-bass reserve behavior;
- a measurable target, such as reducing elevated-setting RMS retreat without
  crossing terminal-margin policy;
- real-JDSP qualification;
- structured listening comparison;
- explicit user acceptance before any promotion.

## Close Condition

Close the `.11` investigation without `.12` if listening does not reveal a
repeatable audible defect at elevated settings.

If listening is inconclusive, keep `.11` accepted and keep the topic as a
watch item rather than creating a candidate.

Outcome: closed as `watch_item`; no candidate hypothesis needed.
