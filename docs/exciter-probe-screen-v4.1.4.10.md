# v4.1.4.10 Low-Level Exciter Probe Screen Decision Record

## Status

Measurement complete with investigation. No `v4.1.4.11` exciter candidate is
justified from this screen alone.

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
minus reduced output, by band.

| Probe | Band | Accepted - bypass RMS | Accepted - reduced RMS | Accepted - bypass `S/M` |
| --- | --- | ---: | ---: | ---: |
| Low-level air activation | Presence edge, `4-7 kHz` | `-2.803 dB` | `+0.214 dB` | `-0.102 dB` |
| Low-level air activation | Brilliance, `7-12 kHz` | `-2.707 dB` | `+0.415 dB` | `+0.128 dB` |
| Low-level air activation | Air, `12-18 kHz` | `+1.590 dB` | `+1.728 dB` | `+0.269 dB` |
| Low-level dull control | Presence edge, `4-7 kHz` | `-0.006 dB` | `+0.004 dB` | `-0.096 dB` |
| Low-level dull control | Brilliance, `7-12 kHz` | `-0.942 dB` | `-0.295 dB` | `-0.552 dB` |
| Low-level dull control | Air, `12-18 kHz` | `+0.864 dB` | `+0.567 dB` | `-0.148 dB` |
| Low-level sibilance texture | Presence edge, `4-7 kHz` | `-0.097 dB` | `-0.016 dB` | `-0.229 dB` |
| Low-level sibilance texture | Brilliance, `7-12 kHz` | `-1.245 dB` | `-0.282 dB` | `-0.436 dB` |
| Low-level sibilance texture | Air, `12-18 kHz` | `-4.204 dB` | `-0.267 dB` | `+0.010 dB` |
| High-level air control | Presence edge, `4-7 kHz` | `-0.027 dB` | `-0.002 dB` | `-0.001 dB` |
| High-level air control | Brilliance, `7-12 kHz` | `-0.028 dB` | `-0.002 dB` | `+0.000 dB` |
| High-level air control | Air, `12-18 kHz` | `+0.005 dB` | `+0.003 dB` | `+0.003 dB` |

## Activation Checks

| Check | Result | Interpretation |
| --- | --- | --- |
| Quiet air-bearing material should show air lift | Pass: `+1.590 dB` accepted over bypass in `12-18 kHz` | The accepted exciter does activate on low-level material that contains useful air-band content. |
| Accepted/reduced/bypass depth order should be monotonic | Investigate: accepted over reduced was `+1.728 dB`, larger than accepted over bypass at `+1.590 dB` | The `35%` fixture measured slightly lower than full bypass in the air band. That is not a reason to retune yet, but it means sensitivity-depth behavior needs a tighter diagnostic before candidate work. |
| Dull material should not receive meaningful air lift | Investigate: `+0.864 dB` accepted over bypass in `12-18 kHz` | The dull-control probe still shows air-band movement. This could be legitimate generated harmonic content, probe design leakage, filter interaction, or exciter overreach. It needs isolation before changing the accepted sound. |
| Louder bright material should show less level-contingent lift | Pass: `+0.005 dB` accepted over bypass in `12-18 kHz` | The stage correctly backs off when the bright probe is loud. |
| Sibilance presence should not be over-lifted | Pass: `-0.097 dB` accepted over bypass in `4-7 kHz` | The accepted setting did not add presence-edge pressure on the generated sibilance probe. |

## Integrity Result

All twelve renders completed with zero clipped samples. Every render stayed
well below the `-6.00 dBFS` terminal observation ceiling used for this
low-level screen.

The highest peak was the accepted high-level air-control render at
`-15.055 dBFS`, so the host limiter was not a meaningful confounder in this
probe run.

## Decision

Do not create an exciter-retune candidate from this screen.

The accepted `.10` exciter is doing something useful: it adds measurable
air-band energy to quiet air-bearing content and almost completely backs off
on louder bright material. It also avoids presence-edge lift on the sibilance
probe.

The weak point is not "the exciter is broken." The weak point is that the
current evidence does not fully explain why the dull-control probe receives
air-band lift, or why reduced `35%` measured slightly lower than bypass on the
quiet air-bearing probe. The next exciter work should be diagnostic:

- add an exciter-specific stage tap or offline branch model before retuning;
- refine the dull-control probe so its intended air-band floor is quantified;
- test additional sensitivity points such as `25%`, `35%`, `50%`, and `65%`
  only after the monotonicity question is better isolated;
- require listening evidence before any `slider3` default change.

