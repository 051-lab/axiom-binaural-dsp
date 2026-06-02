# Axiom Sub Harmonics Map v4.1.4.10

Date: 2026-06-01

## Scope

This record summarizes scoped real-JDSP Sub Harmonics Gain maps for the
accepted baseline:

```text
src/axiom_binaural_dsp_v4.1.4.10.eel
JDSP limiter threshold: -1.00 dB
JDSP limiter release: 60 ms
JDSP postgain: 0.00 dB
Crossfeed: disabled
Slider points: +4, +6, +8, +10, +12 dB
Repetitions per point: 3
```

Temporary external fixtures changed only the `Sub Harmonics Gain (dB)` default.
The accepted `.10` EEL file was not edited.

Full WAV captures and JSON/Markdown reports are local artifacts under `/tmp`
and are not committed to the repository.

## Result

Status: `PASS_WITH_INVESTIGATION`

Both low-end stress classes remained unclipped through `+12 dB`, and neither
class crossed the `-0.50 dBFS` terminal-pressure observation boundary at
elevated Sub Harmonics settings.

The investigation signal is level retreat: as the slider rises, the accepted
bass-aware reserve law preserves headroom but pulls down broadband RMS and
20 ms envelope energy enough to justify a temporary reserve-law screen.

## Dense Electronic

Material: `CC0 electronic outlaw high energy`

| Slider | Highest peak (dBFS) | Mean RMS (dBFS) | Mean P95 20 ms RMS (dBFS) | RMS delta from +4 dB | Clipped samples |
| ---: | ---: | ---: | ---: | ---: | ---: |
| +4 dB | -0.590 | -12.485 | -9.296 | 0.000 | 0 |
| +6 dB | -0.720 | -13.364 | -9.937 | -0.879 | 0 |
| +8 dB | -0.819 | -14.335 | -10.592 | -1.850 | 0 |
| +10 dB | -0.828 | -15.301 | -11.333 | -2.816 | 0 |
| +12 dB | -0.974 | -16.132 | -11.907 | -3.648 | 0 |

## Hip-Hop / Trap Sub

Material: `CC0 instrumental hip hop high energy`

| Slider | Highest peak (dBFS) | Mean RMS (dBFS) | Mean P95 20 ms RMS (dBFS) | RMS delta from +4 dB | Clipped samples |
| ---: | ---: | ---: | ---: | ---: | ---: |
| +4 dB | -0.681 | -13.473 | -10.356 | 0.000 | 0 |
| +6 dB | -0.874 | -14.687 | -11.227 | -1.214 | 0 |
| +8 dB | -0.927 | -15.969 | -12.424 | -2.496 | 0 |
| +10 dB | -0.976 | -17.200 | -13.578 | -3.727 | 0 |
| +12 dB | -0.984 | -18.314 | -14.475 | -4.841 | 0 |

## Host Limiter Check

A scoped limiter-threshold sweep on `CC0 electronic outlaw high energy` produced
two useful observations:

- `-0.50 dB` clipped once, so it is not a safe replacement for the accepted
  host policy.
- Compared with a stricter `-3.00 dB` limiter threshold, the accepted
  `-1.00 dB` threshold measured `+1.136 dB` RMS and `+1.498 dB` P95 20 ms RMS
  higher on qualified scalar metrics.

This supports keeping `-1.00 dB` as the host policy while investigating the
internal reserve law separately.

## Interpretation

The accepted `.10` low-end path is safe on these scoped low-end stress cases,
but it appears conservative above the default `+4 dB` Sub Harmonics setting.

This was not enough by itself to create a permanent `.11` candidate. It was
enough to run a temporary reserve-law screen against the same low-end stress
classes.

Recommended next screen:

```text
Reserve slopes: 0.625, 0.700, 0.750, 0.875, 1.000 dB/dB
Material: dense electronic and hip-hop/trap-sub first
Target: recover at least 0.50 dB RMS or P95 envelope at +8 to +12 dB
Boundary: no clipping, no peak above -0.50 dBFS, no obvious M/S instability
```

Follow-up: the reserve-law screen and full-manifest range qualification are now
recorded in `docs/reserve-law-screen-v4.1.4.10.md`. The temporary
`0.500 dB/dB` elevated-bass reserve law is candidate-worthy, but not accepted.
