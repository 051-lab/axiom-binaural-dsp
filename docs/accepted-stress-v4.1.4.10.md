# Axiom Accepted Stress Baseline v4.1.4.10

Date: 2026-05-30

## Scope

This record summarizes the accepted-setting dense-material stress run for
`src/axiom_binaural_dsp_v4.1.4.10.eel`.

The run used the accepted host contract:

```text
JDSP limiter threshold: -1.00 dB
JDSP limiter release: 60 ms
JDSP postgain: 0.00 dB
Crossfeed: disabled
Repetitions per excerpt: 3
Terminal-pressure observation level: -0.50 dBFS
```

Rendered WAVs and full JSON/Markdown reports are local artifacts and are not
committed to the repository.

## Result

Status: `PASS_WITH_INVESTIGATION`

Normal registered material passed integrity:

- no silent accepted-baseline renders;
- no clipped channel samples on normal material;
- repeatability was stable enough to qualify at least one scalar level metric
  per normal excerpt;
- all normal material except one dense electronic excerpt stayed at or below
  the `-0.50 dBFS` terminal-pressure observation boundary.

Investigation observations:

- `CC0 electronic outlaw high energy` reached `-0.394 dBFS`; this is retained
  as accepted host-limiter pressure, not an EEL defect.
- `CC0 derived flawed clipped electronic` reached `0.000 dBFS` with `8` clipped
  channel samples. Because the manifest declares this excerpt as
  `flawed_source`, the clipping is retained as bad-source stress evidence
  instead of failing the accepted baseline.

## Highest Peaks

| Material | Highest repeated peak (dBFS) | Integrity |
| --- | ---: | --- |
| CC0 electronic outlaw high energy | -0.394 | investigate terminal pressure |
| CC0 instrumental hip hop high energy | -0.644 | pass |
| CC0 moil upright bass jazz high energy | -0.967 | pass |
| CC0 fantasy orchestral crescendo | -0.891 | pass |
| CC0 fight for better future rock metal | -0.740 | pass |
| CC0 emotional piano solo | -9.022 | pass |
| CC0 drum preview cymbals air proxy | -2.462 | pass |
| CC0 crossbowman see sibilant voice | -10.197 | pass |
| CC0 paladin tired speech | -9.924 | pass |
| CC0 derived low level dark cavern ambient | -16.594 | pass |
| CC0 derived mono piano narrow | -18.270 | pass |
| CC0 derived flawed clipped electronic | 0.000 | investigate flawed source |
| CC0 derived bass light piano | -11.136 | pass |
| CC0 derived wide orchestral | -0.927 | pass |

## Interpretation

This does not justify a new EEL candidate by itself. The accepted `.10` baseline
is stable on normal material, and the remaining signal is host-contract
pressure on dense or intentionally flawed material.

The next bass/reserve work should continue with the Sub Harmonics slider map
from `docs/bass-host-limiter-investigation-plan.md`, using the dense electronic
excerpt as a flagged stress case.
