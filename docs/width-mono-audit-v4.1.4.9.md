# v4.1.4.9 Width and Mono Compatibility Audit

## Status

The accepted `v4.1.4.9` spatial stage has been audited through real JDSP
capture using low-level diagnostic probes and a temporary unity-width fixture.
The accepted EEL script was not modified.

Harness run: `20260526T200526-determine-whether-accept-e5c3de`

Conclusion: **no immediate DSP candidate is justified by integrity or channel
leakage**, but the nominal low-bass mono description requires qualification.
The accepted width settings measurably widen side energy in the crossover
transition near `90 Hz`, which is a legitimate future listening investigation
if tighter bass centering becomes a design priority.

## Method

The audit rendered two deterministic low-level multitone probes through real
JDSP at the accepted host-limiter setting:

| Probe | Input relationship | Measurement purpose |
| --- | --- | --- |
| Pure mid | `L = R` | Detect unintended `M->S` leakage and provide a render control |
| Pure side | `L = -R` | Detect unintended `S->M` leakage and map side-width behavior |

The accepted script was rendered unchanged. A temporary comparison fixture
changed only `slider2`, `slider5`, and `slider6` defaults to `100%`. Captures
and the temporary fixture remain outside the repository.

## Results

All four captures passed integrity checks:

| Setting | Probe | Output peak (dBFS) | Clipped samples |
| --- | --- | ---: | ---: |
| Unity width | Pure mid | `-14.137` | `0` |
| Unity width | Pure side | `-18.340` | `0` |
| Accepted width | Pure mid | `-14.830` | `0` |
| Accepted width | Pure side | `-13.733` | `0` |

No measurable `M->S` or `S->M` leakage was reported at any tested frequency
from `63 Hz` through `16 kHz` in either fixture.

### Side Width Map

| Frequency (Hz) | Unity `S->S` (dB) | Accepted `S->S` (dB) | Accepted - unity (dB) |
| ---: | ---: | ---: | ---: |
| 63 | `-30.713` | `-25.204` | `+5.510` |
| 90 | `-12.245` | `-6.738` | `+5.507` |
| 250 | `-2.441` | `+3.091` | `+5.531` |
| 1000 | `-1.001` | `+4.522` | `+5.523` |
| 2400 | `-1.265` | `+4.060` | `+5.325` |
| 6000 | `-1.160` | `+2.612` | `+3.772` |
| 10000 | `-1.100` | `+2.395` | `+3.495` |
| 16000 | `-1.607` | `+1.787` | `+3.394` |

The approximately `+5.5 dB` accepted increase through low-mid content agrees
with the configured `1.35 * 1.40 = 1.89` mid-side width product. The
approximately `+3.4 dB` upper-treble increase agrees with the configured
`1.35 * 1.10 = 1.485` high-side width product.

## Findings

1. The spatializer preserves channel symmetry for controlled pure-mid and
   pure-side input. This audit found no unintended center/side cross-coupling.

2. Accepted width does not create controlled-probe clipping or terminal-level
   pressure at the measurement level used here.

3. The low-frequency mono fold is not a hard `150 Hz` boundary. Although the
   low-pass branch is mono, residual side signal from the widened high-pass
   crossover branch remains at `90 Hz`: accepted `S->S` measures `-6.738 dB`.

4. Relative to unity width, accepted settings add approximately `+5.5 dB` of
   side response at both `63 Hz` and `90 Hz`. At `63 Hz` the residual remains
   strongly attenuated (`-25.204 dB`); at `90 Hz` it is materially present.

5. Pure-mid accepted-versus-unity render differences at low frequencies are
   not interpreted as width effects. Width multiplication cannot act when
   input side is zero; those differences arise from separate hosted renders
   and dynamic-stage state.

## Next Gate

Do not create a new Axiom iteration solely because the width audit passed.

If the design objective is to retain the current expansive presentation,
`v4.1.4.9` remains appropriate. If tighter mono bass or speaker compatibility
is prioritized, the next controlled investigation should evaluate a
low-frequency side-width taper or narrower low-mid transition against `.9`,
with listening focused on kick solidity, bass-image stability, synth width,
and whether the preferred immersive quality is reduced.
