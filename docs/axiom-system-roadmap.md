# Axiom System Roadmap

This roadmap defines the future Axiom system architecture. It complements
`axiom-roadmap.md`, which is a 90-day foundations plan. This document is about
product lanes, profile boundaries, and promotion rules.

The accepted product line remains conservative. Profile concepts are not
official products until they pass qualification and listening acceptance.

## System Boundaries

| Area | Role |
| --- | --- |
| Axiom Core | Accepted stable DSP baseline. |
| Axiom Reference | Measurement-focused neutral comparison profile. |
| Axiom Immersive | Spatially stronger research/listening profile. |
| Axiom Night | Low-fatigue and quiet-listening research profile. |
| Axiom Studio Path | Engineer-facing diagnostic and mix-translation path. |
| Axiom Labs | Experimental fixtures, branches, scripts, and research candidates. |
| Axiom Knowledge | Research notes, bibliographies, and concept summaries. |
| Axiom Qualification | Tests, reports, listening records, and release gates. |

## Axiom Core

Purpose:

- Maintain the accepted stable Axiom listening baseline.
- Preserve speaker-neutral behavior with optional host-owned crossfeed.
- Provide a conservative enhancement chain that can be tested repeatedly.

Allowed DSP changes:

- Narrow fixes with a falsifiable hypothesis.
- Small retunes supported by diagnostics, real-JDSP qualification, and listening.
- Removal of unused or harmful complexity when evidence supports removal.

Forbidden changes:

- Broad multi-variable rewrites.
- New processing stages without Labs evidence.
- In-place edits to the accepted EEL file.
- Internal limiter or crossfeed ownership changes without a dedicated
  architecture decision.
- Claims beyond the evidence record.

Required tests before promotion:

- candidate readiness gate;
- static EEL validation;
- relevant offline analysis;
- real-JDSP qualification;
- local listening package;
- structured user listening acceptance;
- updated qualification doc, changelog, and policy hash.

## Axiom Reference

Purpose:

- Provide a controlled comparison target for measurement and A/B work.
- Keep a lower-effect or unity-style profile available for diagnostics without
  redefining the accepted Core sound.

Allowed DSP changes:

- Temporary fixtures that reduce or bypass a single stage for measurement.
- Reference presets or scripts clearly marked as diagnostic.
- Unity-width, exciter-bypass, STFT-depth, or reserve-law fixtures when scoped.

Forbidden changes:

- Presenting Reference as the accepted listening product.
- Merging diagnostic bypasses into Core without a candidate process.
- Using Reference output to claim universal transparency.

Required tests before promotion:

- fixture diff review;
- static EEL validation;
- offline transfer or perceptual-proxy analysis;
- real-JDSP integrity checks when host behavior matters;
- documentation of exactly which stage was bypassed or reduced.

## Axiom Immersive

Purpose:

- Explore stronger spatial presentation for users who prefer a wider or more
  enveloping sound.
- Keep aggressive spatial ideas out of Core until their tradeoffs are measured.

Allowed DSP changes:

- Labs-only width law experiments.
- Material-aware spatial fixtures.
- Host-crossfeed compatibility investigations.
- M/S and mono-compatibility diagnostics.

Forbidden changes:

- Deep-bass widening that creates uncontrolled mono or headroom issues.
- "True binaural" or HRTF claims without direct evidence.
- Coupling headphone-only behavior into the speaker-neutral Core script.

Required tests before promotion:

- width/mono audit;
- material width screen;
- side-to-mid band analysis;
- terminal-margin and clipping checks;
- headphone and speaker listening notes;
- explicit crossfeed-on and crossfeed-off boundary documentation.

## Axiom Night

Purpose:

- Investigate low-fatigue listening at lower volume or longer sessions.
- Reduce harshness and terminal pressure without making the main baseline dull.

Allowed DSP changes:

- Labs-only reduced exciter sensitivity fixtures.
- Lower STFT depth or alternate suppression envelopes.
- Output reserve or loudness-contingent restraint tests.
- Host preset variants when no EEL change is needed.

Forbidden changes:

- Making Core quieter or darker without evidence that the default has a defect.
- Treating subjective comfort as proof without structured listening records.
- Adding compression or limiting inside the script without an architecture
  decision.

Required tests before promotion:

- low-level exciter probes;
- sibilance and cymbal material checks;
- STFT audit if resonance suppression changes;
- long-session listening notes with fatigue fields;
- comparison against Core at controlled host settings.

## Axiom Studio Path

Purpose:

- Support engineering diagnostics, translation checks, and repeatable review.
- Provide tools and optional profiles for analysis rather than consumer sound.

Allowed DSP changes:

- Diagnostic tap fixtures.
- Stage-isolation scripts.
- Measurement presets.
- Analysis-only profile files that are not accepted listening baselines.

Forbidden changes:

- Shipping diagnostic taps as Core behavior.
- Committing captured audio or local manifests.
- Claiming professional mastering accuracy from proxy metrics.

Required tests before promotion:

- fixture integrity validation;
- repeatability checks;
- perceptual-proxy report review;
- documentation of metric scope and limitations;
- no private artifact leakage.

## Axiom Labs

Purpose:

- Hold experiments until they earn promotion.
- Keep research flexible without destabilizing Core.

Allowed DSP changes:

- temporary fixtures;
- branch-only experiments;
- proof-of-concept scripts;
- diagnostic tools;
- external LLM critique triage.

Forbidden changes:

- Direct merge into Core without the graduation ladder.
- Version names that imply acceptance.
- Hidden multi-variable changes.
- Unlicensed material or copyrighted source content.

Required tests before promotion:

- research note;
- scoped hypothesis;
- fixture or diagnostic report;
- offline analysis;
- real-JDSP screen when audio behavior is affected;
- decision to stop, continue, or create a candidate.

## Axiom Knowledge

Purpose:

- Build the project knowledge base for DSP, psychoacoustics, JDSP, testing,
  human hearing, and device behavior.

Allowed changes:

- bibliography entries;
- short summaries;
- concept maps;
- questions for investigation;
- links to lawful public sources;
- notes that connect research to test design.

Forbidden changes:

- committing copyrighted books;
- copying long protected excerpts;
- storing private library paths;
- treating research summaries as evidence of Axiom behavior.

Required tests before promotion:

- source/license review;
- no copied protected content;
- clear distinction between citation, summary, and engineering decision;
- linked follow-up task if the note suggests DSP work.

## Axiom Qualification

Purpose:

- Define whether a candidate is safe and meaningful enough for listening and
  possible acceptance.

Allowed changes:

- validation scripts;
- report formats;
- corpus metadata;
- device matrix rules;
- listening-record validators;
- Pi harness gates.

Forbidden changes:

- making automated metrics the final acceptance authority;
- weakening gates to pass a preferred candidate;
- hiding failed or investigation results;
- committing private captures or source material.

Required tests before promotion:

- relevant unit tests;
- repeatability or route checks for host runners;
- strict corpus and device readiness where candidate work is involved;
- documentation of limitations and known blind spots.

## Promotion Rules

No profile or component becomes official until it has:

- a written purpose;
- a scoped change boundary;
- evidence that identifies the affected stage;
- real-JDSP qualification when host output matters;
- structured listening acceptance from the user;
- updated public documentation;
- a branch and PR that make the change reviewable.
