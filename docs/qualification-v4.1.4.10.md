# v4.1.4.10 Accepted Baseline Qualification Record

## Status

`src/axiom_binaural_dsp_v4.1.4.10.eel` is the accepted listening candidate
derived from `v4.1.4.9`. It changes only the default low-mid spatial width
multiplier from `140%` to `126%`, plus the version description.

Managed real-host qualification passed, and device listening against `.9`
subsequently accepted `.10` for promotion to the baseline.

## Candidate Change

The accepted `.9` global side width remains `135%`. In the `150 Hz-4 kHz`
low-mid band, `.10` changes the default side-width product:

```text
v4.1.4.9: 1.35 * 1.40 = 1.890x
v4.1.4.10: 1.35 * 1.26 = 1.701x
```

This change does not alter bass generation, STFT processing, high-frequency
width, loudness shaping, output reserve, host-limiter ownership, or crossfeed
policy.

## Evidence Before Candidate Creation

Real-JDSP screening of temporary fixtures showed that `.9` was approximately
`+5.3 dB` more side-forward than the source material through `300 Hz-4 kHz`
on four registered CC0 excerpts. A temporary `126%` low-mid setting reduced
that emphasis by approximately `0.8` to `0.9 dB` without clipping or a
terminal-pressure observation. A stronger `115%` alternative was not advanced
because it crossed the `-0.50 dBFS` observation boundary on the dense
electronic excerpt.

See `docs/lowmid-width-screen-v4.1.4.9.md` for the pre-candidate decision
record.

## Managed Real-Host Qualification

The scoped `.9` versus `.10` qualification rendered both versions through
JDSP at the accepted `-1.00 dB` host limiter threshold. It verified that the
candidate edit was restricted to the description and the two `slider5`
default sites, then measured band-specific spatial balance on the four
registered CC0 excerpts.

| Excerpt | Mean candidate - `.9` S/M, `150 Hz-4 kHz` | Candidate peak | Result |
| --- | ---: | ---: | --- |
| Electronic high energy | `-0.918 dB` | `-0.586 dBFS` | PASS |
| Instrumental hip-hop high energy | `-0.897 dB` | `-0.670 dBFS` | PASS |
| Upright-bass jazz high energy | `-0.851 dB` | `-0.976 dBFS` | PASS |
| Orchestral crescendo | `-0.885 dB` | `-0.948 dBFS` | PASS |

Across all material and affected bands, the mean candidate-minus-`.9` side to
mid reduction was `-0.888 dB`. All candidate captures had zero clipped
samples. The highest candidate peak, `-0.586 dBFS`, remained below the
`-0.50 dBFS` terminal observation boundary.

Static EEL validation passed and confirmed the inherited host-limiter,
crossfeed-free, phase-preserving bass, reduced-reserve and final write-back
constraints. The Python test suite passed with `83` tests and the Pi harness
suite passed with `16` tests.

The full captures and machine-local reports remain outside the repository.

## Listening Gate Result

- On 2026-05-26, device listening evaluated `.10` after qualification.
- The user accepted `.10` as the new baseline.
- The decision closes the human listening gate for the restrained low-mid
  width change.
