# Axiom Profile Matrix

This matrix turns the system roadmap into operational rules. Use it when an
idea, issue, Labs experiment, or advisory review needs a destination.

Only Axiom Core is an accepted listening product today. All other profiles are
research, diagnostic, or qualification lanes until they pass the required
promotion gates.

## Matrix

| Profile or Area | Current Status | Operating Authority | Purpose | Allowed Changes | Required Tests Before Promotion |
| --- | --- | --- | --- | --- | --- |
| Axiom Core | Accepted: `v4.1.4.11` | User acceptance plus Codex/Pi qualification | Stable speaker-neutral Axiom listening baseline. | Narrow DSP retunes, removals, or fixes with scoped evidence. | Candidate readiness, static EEL, relevant offline analysis, real-JDSP qualification, listening package, user acceptance, release gates. |
| Axiom Reference | Research/diagnostic | Codex/Pi | Controlled comparison and lower-effect diagnostic profile. | Temporary unity, bypass, reduced-depth, or reference fixtures. | Fixture diff review, static EEL, offline transfer or perceptual-proxy analysis, real-JDSP integrity when host behavior matters. |
| Axiom Immersive | Research/Labs | User direction, Codex/Pi investigation | Stronger spatial or enveloping presentation. | Labs-only width laws, M/S diagnostics, host-crossfeed compatibility tests. | Width/mono audit, material width screen, terminal-margin checks, speaker and headphone listening, crossfeed boundary notes. |
| Axiom Night | Research/Labs | User direction, Codex/Pi investigation | Lower-fatigue or quiet-listening path. | Reduced exciter sensitivity fixtures, STFT-depth variants, reserve or host preset variants. | Low-level exciter probes, sibilance/cymbal checks, STFT audit if changed, fatigue-focused listening records. |
| Axiom Studio Path | Research/diagnostic | Codex/Pi | Engineer-facing diagnostics and translation checks. | Stage taps, measurement presets, analysis-only profile files. | Fixture integrity, repeatability checks, perceptual-proxy review, no private artifact leakage. |
| Axiom Labs | Active research area | Codex/Pi under user direction | Experiments before candidate creation. | Branch-only experiments, temporary fixtures, diagnostic scripts, external review triage. | Research note, scoped hypothesis, offline or fixture evidence, real-JDSP screen when audio behavior is affected. |
| Axiom Knowledge | Active research area | Codex plus advisory sources | Bibliographies, concepts, and test-design notes. | Citations, short summaries, concept maps, research questions. | Source/license review, no copied protected content, clear follow-up task if DSP work is suggested. |
| Axiom Qualification | Active infrastructure | Codex/Pi | Determine whether evidence is strong enough for listening or acceptance. | Validation scripts, corpus metadata, device matrix, report formats, listening validators. | Tooling tests, route/repeatability checks, strict corpus/device readiness when candidate work is involved. |

## Destination Rules

- If the idea changes accepted audio behavior, start in Labs unless a narrow
  qualification-backed candidate already exists.
- If the idea only clarifies documentation or workflow, it belongs in docs or
  Qualification, not Core.
- If the idea comes from a book, article, video, or external LLM, it starts in
  Knowledge or external-review triage.
- If the idea needs a temporary EEL fixture, it belongs in Labs or Reference
  until measured.
- If the idea is a profile concept, it stays out of Core until its profile
  tests and listening target are defined.

## Forbidden Crossovers

Do not:

- merge Labs directly into Core;
- present Reference, Immersive, Night, or Studio Path as accepted products;
- hide a multi-variable profile change inside a narrow Core candidate;
- use advisory feedback as evidence without local testing;
- add private/copyrighted material to Knowledge or Qualification;
- make stronger claims than the current evidence supports.

## Promotion Path

The only path from research to accepted Core is:

```text
idea
  -> research note or issue
  -> diagnostic script or temporary fixture
  -> offline analysis
  -> real JDSP test
  -> listening candidate
  -> qualification
  -> accepted baseline
```

Any stage can stop with "no action" when evidence does not justify further
work.
