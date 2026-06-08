# DAFX: Digital Audio Effects

Type: book
Author: Udo Zoelzer
Year: 2002
Publisher or venue: John Wiley & Sons
Identifier or URL:
Source ID: dafx-digital-audio-effects
Access notes: Local PDF is registered in the local-only Axiom Knowledge source
index. Do not commit the PDF or private local paths.

## Summary

This source is a broad digital-audio-effects reference. For Axiom, it is most
useful as a conceptual map for effect categories, processing-stage vocabulary,
measurement questions, and safe ways to reason about filters, delays, dynamics,
nonlinear processing, modulation, and time-frequency processing.

## Axiom-Relevant Concepts

- effect taxonomy: useful when naming whether an Axiom idea belongs to width,
  enhancement, dynamics, spectral processing, or another stage;
- stage isolation: useful for designing diagnostics that ask one question at a
  time instead of changing many variables together;
- nonlinear and dynamics caution: relevant to avoiding hidden level,
  intermodulation, fatigue, or limiter-pressure side effects;
- time-frequency framing: relevant to STFT-related reasoning without bypassing
  Axiom's JDSP/EEL2 API constraints.

## Possible Axiom Follow-Up

- research question: Which DAFX categories map cleanly to the accepted Axiom
  chain, and which would be inappropriate for Axiom Core?
- diagnostic or fixture: Create future concept notes for dynamics, nonlinear
  enhancement, and spectral processing as separate Axiom test-design topics.
- affected area: Knowledge, Core, Labs, Qualification

## Evidence Boundary

This note can inform DSP vocabulary and fixture design. It is not proof that
Axiom behaves a certain way, and no algorithm from this source should be
implemented without EEL2/JDSP safety review and local measurement.
