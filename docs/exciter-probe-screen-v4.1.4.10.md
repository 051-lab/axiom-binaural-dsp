# v4.1.4.10 Low-Level Exciter Probe Screen Decision Record

## Status

Measurement complete. No `v4.1.4.11` exciter candidate is justified from this
screen.

`src/axiom_binaural_dsp_v4.1.4.10.eel` remains unchanged as the accepted
baseline.

## Question

The registered-material exciter sensitivity screen showed almost no difference
between accepted `50%`, reduced `35%`, and bypassed `0%` sensitivity on dense
high-energy material. That proved the accepted exciter was not adding obvious
high-frequency pressure there, but it did not prove whether the stage is useful
on quiet material.

This follow-up used generated deterministic probes instead of private music:

- quiet air-bearing harmonic material;
- quiet dull-control harmonic material;
- quiet sibilance-texture bursts;
- a louder bright air-control probe.

Each probe was rendered through real JDSP with temporary fixtures for accepted
`50%`, reduced `35%`, and bypassed `0%` `slider3` sensitivity. The accepted
host policy was used: JDSP master limiter enabled at `-1.00 dB`, `60 ms`
release, `0 dB` postgain, and crossfeed disabled.

## Measured Result

The table reports accepted output minus bypassed output, and accepted output
minus reduced output, by band. The report was rerun after adding absolute
band-RMS context, a `-90.0 dBFS` decision floor, and a `0.20 dB` tolerance for
small reduced-versus-bypass ordering differences.

| Probe | Band | Accepted - bypass RMS | Accepted - reduced RMS | Accepted - bypass `S/M` |
| --- | --- | ---: | ---: | ---: |
| Low-level air activation | Presence edge, `4-7 kHz` | `-2.802 dB` | `+0.213 dB` | `-0.108 dB` |
| Low-level air activation | Brilliance, `7-12 kHz` | `-2.705 dB` | `+0.415 dB` | `+0.125 dB` |
| Low-level air activation | Air, `12-18 kHz` | `+1.592 dB` | `+1.728 dB` | `+0.269 dB` |
| Low-level dull control | Presence edge, `4-7 kHz` | `-0.010 dB` | `-0.008 dB` | `-0.125 dB` |
| Low-level dull control | Brilliance, `7-12 kHz` | `-0.840 dB` | `-0.313 dB` | `-0.378 dB` |
| Low-level dull control | Air, `12-18 kHz` | `+0.882 dB` | `+0.543 dB` | `+0.249 dB` |
| Low-level sibilance texture | Presence edge, `4-7 kHz` | `-0.098 dB` | `-0.016 dB` | `-0.230 dB` |
| Low-level sibilance texture | Brilliance, `7-12 kHz` | `-1.245 dB` | `-0.282 dB` | `-0.436 dB` |
| Low-level sibilance texture | Air, `12-18 kHz` | `-4.204 dB` | `-0.267 dB` | `+0.012 dB` |
| High-level air control | Presence edge, `4-7 kHz` | `-0.027 dB` | `-0.002 dB` | `-0.001 dB` |
| High-level air control | Brilliance, `7-12 kHz` | `-0.028 dB` | `-0.002 dB` | `+0.001 dB` |
| High-level air control | Air, `12-18 kHz` | `+0.005 dB` | `+0.003 dB` | `+0.003 dB` |

Absolute band level matters here. The dull-control air band measured
`-104.991 dBFS` accepted and `-105.873 dBFS` bypassed, so its `+0.882 dB`
difference is below the decision floor and is not treated as audible evidence
that the exciter is manufacturing air.

## Activation Checks

| Check | Result | Interpretation |
| --- | --- | --- |
| Quiet air-bearing material should show air lift | Pass: `+1.592 dB` accepted over bypass in `12-18 kHz` | The accepted exciter does activate on low-level material that contains useful air-band content. |
| Accepted/reduced/bypass depth order should be monotonic | Pass: accepted over reduced was `+1.728 dB`, within the `0.20 dB` tolerance relative to accepted over bypass at `+1.592 dB` | The small ordering irregularity is not decision-grade evidence of a broken sensitivity law. |
| Dull material should not receive meaningful air lift | Pass: `+0.882 dB` accepted over bypass, but both compared air-band levels were below `-90 dBFS` | This is floor-level movement, not proof of audible air being manufactured from dull material. |
| Louder bright material should show less level-contingent lift | Pass: `+0.005 dB` accepted over bypass in `12-18 kHz` | The stage correctly backs off when the bright probe is loud. |
| Sibilance presence should not be over-lifted | Pass: `-0.098 dB` accepted over bypass in `4-7 kHz` | The accepted setting did not add presence-edge pressure on the generated sibilance probe. |

## Integrity Result

All twelve renders completed with zero clipped samples. Every render stayed
well below the `-6.00 dBFS` terminal observation ceiling used for this
low-level screen.

The highest peak was the bypassed high-level air-control render at
`-15.005 dBFS`, so the host limiter was not a meaningful confounder in this
probe run.

## Decision

Do not create an exciter-retune candidate from this screen.

The accepted `.10` exciter is doing something useful: it adds measurable
air-band energy to quiet air-bearing content and almost completely backs off
on louder bright material. It also avoids presence-edge lift on the sibilance
probe.

The earlier weak point was not "the exciter is broken." It was that the first
report did not show absolute band level, so near-silence dB deltas were easy to
overread. With floor-aware evaluation, the generated probes now support the
accepted `.10` exciter behavior.

The next exciter work should remain diagnostic rather than candidate-oriented:

- add an exciter-specific stage tap or offline branch model before retuning;
- refine the dull-control probe so its intended air-band floor is quantified;
- test additional sensitivity points such as `25%`, `35%`, `50%`, and `65%`
  only if a new listening concern points back to the exciter;
- require listening evidence before any `slider3` default change.
