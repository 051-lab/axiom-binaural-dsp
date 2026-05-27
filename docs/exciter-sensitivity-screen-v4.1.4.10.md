# v4.1.4.10 Dynamic Exciter Sensitivity Screen Decision Record

## Status

No new DSP listening candidate is justified from this registered-material
screen. `src/axiom_binaural_dsp_v4.1.4.10.eel` remains unchanged as the
accepted baseline.

## Question

The accepted `.10` baseline uses `slider3 = 50%` for the dynamic
Fletcher-Munson exciter. The stage is level-dependent: it tracks stereo RMS,
targets lower-level material, high-passes content above the air band, smooths
the additive amount, and caps calculated boost at `10 dB`.

This screen tested whether temporarily reducing only the sensitivity would
show a meaningful reduction in high-frequency energy, side balance, or terminal
pressure on the registered CC0 material set.

| Temporary setting | `slider3` | Relative accepted-depth multiplier |
| --- | ---: | ---: |
| Accepted `.10` | `50%` | `1.00x` |
| Reduced fixture | `35%` | `0.70x` |
| Bypass fixture | `0%` | `0.00x` |

The fixtures changed only the two `slider3` default sites during real-JDSP
renders. They did not modify the accepted `.10` source.

## Measured Result

Four registered CC0 excerpts were rendered through JDSP. The table reports
mean output differences across the material set.

| Band | Accepted `.10` - source RMS | Reduced - accepted RMS | Bypass - accepted RMS | Reduced - accepted `S/M` | Bypass - accepted `S/M` |
| --- | ---: | ---: | ---: | ---: | ---: |
| Presence edge, `4-7 kHz` | `-0.940 dB` | `+0.010 dB` | `+0.003 dB` | `+0.015 dB` | `+0.024 dB` |
| Brilliance, `7-12 kHz` | `-0.769 dB` | `+0.012 dB` | `+0.011 dB` | `+0.002 dB` | `+0.010 dB` |
| Air, `12-18 kHz` | `-1.020 dB` | `+0.017 dB` | `+0.011 dB` | `-0.013 dB` | `+0.001 dB` |
| Mean across tested bands | `-0.910 dB` | `+0.013 dB` | `+0.008 dB` | `+0.002 dB` | `+0.012 dB` |

The temporary sensitivity changes are below a practical decision threshold on
this material. Bypassing the exciter did not meaningfully reduce measured
brilliance or air; in aggregate it was effectively level-neutral relative to
accepted `.10`.

The likely interpretation is that the current exciter is mostly inactive on
these high-energy mastered excerpts because the loudness-contingent envelope
does not request meaningful boost at their rendered levels. That is not a
defect. It means this registered corpus is more useful for proving the exciter
does not add obvious high-frequency pressure than for judging low-level
enhancement behavior.

## Integrity Result

All twelve renders completed with zero clipped samples. Accepted `.10`,
reduced `35%`, and bypass `0%` all stayed below the `-0.50 dBFS` observation
boundary on every excerpt.

The highest accepted peak was `-0.616 dBFS` on dense electronic material. The
highest reduced or bypass peak was `-0.631 dBFS` on the same excerpt for both
temporary fixtures, so reduced sensitivity did not expose a useful headroom
advantage.

## Decision

Do not create `v4.1.4.11` from exciter sensitivity reduction on this evidence.
The measured effect of reducing or bypassing `slider3` on the registered
high-energy material is too small to justify a listening candidate.

The next exciter-specific investigation, if needed, should use controlled
lower-level material or generated low-level tonal/noise passages that actually
exercise the loudness-contingent boost law. It should not retune the accepted
default based on this high-energy corpus alone.
