# Airwindows Open Source DSP

Type: documentation
Author: Chris Johnson
Year: ongoing
Publisher or venue: Airwindows GitHub repository
Identifier or URL: https://github.com/airwindows/airwindows
Source ID: airwindows-open-source-dsp
Access notes: Public upstream repository. Intake should pin a specific upstream
commit before indexing; the 2026-06-15 planning check resolved `master` to
`1a84b7d4ccec52c2a7b9f1e8a9046e93d09c9ce0`.

## Summary

Airwindows is a public collection of audio effect source code and effect
descriptions by Chris Johnson. It is useful to Axiom as a broad map of audio
effect ideas, naming vocabulary, and possible test questions around nonlinear
texture, dynamics, spatial utility processing, bass handling, air-band
treatment, filtering, and dithering.

The repository is MIT licensed. Axiom still uses a stricter default boundary:
agents may extract clean-room concepts and research questions, but must not
copy implementation structure, constants, comments, distinctive naming, or
translated C++ logic into EEL without a separate provenance and license review.

## Axiom-Relevant Concepts

- Nonlinear stages can be studied as perceptual goals such as density, edge,
  loudness, or clipping risk, then converted into Axiom-native diagnostics.
- Bass and low-frequency processors can inform questions about punch, blur,
  headroom, RMS retreat, and terminal limiter pressure.
- Dynamics and envelope tools can suggest measurement fixtures for attack,
  release, pumping, and transient contrast.
- High-frequency and air-band tools can inform exciter-risk listening
  vocabulary without justifying a retune by themselves.
- Spatial utilities can help frame Labs questions while preserving Axiom Core's
  speaker-neutral and host-crossfeed boundaries.

## Possible Axiom Follow-Up

- research question: Which Airwindows effect families suggest testable Axiom
  Labs hypotheses without changing the accepted baseline?
- diagnostic or fixture: local-only Airwindows metadata index queried through
  the Codex helper, returning effect names, tags, and relative upstream paths
  only.
- affected area: Knowledge, Labs, docs, tooling

## Evidence Boundary

This note can inform test design. It is not proof that Axiom behaves a certain
way, not listening acceptance, and not permission to create an Axiom Clean
candidate. Airwindows-inspired ideas must pass through Knowledge, Labs,
diagnostic evidence, measurement, listening target, candidate qualification,
and explicit user acceptance before they can affect Core.
