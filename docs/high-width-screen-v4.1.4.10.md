# v4.1.4.10 High-Frequency Width Screen Decision Record

## Status

No new DSP listening candidate is justified from this screen.
`src/axiom_binaural_dsp_v4.1.4.10.eel` remains unchanged as the accepted
baseline.

## Question

The accepted `.10` baseline retains the high-frequency width setting inherited
from `.9`: `slider6 = 110%` under the `slider2 = 135%` global width control.
This screen tested whether temporarily reducing only that high-frequency
multiplier would identify a measurable excess in presence, brilliance, or air
that warranted human A/B evaluation.

| Temporary setting | `slider6` | Effective high-band side product |
| --- | ---: | ---: |
| Accepted `.10` | `110%` | `1.4850x` |
| Restrained fixture | `105%` | `1.4175x` |
| Neutral-multiplier fixture | `100%` | `1.3500x` |

The fixtures changed only the two `slider6` default sites during real-JDSP
renders. They did not modify the accepted `.10` source.

## Measured Result

Four registered CC0 excerpts were rendered through JDSP. The table reports
mean output side-to-mid (`S/M`) differences across the material set.

| Band | Accepted `.10` - source | Restrained - accepted | Neutral - accepted |
| --- | ---: | ---: | ---: |
| Presence edge, `4-7 kHz` | `+3.973 dB` | `-0.198 dB` | `-0.433 dB` |
| Brilliance, `7-12 kHz` | `+3.524 dB` | `-0.360 dB` | `-0.749 dB` |
| Air, `12-18 kHz` | `+3.364 dB` | `-0.396 dB` | `-0.816 dB` |
| Mean across tested bands | `+3.620 dB` | `-0.318 dB` | `-0.666 dB` |

The accepted high-frequency widening is therefore measurable and consistent,
but it is an existing spatial characteristic rather than evidence of a defect.
The restrained alternative makes a relatively small reduction in the exact
brilliance and air behavior previously accepted by listening.

## Integrity Result

All twelve renders completed with zero clipped samples. Accepted `.10` passed
the terminal observation boundary on every excerpt, with its highest peak at
`-0.653 dBFS` on dense electronic material. The temporary `105%` fixture
produced the only observation result, reaching `-0.423 dBFS` on that excerpt
and exceeding the `-0.50 dBFS` observation boundary.

Reducing high width therefore did not demonstrate a headroom advantage in the
highest-pressure tested material. Its only technical benefit in this screen is
a modest reduction of measured high-band side emphasis.

## Decision

Do not create `v4.1.4.11` from high-frequency width restraint on this
evidence. The accepted `.10` setting is measurably intentional, has already
passed listening evaluation as clean and non-harsh, and did not trigger the
terminal-level observation seen in the restrained fixture.

Reopen high-frequency width only if listening reports glare, sibilant
instability, excessive spatial edge, or if a broader registered-material set
shows a repeatable integrity problem under accepted `.10`.
