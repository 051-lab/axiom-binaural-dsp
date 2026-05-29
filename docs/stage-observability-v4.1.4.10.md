# v4.1.4.10 Bass/Reserve Stage Observability Record

## Status

Measurement complete. No bass or reserve candidate is justified from this
screen.

`src/axiom_binaural_dsp_v4.1.4.10.eel` remains unchanged as the accepted
baseline.

## Question

The accepted `.10` baseline has a strong subjective bass character and a
host-owned limiter boundary. This diagnostic run asked where bass weight and
reserve pressure appear inside the accepted script before any further
refinement is considered.

The run used temporary same-render fixtures only:

- `spatial_out -> bass_post` compares the spatial output tap against the
  post-bass harmonic tap;
- `reserve_pre -> reserve_post` compares the final pre-reserve tap against the
  post-reserve tap.

Each fixture routes the reference tap to the left output channel and the
candidate tap to the right output channel inside the same render. This makes
the result a diagnostic tap comparison, not a production stereo render.

## Measured Result

| Pairing | Stimulus | Reference tap | Candidate tap | Ref peak | Cand peak | Ref RMS | Cand RMS | Cand - ref RMS | Low-bass delta | Upper-bass delta |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `spatial_to_bass` | `bass_burst` | `spatial_out` | `bass_post` | `-4.570 dBFS` | `-1.451 dBFS` | `-14.332 dBFS` | `-12.736 dBFS` | `+1.596 dB` | `+0.346 dB` | `+2.927 dB` |
| `spatial_to_bass` | `bass_pressure_90hz` | `spatial_out` | `bass_post` | `-4.085 dBFS` | `-0.995 dBFS` | `-12.659 dBFS` | `-7.958 dBFS` | `+4.701 dB` | `+4.644 dB` | `+4.662 dB` |
| `spatial_to_bass` | `correlated_mono` | `spatial_out` | `bass_post` | `-5.481 dBFS` | `-2.297 dBFS` | `-16.739 dBFS` | `-12.641 dBFS` | `+4.098 dB` | `+6.067 dB` | `+6.076 dB` |
| `reserve_pre_to_post` | `bass_burst` | `reserve_pre` | `reserve_post` | `-1.358 dBFS` | `-2.359 dBFS` | `-12.650 dBFS` | `-13.650 dBFS` | `-1.000 dB` | `-1.000 dB` | `-1.000 dB` |
| `reserve_pre_to_post` | `bass_pressure_90hz` | `reserve_pre` | `reserve_post` | `-0.995 dBFS` | `-1.995 dBFS` | `-7.922 dBFS` | `-8.922 dBFS` | `-1.000 dB` | `-1.000 dB` | `-1.000 dB` |
| `reserve_pre_to_post` | `correlated_mono` | `reserve_pre` | `reserve_post` | `-1.343 dBFS` | `-2.343 dBFS` | `-11.623 dBFS` | `-12.623 dBFS` | `-1.000 dB` | `-1.000 dB` | `-1.000 dB` |

## Integrity Result

All twelve diagnostic tap channels passed integrity checks. There were zero
clipped samples, no silence failures, and no host-route failure.

The highest observed diagnostic tap peak was `-0.995 dBFS` before reserve on
the `bass_pressure_90hz` stimulus. The corresponding post-reserve tap was
`-1.995 dBFS`.

## Decision

Do not create a bass or reserve candidate from this evidence.

The bass stage is visibly additive where expected. The strongest 90 Hz
pressure probe gained `+4.701 dB` RMS from `spatial_out` to `bass_post`, with
matching low-bass and upper-bass increases. The correlated mono probe also
shows the intended bass-weight contribution without clipping.

The reserve stage is exactly predictable at the accepted `+4 dB` Sub Harmonics
default: `reserve_post` is `-1.000 dB` relative to `reserve_pre` across peak,
RMS, low-bass, and upper-bass measurements. That confirms the default accepted
path is using the fixed terminal reserve without hidden extra bass-aware
attenuation.

The next work should move to broader metrics and corpus coverage rather than
retuning the low-end. Any future elevated-bass work should use the existing
Sub Harmonics range and reserve-law screens instead of changing the accepted
default path.

