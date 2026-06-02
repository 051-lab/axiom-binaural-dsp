# Axiom Architecture Decision: v4.1.4.10 to v4.1.4.11

Date: 2026-06-01

Status: **v4.1.4.11 accepted**

## Decision

Promote `src/axiom_binaural_dsp_v4.1.4.11.eel` to the accepted Axiom Clean
baseline after measured reserve-law qualification and human listening
acceptance against `v4.1.4.10`.

Keep `src/axiom_binaural_dsp_v4.1.4.10.eel` as the previous accepted
reference. Do not create a broad `.12` tuning candidate and do not start a v5
architecture branch yet.

The next sound-changing candidate is allowed only if it has all of the
following:

- a falsifiable hypothesis;
- a measured target;
- a scoped edit boundary;
- real-host qualification;
- level-controlled listening target;
- explicit human listening acceptance.

The accepted `.11` change is intentionally narrow: it changes only the
elevated-bass reserve slope from `0.750` to `0.500 dB/dB` above the default
`+4 dB` Sub Harmonics setting. It does not alter width, bass generation,
exciter behavior, STFT behavior, crossfeed ownership, or limiter ownership.

## Evidence State

Candidate readiness passed locally before `.11` creation:

- accepted `.10` baseline hash matched policy;
- registered corpus metadata and taxonomy coverage pass strict validation;
- device coverage passes strict validation across Android, speaker,
  wired/USB, Bluetooth, and WSL/JDSP lab routes.

Wired/USB and Bluetooth route completion is recorded as user-attested physical
route evidence. It is useful for readiness and field confidence, but it is not
the same as an automated endpoint-capture report.

The bass/host-limiter investigation now has a completed reserve-law result:

- `0.500 dB/dB` recovered meaningful RMS on focused dense electronic and
  hip-hop/trap-sub excerpts at `+8 dB`;
- the same temporary law survived full-manifest qualification across 14
  registered items at `+12`, `+10`, `+8`, and `+6 dB`;
- normal registered material produced no clipped samples;
- declared flawed-source clipping remains an investigation marker, not a
  normal-material rejection.

## v4 Direction

Continue v4 only through narrow, evidence-backed candidates. Valid `.12`
directions are:

- bass/reserve law refinement if the investigation shows avoidable level
  retreat, punch loss, or terminal-margin instability;
- STFT behavior only if a stage audit or material screen finds measurable
  resonance handling damage;
- spatial defaults only if route-specific listening records show repeatable
  center-image, speaker-translation, or fatigue problems;
- exciter behavior only if low-level material exposes dullness or harshness
  that current probes did not capture.

Invalid `.12` reasons:

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

Before creating any `.12` file, rerun candidate readiness against the accepted
`.11` policy anchor and require a new scoped hypothesis with measured evidence.

That investigation now supports the narrow `.11` reserve-law candidate. The
edit boundary is the elevated-bass reserve slope only. Require Android/package
validation and structured listening acceptance before any baseline promotion.
