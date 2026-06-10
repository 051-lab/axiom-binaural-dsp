# Axiom Sub Harmonics Follow-Up v4.1.4.11

Date: 2026-06-08

## Scope

This record summarizes the targeted post-acceptance `.11` real-JDSP follow-up
for the open investigation:

```text
Run: 20260603T004349-post-acceptance-v4-1-4-1-0d309b
Accepted baseline: src/axiom_binaural_dsp_v4.1.4.11.eel
JDSP limiter threshold: -1.00 dB
JDSP limiter release: 60 ms
JDSP postgain: 0.00 dB
Crossfeed: disabled
Slider points: +4, +10, +12 dB
Repetitions per point: 3
Material filter: electronic|hip hop|bass|flawed
```

Temporary external fixtures changed only the `Sub Harmonics Gain (dB)` default.
The accepted `.11` EEL file was not edited.

Full WAV captures and JSON/Markdown reports remain local artifacts and are not
committed to the repository.

## Result

Harness gate: `FAIL`

Interpretation: this is an investigation result, not `.12` approval.

The corrected follow-up completed after the JDSP capture route was restored.
It produced a full aggregate report for `+4`, `+10`, and `+12 dB`. No
normal-material clipped samples were observed through `+12 dB`, and the highest
tested unclipped slider value was `+12 dB`.

The failure came from evidence quality and investigation findings:

- the default `+4 dB` dense electronic item did not produce a repeated level
  metric that qualified within the spread policy;
- all tested slider settings reached the terminal-pressure observation zone on
  at least one selected item;
- elevated `+10 dB` and `+12 dB` settings showed repeatable RMS retreat on
  hip-hop/trap-sub and bass-light material;
- flawed-source clipping remains an investigation stress behavior, not a
  normal-material rejection.

## 2026-06-09 Confirmatory Rerun

A confirmatory rerun used the same accepted `.11` EEL, JDSP limiter setting,
slider points, repetition count, and material filter:

```bash
node tools/axiom-team/bin/axiom-team.mjs map-sub-gain \
  20260603T004349-post-acceptance-v4-1-4-1-0d309b \
  --slider-db 4 --slider-db 10 --slider-db 12 \
  --label-regex 'electronic|hip hop|bass|flawed'
```

The rerun again recorded `FAIL`, with the same engineering interpretation:

- normal material stayed unclipped through `+12 dB`;
- the hard failure was a repeatability qualification failure at the accepted
  `+4 dB` control point on the dense electronic item;
- flawed-source clipping remained confined to the declared flawed-source
  stress material;
- terminal-pressure observations were driven by the flawed-source stress
  material;
- elevated `+10 dB` and `+12 dB` settings again showed repeatable RMS retreat
  on hip-hop/trap-sub and bass-light material.

The rerun's range result was:

```text
Highest tested slider setting without normal-material clipping: +12 dB
Slider settings with normal-material clipped samples: none
Slider settings reaching terminal-pressure observation zone: +4, +10, +12 dB
Slider settings with repeatable RMS retreat beyond -1 dB versus default: +10, +12 dB
```

RMS-retreat observations from the rerun:

| Slider | Material class | RMS change versus +4 dB |
| ---: | --- | ---: |
| +10 dB | hip-hop/trap-sub | -2.258 dB |
| +10 dB | bass-light control | -2.980 dB |
| +12 dB | hip-hop/trap-sub | -2.861 dB |
| +12 dB | bass-light control | -3.960 dB |

This strengthens the conclusion that the open question is not normal-material
clipping through `+12 dB`; it is whether elevated Sub Harmonics settings create
an audible user-control tradeoff such as practical loudness retreat, kick
softening, bass blur, or fatigue.

## Measurement Summary

| Slider | Material | Highest peak (dBFS) | Mean RMS (dBFS) | Clipped samples | Qualified scalar metrics |
| ---: | --- | ---: | ---: | ---: | --- |
| +4 dB | CC0 electronic outlaw high energy | -0.618 | -12.504 | 0 | peak, crest |
| +4 dB | CC0 instrumental hip hop high energy | -0.805 | -13.489 | 0 | peak, RMS, crest, P99 |
| +4 dB | CC0 moil upright bass jazz high energy | -0.971 | -14.736 | 0 | peak, RMS, crest, P95, P99 |
| +4 dB | CC0 derived flawed clipped electronic | -0.000 | -10.533 | 4 | none |
| +4 dB | CC0 derived bass light piano | -11.143 | -29.122 | 0 | peak, RMS, crest, P99 |
| +10 dB | CC0 electronic outlaw high energy | -0.684 | -13.989 | 0 | RMS, P95 |
| +10 dB | CC0 instrumental hip hop high energy | -0.886 | -15.745 | 0 | peak, RMS, crest, P95 |
| +10 dB | CC0 moil upright bass jazz high energy | -0.983 | -15.509 | 0 | peak, RMS, crest |
| +10 dB | CC0 derived flawed clipped electronic | 0.000 | -10.832 | 6 | none |
| +10 dB | CC0 derived bass light piano | -14.040 | -32.102 | 0 | peak, RMS, crest, P95 |
| +12 dB | CC0 electronic outlaw high energy | -0.797 | -14.298 | 0 | peak, RMS, crest, P99 |
| +12 dB | CC0 instrumental hip hop high energy | -0.968 | -16.349 | 0 | peak, RMS, crest |
| +12 dB | CC0 moil upright bass jazz high energy | -0.984 | -15.455 | 0 | peak, RMS, crest, P95, P99 |
| +12 dB | CC0 derived flawed clipped electronic | -0.004 | -10.899 | 0 | RMS, P95 |
| +12 dB | CC0 derived bass light piano | -14.987 | -33.082 | 0 | peak, RMS, crest, P95, P99 |

## Range Findings

- Highest tested slider setting without normal-material clipping: `+12 dB`.
- Slider settings with normal-material clipped samples: none.
- Slider settings reaching the terminal-pressure observation zone: `+4 dB`,
  `+10 dB`, and `+12 dB`.
- Elevated settings with repeatable RMS retreat beyond `-1.000 dB` versus
  default: `+10 dB` and `+12 dB`.

## Interpretation

The result does not prove an unsafe `.11` default, because the accepted `+4 dB`
default did not clip normal material. It also does not justify creating `.12`
immediately, because the failure includes a measurement-repeatability problem
at the default dense electronic point.

The useful signal is narrower:

- elevated user Sub Harmonics settings can trade level/punch for headroom on
  specific material;
- normal-material clipping is not the observed failure through the tested
  range;
- the next decision should focus on whether the elevated-setting RMS retreat is
  audible as bass blur, kick softening, low-end crowding, limiter pumping, or
  fatigue.

Recommended next action: keep `v4.1.4.11` accepted, keep the investigation
open, and prepare a narrow listening/diagnostic question before any `.12`
candidate is created.
