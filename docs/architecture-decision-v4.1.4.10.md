# Axiom Architecture Decision: v4.1.4.10 Baseline

Date: 2026-05-30

Status: **candidate-ready, no immediate DSP edit**

## Decision

Keep `src/axiom_binaural_dsp_v4.1.4.10.eel` as the accepted Axiom Clean
baseline. Do not create a broad `.11` tuning candidate and do not start a v5
architecture branch yet.

The next sound-changing candidate is allowed only if it has all of the
following:

- a falsifiable hypothesis;
- a measured target;
- a scoped edit boundary;
- real-host qualification;
- level-controlled listening target;
- explicit human listening acceptance.

The most plausible future candidate area is still bass/reserve/host-limiter
interaction at elevated `Sub Harmonics Gain`, but this remains an investigation
target, not an approved edit.

## Evidence State

Candidate readiness now passes locally:

- accepted `.10` baseline hash matches policy;
- registered corpus metadata and taxonomy coverage pass strict validation;
- device coverage passes strict validation across Android, speaker,
  wired/USB, Bluetooth, and WSL/JDSP lab routes.

Wired/USB and Bluetooth route completion is recorded as user-attested physical
route evidence. It is useful for readiness and field confidence, but it is not
the same as an automated endpoint-capture report.

## v4 Direction

Continue v4 only through narrow, evidence-backed candidates. Valid `.11`
directions are:

- bass/reserve law refinement if the investigation shows avoidable level
  retreat, punch loss, or terminal-margin instability;
- STFT behavior only if a stage audit or material screen finds measurable
  resonance handling damage;
- spatial defaults only if route-specific listening records show repeatable
  center-image, speaker-translation, or fatigue problems;
- exciter behavior only if low-level material exposes dullness or harshness
  that current probes did not capture.

Invalid `.11` reasons:

- making Axiom louder without a measured target;
- changing defaults because another version number is desired;
- adding stages before the current chain shows a specific failure;
- retuning width, exciter, STFT, or bass from preference alone.

## v5 Direction

Defer v5. A v5 branch is justified only by an architecture-level change:

- material-aware adaptive laws that v4 cannot express cleanly;
- redesigned end-to-end gain and reserve architecture;
- formal speaker/headphone/profile architecture;
- validated Axiom Clean versus Axiom Color product split;
- a major proven stage with its own aliasing, IMD, CPU, headroom, mono, side/mid,
  limiter, and listening evidence.

Small tuning edits, default changes, or reserve-slope adjustments remain v4
work.

## Best Next Work

Before creating any `.11` file, run or refresh the bass and host-limiter
investigation described in `docs/bass-host-limiter-investigation-plan.md`.

If that investigation finds no measurable problem, the correct decision is to
leave `.10` unchanged and improve evidence quality, route-specific listening
records, and release hygiene.
