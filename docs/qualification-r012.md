# Axiom Clean R012 Technical Qualification Record

Date: 2026-07-11
Status: Requires investigation

This is a sanitized technical record. Raw captures, local manifests, source
audio, host dumps, and generated reports remain outside the repository.
`../axiom-state.json` is the operational state authority.

## Identity

| Role | Path | SHA-256 |
| --- | --- | --- |
| A: Axiom Clean R011 (accepted) | `src/axiom_binaural_dsp_v4.1.4.11.eel` | `ad7dd7b33f2e62ff03ae08d7101c7ac333d707baef26b952806990ad979b0b0e` |
| B: width-only Labs control | `src/labs/axiom_binaural_dsp_v4.1.4.11_width_profile_lab.eel` | `2e8e192200701cfe49b5cc0cc5046395eb67c76ec4b2fffc64de635d6abe50c9` |
| C: Axiom Clean R012 | `src/axiom_clean_r012.eel` | `774e3d601b471f98b1818ee4ba424abf9e71a494f4a5a228d45c3d6af3ce070d` |

R011 was the accepted comparison and R012 remained the active unqualified
candidate throughout the run. The qualification plan and checkpoint commit
were `docs/qualification-r012-plan.md` and `4a09814` respectively. No DSP or
preset file changed.

## Environment

- JamesDSP: `2.7.0-78-geb848bf`, Pulseaudio flavor.
- Route: serialized managed native playback/capture route, stereo `s16le`,
  native `44.1 kHz`; route restoration completed after the run.
- Host policy: Liveprog and master processing enabled; terminal limiter enabled
  at `-1.00 dB`, `60 ms`, `0 dB` postgain; crossfeed off; other host modules
  disabled.
- Native `48 kHz` and `96 kHz` operation was not available on this route and
  was not represented as a resampled result.

## Coverage And Findings

| Comparison | Coverage | Result |
| --- | --- | --- |
| A/B | deterministic probes; generated program corpus; six sanitized local material classes | No clipped captures. The expected width normalization reduced stereo side energy by about `2.5 dB` on stereo material; this is not a generic transparency failure. |
| B/C | deterministic probes; generated program corpus; six sanitized local material classes at default Sub Harmonics | No clipped captures. Peak differences were within `0.001 dB`, loudness deltas within `0.005 dB`, and side/mid differences within `0.005 dB` on completed default-setting material. |
| A/C | deterministic probes; generated program corpus; six sanitized local material classes | No clipped captures. Differences were dominated by the intended width-profile change; stereo side energy decreased about `2.5 dB` while mono and vocal-oriented material was materially unchanged. |

Completed material categories covered dense electronic, trap-sub, acoustic
bass, vocal/sibilant, mono/narrow, and wide stereo content. Deterministic
coverage included sustained low-frequency material and transient-oriented
probes. Repeated completed captures were stable under the available integrity,
peak, RMS, alignment, and correlation checks. Silence, muted-route, stale
output, and invalid initialization checks did not invalidate completed runs.

Near-ceiling `-1 dB` output occurred on sustained bass and selected program
material with zero clipped samples. This is evidence of terminal-limiter
participation risk, not proof that limiter pressure is unchanged.

## Elevated-Bass Screen

A bounded native-rate A/C screen completed three repetitions at `+4`, `+8`,
and `+12 dB` Sub Harmonics for dense electronic and trap-sub material. It
found no clipped samples and stable repeated scalar measurements. Relative to
R011, R012 showed extra RMS retreat:

| Setting | Dense electronic C-A RMS | Trap-sub C-A RMS |
| --- | ---: | ---: |
| `+4 dB` | `-0.472 dB` | `-0.698 dB` |
| `+8 dB` | `-0.417 dB` | `-0.764 dB` |
| `+12 dB` | `-0.335 dB` | `-0.671 dB` |

R012 also showed lower peak on trap-sub at `+8 dB` (`-0.593 dB`) and `+12 dB`
(`-0.257 dB`). The result is repeatable but not attributable from A/C alone:
it could involve the intended width difference, interpolation behavior, or
unobservable limiter interaction. This is the reason technical qualification
requires investigation rather than proceeding to listening.

## Saturation Analysis Limits

The completed B/C default-setting material and deterministic screen support a
complete-output observation only: the interpolation change was near-neutral
there. They do not isolate a generated-harmonic branch. No claim of true
oversampling is made.

The plan's full `40`, `60`, `80`, and `90 Hz` sine, two-tone, decaying-kick,
and short-transient saturation matrix was not completed. There is no branch
tap, accepted THD/alias threshold, or host limiter gain-reduction/active-time
telemetry. The older sub-harmonics model does not represent R012 interpolation.
The elevated B/C isolation at `+8` and `+12 dB`, `+6`/`+10 dB` settings, and
native `48`/`96 kHz` coverage are also incomplete.

## Elevated B/C Isolation Follow-Up

Date: 2026-07-14

A serialized native `44.1 kHz` B/C map repeated the two elevated settings that
had driven the earlier A/C concern. It used the same terminal limiter
(`-1.00 dB`, `60 ms`, `0 dB` postgain), crossfeed-off host policy, dense
electronic and hip-hop material, and three renders per condition. Raw evidence
remains local under `/tmp`.

| Setting | Material | C-B peak | C-B RMS |
| --- | --- | ---: | ---: |
| `+8 dB` | Dense electronic | `0.000 dB` | `+0.001 dB` |
| `+8 dB` | Hip-hop | `0.000 dB` | `-0.001 dB` |
| `+12 dB` | Dense electronic | `0.000 dB` | `+0.001 dB` |
| `+12 dB` | Hip-hop | `0.000 dB` | `-0.002 dB` |

Neither B nor C clipped. The completed elevated B/C evidence does not show a
candidate-specific level, clipping, or repeatability regression from R012's
interpolated saturation arithmetic. It does not establish true oversampling,
branch-specific behavior, THD, alias performance, or limiter telemetry.

The B control's `+4 dB` dense-electronic RMS spread was `0.155 dB`, exceeding
the `0.100 dB` repeatability limit. Its peak metric remained stable and the
corresponding C condition qualified, but the control's default-level
instability prevents this follow-up from clearing all technical limitations.
R012 therefore remained **Requires investigation** and was not listening
eligible pending the B default-repeatability retest documented below.

## Width-Control Repeatability Retest

Date: 2026-07-14

A five-render native `44.1 kHz` retest ran the B width-only control at the
default `+4 dB` Sub Harmonics setting on the same dense-electronic excerpt.
The managed route restored normally after the run. It produced zero clipped
samples and a stable `-1.000 dBFS` peak, but its RMS spread was `0.149 dB`,
again above the `0.100 dB` repeatability policy. The earlier three-render
control spread was `0.155 dB`.

This confirms a persistent control/host-capture variability limitation rather
than a candidate-specific R012 regression. R012 remains **Requires
investigation** and is not listening eligible. The next safe action is an owner
decision to investigate the managed-host variance with a specifically scoped
conditioning/capture study, or to pause R012; do not change DSP or promote the
candidate.

## Decision

**Requires investigation.** R012 remains active but unqualified. Listening is
pending; R012 is not accepted, promoted, or approved to replace R011.

The single safe next action is an owner decision on a narrowly bounded,
serialized B/C elevated-bass isolation at the supported native rate, with no
DSP changes. Do not begin subjective acceptance listening until that result is
reviewed.
