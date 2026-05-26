# v4.1.4.9 Accepted Baseline Qualification Record

## Status

`src/axiom_binaural_dsp_v4.1.4.9.eel` is the accepted baseline derived from
`v4.1.4.8`. It changes only the terminal reserve applied when `Sub Harmonics
Gain` is above the accepted `+4 dB` default.

Managed real-host qualification completed with an explicit investigation
marker, as documented below. Device A/B listening against `.8` subsequently
accepted `.9` as the new baseline.

## Candidate Change

At `slider1 <= +4 dB`, `.9` is output-gain identical to `.8`. Above default,
the candidate retains more level while still reserving additional peak margin:

```text
bassReserveDb = max(0, slider1 - 4) * 0.750
outputGain = -1 dB fixed reserve - bassReserveDb
```

This change does not alter the bass generator, spatial processing, exciter,
STFT suppressor, host-limiter ownership, or crossfeed policy.

## Evidence Before Candidate Creation

Temporary EEL fixtures based on `.8` were captured through the real JDSP host
path with externally stored CC0 excerpts. The `0.750 dB/dB` reserve slope
qualified at every tested slider/material combination:

| Slider setting | Highest observed candidate peak | Result |
| --- | ---: | --- |
| `+12 dB` | `-0.960 dBFS` | PASS |
| `+10 dB` | `-0.912 dBFS` | PASS |
| `+8 dB` | `-0.780 dBFS` | PASS |
| `+6 dB` | `-0.669 dBFS` | PASS |

All 16 tested `0.750 dB/dB` captures had zero clipped samples. At `+8 dB`,
relative to the full-reserve `.8` behavior, the reduced slope restored
approximately `+0.863 dB` RMS on the electronic excerpt and `+0.969 dB` RMS
on the hip-hop excerpt while retaining safe measured peaks.

The `0.500 dB/dB` alternative was rejected: the electronic excerpt reached
`-0.473 dBFS` at `+6 dB`, crossing the `-0.500 dBFS` observation boundary,
although no clipped samples were recorded.

The full reports and CC0 assets intentionally remain in local measurement
state rather than in this repository.

## Managed Real-Host Qualification

The managed `.8` versus `.9` JDSP session completed with
`PASS_WITH_INVESTIGATION` at a persistent `-1.00 dB` host limiter threshold.
The `.9` comparison contract expects recovered level relative to `.8` at
elevated Sub Harmonics settings, rather than incorrectly requiring `.9` to
add more attenuation than `.8`.

| Check | Result | Observation |
| --- | --- | --- |
| Default continuous probes | PASS | Peak deltas from `-0.002` to `+0.008 dB`; zero clipping |
| `+8 dB` bass burst recovery | PASS | `+1.000 dB` relative to `.8`; zero clipping |
| `+8 dB` correlated mono recovery | PASS | `+1.001 dB` relative to `.8`; zero clipping |
| `+8 dB` side-only recovery | PASS | `+0.954 dB` relative to `.8`; zero clipping |
| `+8 dB` sustained pressure margin | PASS | Candidate peak `-0.996 dBFS` |
| `+12 dB` boundary terminal margin | PASS | Candidate peak `-4.387 dBFS`; zero clipping |
| Generated program corpus | PASS | Three passages, zero clipping |
| External CC0 material | INVESTIGATE | All four excerpts unclipped; electronic excerpt peaked at `-0.443 dBFS` |

The electronic excerpt's default-control observation is not caused by the
new reserve slope: `.8` peaked at `-0.442 dBFS` and `.9` at `-0.443 dBFS`
for that excerpt. It is retained as existing host-limiter participation close
to the terminal ceiling and must be considered during listening.

During qualification development, an earlier external-material run exhibited
an integrity-only peak mismatch on formula-identical default processing. The
managed runner now writes current failure reports reliably and permits one
fresh rerun only for this no-clipping integrity-instability case; clipping is
never retried away.

## Listening Gate Result

- On 2026-05-26, device A/B listening compared `.9` against `.8`.
- The user accepted `.9` as the new baseline after that comparison.
- The decision closes the required human listening gate for the reduced
  elevated-bass reserve change.
