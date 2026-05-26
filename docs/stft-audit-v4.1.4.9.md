# v4.1.4.9 STFT Stage Audit

## Status

The accepted `v4.1.4.9` STFT stage has been audited through real JDSP capture
using diagnostic fixtures only. This audit does not modify the accepted EEL
script and does not justify a sound-changing candidate by itself.

Harness run: `20260526T190151-determine-whether-accept-282005`

Conclusion: **no `v4.1.4.10` STFT candidate is justified**. The STFT stage
introduces measurable round-trip delay and expected signal difference, but
three repeated impulse captures do not identify meaningful transient spreading
or an integrity failure in the accepted configuration.

## Measurement Method

An initial A/B attempt compared separately loaded full-bypass and STFT
fixtures. That method was rejected for interpretation because independent live
loads produced unstable STFT frame/timeline alignment.

The decision-grade diagnostic method instead creates two temporary fixtures
from accepted `.9`:

| Fixture | `slider7` | Diagnostic output mapping |
| --- | ---: | --- |
| Unity round trip | `0%` | Left = pre-STFT mono path; right = STFT-processed path |
| Accepted suppression | `50%` | Left = pre-STFT mono path; right = STFT-processed path |

Only mono probes are used because the diagnostic output channels intentionally
carry different paths. Both paths are captured in the same JDSP render,
removing independent-load scheduling ambiguity from the delay and residual
measurement.

Temporary fixtures and WAV/report artifacts remain under local harness state
and are not committed.

## Same-Render Results

All diagnostic captures passed integrity checks with zero clipped samples.

### Unity STFT Round Trip (`slider7 = 0%`)

| Stimulus | STFT delay (ms) | Correlation | Signal / residual (dB) | STFT peak (dBFS) |
| --- | ---: | ---: | ---: | ---: |
| Impulse | `11.791667` | `0.063505518` | `-2.725` | `-6.488` |
| Bass burst | `11.604167` | `0.999995800` | `50.758` | `-2.353` |
| Sweep | `11.604167` | `0.986585490` | `15.714` | `-1.407` |
| Correlated mono | `22.604167` | `0.993976337` | `19.191` | `-2.389` |

The correlated-mono delay is not treated as a latency estimate because its
periodic content makes alignment ambiguous. Direct peak timing across three
impulse renders established `11.604167 ms` of unity STFT path delay in every
repeat.

### Accepted STFT Suppression (`slider7 = 50%`)

| Stimulus | STFT delay (ms) | Correlation | Signal / residual (dB) | STFT peak (dBFS) |
| --- | ---: | ---: | ---: | ---: |
| Impulse | `11.791667` | `0.088777362` | `-2.517` | `-8.069` |
| Bass burst | `11.604167` | `0.999995799` | `50.756` | `-2.353` |
| Sweep | `11.604167` | `0.972590001` | `12.612` | `-1.407` |
| Correlated mono | `22.604167` | `0.994018405` | `19.225` | `-2.390` |

## Repeated Impulse Transient Results

| Fixture | Peak-arrival delta (ms) | Processed peak vs dry (dB) | Energy-span delta, 5-95% (ms) | Processed minus dry energy within +/-1 ms |
| --- | ---: | ---: | ---: | ---: |
| Unity repeat 1 | `11.604167` | `-0.328` | `0.000000` | `-0.000007` |
| Unity repeat 2 | `11.604167` | `+0.293` | `0.000000` | `-0.000007` |
| Unity repeat 3 | `11.604167` | `+0.732` | `+0.020833` | `-0.000011` |
| Accepted repeat 1 | `11.520833` | `-1.544` | `0.000000` | `-0.000728` |
| Accepted repeat 2 | `11.604167` | `-1.042` | `-0.020833` | `-0.000760` |
| Accepted repeat 3 | `11.604167` | `+0.206` | `0.000000` | `-0.001009` |

At unity, the energy retained within `+/-1 ms` of the impulse peak differs
from the simultaneous dry path by less than `0.0011%` in every repeat. With
accepted suppression active, the difference is at most `0.101%`. The observed
energy-span changes are at most one sample (`0.020833 ms` at `48 kHz`) and are
not evidence of audible transient smearing.

## Findings

1. The accepted STFT layer is not a latency-neutral stage. Direct impulse
   timing measures approximately `11.6 ms` of STFT path latency.

2. Setting suppression to `0%` does not remove the STFT stage's behavior. The
   unity-round-trip sweep comparison retains only `15.714 dB` signal-to-
   residual, confirming a measurable round-trip contribution.

3. Accepted `50%` suppression increases the sweep difference relative to the
   simultaneous pre-STFT path, reducing signal-to-residual from `15.714 dB`
   at unity to `12.612 dB`.

4. The bass-burst result is effectively unaffected by active suppression in
   this audit, as expected for content concentrated below the target
   `2-6 kHz` region.

5. Repeated direct impulse measurements do not show consequential transient
   spread: the maximum 5-95% energy-span delta is one sample and local energy
   concentration remains effectively unchanged at unity and minimally changed
   at accepted suppression.

## Next Gate

Do not create `v4.1.4.10` from the STFT stage. `v4.1.4.9` remains the accepted
listening baseline.

The next investigation should examine an independent part of the accepted
chain, such as mono compatibility and width behavior, using measurement-first
qualification before proposing another listening candidate.
