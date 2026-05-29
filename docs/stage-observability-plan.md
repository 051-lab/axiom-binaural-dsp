# Axiom Stage Observability Plan

## Summary

Stage observability is the next Phase 1 measurement foundation task. Its goal
is to explain *where* an output change comes from before any new DSP candidate
is created. The accepted `v4.1.4.10` EEL file remains immutable; observability
uses temporary diagnostic fixtures and reports outside the repository.

The first implementation should extend the existing same-render diagnostic
pattern from `scripts/run_jdsp_stft_audit.py`: write one stage reference path
to the left channel and one processed path to the right channel in a temporary
fixture, then split/analyze the capture after real-JDSP rendering.

## Diagnostic Taps

| Tap | Source point in `.10` chain | Primary question | First-priority metrics |
| --- | --- | --- | --- |
| `dc_input` | after DC blockers, before spatializer | Did input protection alter level or remove useful LF content? | peak/RMS, DC estimate, low-band energy |
| `spatial_out` | after low/mid/high M/S recombine | How much level and M/S balance comes from width processing? | peak/RMS, band S/M, mono sum, M/S leakage |
| `bass_harmonic` | harmonic branch before additive injection | What does generated bass add before it hits the main path? | harmonic spectrum, low-band RMS, IMD/alias probes later |
| `bass_post` | after harmonic injection | How much bass weight and headroom pressure did the branch add? | peak/RMS, crest, low-band energy, S/M, clipping margin |
| `exciter_pre` | before high-pass exciter branch | Is the material level low enough to activate the exciter? | envelope/RMS, high-band RMS, short-window loudness proxy |
| `exciter_post` | after additive exciter injection | Did the exciter add useful air or only level? | high-band RMS, spectral centroid proxy, S/M, peak margin |
| `stft_pre` | immediately before STFT buffering | What enters resonance suppression? | peak/RMS, 2-6 kHz energy, transient metrics |
| `stft_post` | STFT output stream before reserve | What did STFT reconstruction/suppression change? | residual, delay, 2-6 kHz energy, transient spread |
| `reserve_pre` | after STFT, before output gain | What reaches terminal reserve? | peak/RMS, crest, true-peak proxy later |
| `reserve_post` | final output after reserve | How much terminal margin is actually produced? | peak/RMS, crest, output gain, host limiter pressure |

## Fixture Policy

- Generate fixtures into `/tmp`, `~/.local/state/axiom-engineering/`, or a
  caller-supplied output directory outside git.
- Never edit accepted or historical EEL files in place.
- Use explicit stage marker checks before replacing code. If a marker or
  control signature is missing or duplicated, fail rather than guessing.
- Preserve the final EEL write-back contract: the final two `@sample` lines
  must remain `spl0 = out_L;` and `spl1 = out_R;`.
- Keep fixture logic JDSP-safe: no `%`, no forbidden delay/filterbank APIs, no
  overlapping memory, no uninitialized diagnostic variables.
- Treat every fixture as diagnostic, not as a candidate. A fixture can justify
  a later candidate, but it is not a production script.

## First Implementation Target

Build one diagnostic runner before generalizing:

```text
scripts/run_jdsp_stage_observability.py
```

Initial scope:

- Accepted `.10` input only.
- Real-JDSP rendering through the accepted host limiter policy.
- Generated deterministic probes first; registered material can be added after
  the probe path is stable.
- Two fixture modes:
  - `bass_reserve`: left channel = pre-bass spatial output or reserve-pre path,
    right channel = post-bass or reserve-post path.
  - `stft`: retain the existing pre-STFT versus STFT same-render pattern, then
    migrate shared logic out of `run_jdsp_stft_audit.py` only if duplication
    becomes harmful.

Do not begin with every tap. The first useful bottleneck is the
bass/reserve/host-limiter boundary, with STFT kept as the proven diagnostic
pattern.

## Report Shape

Each run should write a machine-readable JSON report and a short Markdown
summary outside git.

Minimum report fields:

- accepted script path and SHA-256;
- fixture mode and generated fixture path;
- host policy: limiter threshold, release, postgain, crossfeed state;
- stimulus/material label and provenance class;
- capture integrity: silence, clipping, frame count, sample rate;
- per-channel peak, RMS, crest, and 20 ms envelope peak;
- M/S peak and RMS where stereo meaning is preserved;
- band energy for low bass, upper bass, low-mid, presence, brilliance, and air;
- stage delta between diagnostic left/right paths;
- pass, fail, or investigate status with reasons.

Raw captures, temporary EEL fixtures, and full reports remain outside git. A
future public decision document may summarize selected findings.

## Acceptance Criteria

The first stage-observability implementation is useful only when all of these
are true:

- Generated fixtures pass `scripts/validate_axiom_static.sh`.
- Real-JDSP captures are not silent and have zero clipped samples unless the
  test intentionally records a boundary failure.
- Same-render diagnostic paths are aligned well enough for level and spectral
  comparison.
- The report can identify whether bass/reserve or STFT explains a measured
  final-output difference.
- The tool refuses to run if source signatures drift from accepted `.10`.
- No generated fixture, WAV, private manifest, or full run output is committed.

## Follow-On Work

After the first runner is stable:

- Add lower-level exciter probes and `exciter_pre`/`exciter_post` diagnostics.
- Add registered-material mode using the existing local manifest policy.
- Add true-peak proxy and Bark/ERB-style perceptual bands.
- Consider a shared fixture-generation module only after two or more runners
  duplicate enough logic to justify extraction.
- Feed summarized results into the bass/host-limiter investigation before any
  `.11` candidate is proposed.
