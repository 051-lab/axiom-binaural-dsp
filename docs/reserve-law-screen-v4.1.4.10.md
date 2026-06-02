# Axiom Reserve-Law Screen v4.1.4.10

Date: 2026-06-01

## Scope

This record summarizes temporary reserve-law fixture tests from the accepted
baseline:

```text
src/axiom_binaural_dsp_v4.1.4.10.eel
Accepted elevated-bass reserve slope: 0.750 dB/dB
Host limiter threshold: -1.00 dB
Host limiter release: 60 ms
Host postgain: 0.00 dB
Crossfeed: disabled
```

The accepted `.10` EEL file was not edited. All tested reserve laws were
external temporary fixtures.

Full WAV captures and JSON/Markdown reports are local artifacts under `/tmp`
and are not committed to the repository.

## Focused +8 dB Screen

Screened slopes:

```text
0.750 reference
0.700
0.625
0.500
```

Measured material:

- `CC0 electronic outlaw high energy`
- `CC0 instrumental hip hop high energy`

The run used two conditioning renders before each measured set. One
conditioning render was not enough for this host route because the first
measured accepted-reference electronic render showed a warm-up RMS outlier.

Result: `VIABLE_REDUCED_RESERVE_IDENTIFIED`

| Slope | Material | Highest peak (dBFS) | Mean RMS (dBFS) | RMS recovery vs 0.750 | Clipped samples |
| ---: | --- | ---: | ---: | ---: | ---: |
| 0.750 | electronic | -0.783 | -14.334 | 0.000 | 0 |
| 0.750 | hip-hop / trap sub | -0.933 | -15.969 | 0.000 | 0 |
| 0.700 | electronic | -0.771 | -14.166 | +0.168 | 0 |
| 0.700 | hip-hop / trap sub | -0.892 | -15.776 | +0.193 | 0 |
| 0.625 | electronic | -0.735 | -13.921 | +0.412 | 0 |
| 0.625 | hip-hop / trap sub | -0.880 | -15.489 | +0.480 | 0 |
| 0.500 | electronic | -0.690 | -13.528 | +0.806 | 0 |
| 0.500 | hip-hop / trap sub | -0.799 | -15.020 | +0.949 | 0 |

Only `0.500 dB/dB` cleared the `+0.50 dB` recovery target on both scoped
low-end stress excerpts.

## Focused Elevated-Range Qualification

The `0.500 dB/dB` slope was then range-qualified on the same two low-end stress
classes at:

```text
+12 dB, +10 dB, +8 dB, +6 dB
```

Result: `VIABLE_REDUCED_RESERVE_RANGE_IDENTIFIED`

| Slider | Material | Highest peak (dBFS) | Mean RMS (dBFS) | Clipped samples |
| ---: | --- | ---: | ---: | ---: |
| +12 dB | electronic | -0.808 | -14.292 | 0 |
| +12 dB | hip-hop / trap sub | -0.970 | -16.347 | 0 |
| +10 dB | electronic | -0.686 | -13.980 | 0 |
| +10 dB | hip-hop / trap sub | -0.883 | -15.742 | 0 |
| +8 dB | electronic | -0.683 | -13.527 | 0 |
| +8 dB | hip-hop / trap sub | -0.914 | -15.020 | 0 |
| +6 dB | electronic | -0.699 | -13.017 | 0 |
| +6 dB | hip-hop / trap sub | -0.705 | -14.240 | 0 |

## Full-Manifest Elevated-Range Qualification

The `0.500 dB/dB` slope was then run across the full registered 14-item
material manifest at:

```text
+12 dB, +10 dB, +8 dB, +6 dB
```

Result: `VIABLE_REDUCED_RESERVE_RANGE_IDENTIFIED`

Local report:

```text
/tmp/axiom-v410-reserve-range-full-slope050-20260530/reserve_range_qualification.md
```

Summary across normal material, excluding the declared flawed-source stress
case:

| Slider | Highest normal-material peak (dBFS) | Track | Normal-material clipped samples |
| ---: | ---: | --- | ---: |
| +12 dB | -0.801 | CC0 electronic outlaw high energy | 0 |
| +10 dB | -0.686 | CC0 electronic outlaw high energy | 0 |
| +8 dB | -0.690 | CC0 electronic outlaw high energy | 0 |
| +6 dB | -0.702 | CC0 instrumental hip hop high energy | 0 |

The declared flawed-source stress case remained an investigation marker instead
of a normal-material rejection:

| Slider | Highest flawed-source peak (dBFS) | Clipped samples |
| ---: | ---: | ---: |
| +12 dB | -0.187 | 0 |
| +10 dB | 0.000 | 4 |
| +8 dB | -0.000 | 3 |
| +6 dB | -0.000 | 2 |

## Interpretation

The `0.500 dB/dB` law is now a legitimate reserve-law listening-candidate
target, but it is not yet an accepted Axiom script.

What is proven:

- the accepted `0.750 dB/dB` law is safe but conservative on the two scoped
  low-end stress classes;
- `0.500 dB/dB` recovers meaningful RMS at `+8 dB`;
- `0.500 dB/dB` remained below the `-0.50 dBFS` observation boundary through
  `+12 dB` on the scoped low-end stress classes;
- `0.500 dB/dB` survived the full 14-item registered manifest at `+12`, `+10`,
  `+8`, and `+6 dB` with no normal-material clipped samples;
- declared flawed-source clipping is still useful stress evidence, but it is
  not a rejection of the normal-material operating range;
- the current JDSP host policy should remain `-1.00 dB`.

What is not proven:

- Android listening acceptance;
- fatigue, bass smear, or pumping behavior;
- whether `0.500 dB/dB` should become `v4.1.4.11`.

Candidate follow-up before any accepted baseline change:

```text
v4.1.4.11 now packages this exact reserve-law target. Listen against accepted
v4.1.4.10 and reject it if the recovered density causes bass blur, pumping,
harshness, stereo instability, or fatigue.
```
