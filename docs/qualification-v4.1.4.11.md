# v4.1.4.11 Accepted Baseline Qualification Record

Date: 2026-06-01

## Status

`src/axiom_binaural_dsp_v4.1.4.11.eel` is the accepted Axiom Clean listening
baseline. It was derived from the accepted `v4.1.4.10` baseline and changes
only the elevated-bass reserve slope above the default `+4 dB` Sub Harmonics
setting.

## Candidate Identity

| Item | Value |
| --- | --- |
| Previous accepted reference | `src/axiom_binaural_dsp_v4.1.4.10.eel` |
| Previous accepted SHA-256 | `2b72288048f3e6a180eb5a0e3d951f34fc463d113bb8d716c03cfda8aeafffc5` |
| Accepted script | `src/axiom_binaural_dsp_v4.1.4.11.eel` |
| Accepted SHA-256 | `ad7dd7b33f2e62ff03ae08d7101c7ac333d707baef26b952806990ad979b0b0e` |
| Host limiter policy | `-1.00 dB`, `60 ms`, `0 dB` postgain |
| Crossfeed during qualification | disabled |

## Scoped Change

The candidate changes only the version description and the elevated-bass
terminal reserve slope used when `Sub Harmonics Gain` is above the accepted
`+4 dB` default.

```text
v4.1.4.10: bassReserveDb = max(0, slider1 - 4) * 0.750
v4.1.4.11: bassReserveDb = max(0, slider1 - 4) * 0.500
```

The default `+4 dB` Sub Harmonics path remains unchanged because the conditional
reserve law is inactive at and below the accepted default. The candidate does
not change spatial width, bass generation, exciter behavior, STFT behavior,
host-limiter ownership, crossfeed ownership, or slider ranges.

## Evidence Before Candidate Creation

The pre-candidate reserve-law investigation used temporary fixtures generated
from the accepted `.10` source. Those fixtures tested the exact production
candidate target before the versioned `.11` file existed.

Focused `+8 dB` screen:

- `0.500 dB/dB` recovered `+0.806 dB` RMS on dense electronic material versus
  the accepted `0.750 dB/dB` reference.
- `0.500 dB/dB` recovered `+0.949 dB` RMS on hip-hop/trap-sub material versus
  the accepted reference.
- The lighter `0.700` and `0.625` alternatives did not clear the `+0.50 dB`
  recovery target on both scoped excerpts.

Full-manifest range qualification:

- `0.500 dB/dB` survived all 14 registered material items at `+12`, `+10`,
  `+8`, and `+6 dB`.
- Normal material produced no clipped samples.
- Highest normal-material peaks were `-0.801 dBFS` at `+12`, `-0.686 dBFS` at
  `+10`, `-0.690 dBFS` at `+8`, and `-0.702 dBFS` at `+6`.
- The declared flawed-source stress item remained investigation evidence and
  is not counted as a normal-material rejection.

See `docs/reserve-law-screen-v4.1.4.10.md` for the full pre-candidate decision
record. Full WAV captures and machine-local reports remain outside the
repository.

## Automated Validation

Completed:

- `scripts/validate_axiom_static.sh src/axiom_binaural_dsp_v4.1.4.11.eel`
- `scripts/validate_axiom_static.sh src/axiom_binaural_dsp_v4.1.4.10.eel`
- `python3 -m unittest discover -s tests -p 'test_*.py'`
- `npm test` in `tools/axiom-team`

Results:

- Static EEL validation passed for `.10` and `.11`.
- Python tests passed: `159`.
- Pi harness tests passed: `22`.

## Listening Acceptance

Result: accepted on 2026-06-01.

The user completed device listening tests against `v4.1.4.10` and reported that
`v4.1.4.11` surpassed `.10`. This closes the candidate gate and promotes `.11`
to the accepted Axiom Clean baseline.

Post-acceptance monitoring should continue to watch for bass blur, limiter
pumping, harshness, stereo instability, or fatigue at elevated Sub Harmonics
settings. Any sound-changing response must create a new versioned script rather
than modifying `.11`.
