# Axiom-DSP AI Development Ecosystem

This document converts the local `axiom-idea.html` vision document into a
repository-facing operating framework. Styling and visual layout are not part
of this specification; only the semantic roles, information flow, and workflow
rules are preserved.

## Core Directive

Codex is the repository manager and workflow orchestrator for Axiom-DSP. It
operates in the terminal, maintains the GitHub repository, coordinates local
tools, and converts ideas into scoped engineering work.

The goal is not to let agents freely rewrite the DSP. The goal is to make
Axiom development organized, dependable, testable, and adaptable enough for
research without weakening the accepted baseline.

The current development philosophy is:

- Stability first: the accepted baseline remains conservative and immutable
  until a qualified replacement is accepted.
- Measurement second: new concerns should become diagnostics, fixtures, or
  reports before they become DSP code.
- Experimentation third: broad ideas belong in Labs branches or research notes
  until they pass the graduation ladder.

Axiom should be developed as a product system, not as a collection of one-off
scripts. Every durable change should answer where it belongs: Core, Labs,
Knowledge, Qualification, documentation, or local-only state.

## Ecosystem Flow

### Axiom

Axiom is the project being protected and improved. In this repository it is
represented by:

- versioned EEL2 scripts in `src/`;
- public architecture and qualification records in `docs/`;
- repeatable analysis and JDSP runners in `scripts/`;
- the controlled Pi engineering harness in `tools/axiom-team/`;
- local-only captured evidence and run state outside the repository.

The accepted Axiom line is conservative. Experimental or advisory work can
inform it, but cannot bypass qualification and listening acceptance.

### User: Visionary, Operator, Final Listening Authority

The user supplies strategic direction, listening judgment, device context, and
new research interests. The user is the final authority for acceptance after
measurement gates indicate that a candidate is safe enough to hear.

User responsibilities:

- define product direction and listening priorities;
- provide human-ear validation on real devices;
- approve publication and merge steps;
- decide when a candidate is accepted or rejected.

### Codex: Repository Manager And Workflow Orchestrator

Codex is responsible for turning direction into disciplined engineering work.
It should organize the repository, inspect existing state before acting,
coordinate validation, create or update documentation, and prepare commits and
pull requests only after scope is clear.

Codex responsibilities include:

- repository organization and source-of-truth maintenance;
- branch discipline and PR preparation;
- test orchestration across static, offline, real-JDSP, and listening evidence;
- translating advisory LLM feedback into actionable issues or research notes;
- protecting the accepted baseline from silent or broad edits.

Codex must not treat external opinions, measurements, or its own preferences as
listening acceptance.

### External LLMs: Advisory Review Council

ChatGPT, Claude, Qwen, Gemini, and similar systems may be used as advisory
reviewers. Their role is to critique, suggest, explain, and challenge.

Advisory feedback is useful only after it is normalized into repository work:

1. Capture the critique as a short research note, issue draft, or review
   summary.
2. Identify whether it affects Core, Labs, Knowledge, Qualification, or docs.
3. Convert it into a falsifiable hypothesis or a documentation task.
4. Test it with local tools before any accepted-line change.

External LLM output is not evidence by itself. It is input for investigation.

### Pi And Terminal Workflows: Execution And Verification Layer

Pi sessions and terminal agents execute controlled work: audits, screens,
candidate creation, qualification, and local verification. They should receive
scoped tasks from Codex and return concrete artifacts: reports, diffs, logs,
and status.

Pi work is strongest when it follows a narrow loop:

```text
Observation -> hypothesis -> diagnostic command -> report -> decision
```

Two real-host JDSP measurements must not run at the same time. Real-host
qualification is serialized because shared audio routing can corrupt results.

## Operational Pillars

### Terminal Execution

The terminal layer turns plans into evidence. It should favor deterministic
commands, explicit output paths, and reproducible validation.

Expected outputs include:

- static EEL checks;
- Python and Node tests for tooling;
- offline perceptual-proxy reports;
- real-JDSP repeatability reports;
- sanitized decision records;
- structured listening package artifacts kept local unless safe to publish.

Generated audio captures, private material, local manifests, and device-specific
reports remain outside the repository.

### Advisory Integration

External AI review should be treated as a structured input stream, not as a
parallel source of authority. Advisory comments should be filtered through:

- claim safety: avoid stronger claims than evidence supports;
- product fit: decide whether the idea belongs in Core or Labs;
- testability: define the diagnostic or fixture needed;
- maintenance cost: decide whether the complexity earns its place.

### Candidate Graduation Ladder

New DSP ideas must move through this ladder:

```text
idea
  -> research note
  -> diagnostic script or temporary fixture
  -> offline analysis
  -> real JDSP test
  -> listening candidate
  -> qualification
  -> accepted baseline
```

Skipping the ladder is allowed only for documentation-only cleanup or tooling
changes that do not change DSP behavior.

### Claim Discipline

The repository must not claim capabilities that have not been proven by the
current evidence set. Avoid phrases such as:

- "true binaural";
- "HRTF-accurate";
- "mastering-grade";
- "true peak";
- "certified loudness";
- "transparent" unless the scope is measured and stated.

Use narrower language such as "psychoacoustic stereo enhancement",
"measured proxy", "host-path capture", "accepted listening baseline", or
"qualified under the documented JDSP host settings".

## Technical Domain Context

### Core DSP And EEL2

Axiom is a JamesDSP / JDSP4Linux EEL2 Liveprog processor. All agents must obey
the strict EEL2 and JDSP constraints in `AGENTS.md` before editing DSP code.

Relevant domains:

- IIR biquad filtering and difference equations;
- mid-side stereo processing;
- additive harmonic generation;
- level-dependent high-frequency excitation;
- STFT analysis and reconstruction;
- gain staging and host-limiter interaction;
- phase and mono-compatibility behavior.

### JDSP And Host Integration

Axiom does not own every audio stage. The host owns terminal limiting and
optional crossfeed. Qualification uses the documented JDSP host baseline:

- master limiter enabled;
- `-1.00 dB` threshold;
- `60 ms` release;
- `0 dB` postgain;
- crossfeed disabled during comparison.

Host settings must be documented whenever they affect a result.

### Plugin And Product Architecture

The long-term system may include multiple profiles or paths, but only Axiom
Core is accepted today. Profile concepts such as Reference, Immersive, Night,
or Studio Path must remain research or Labs work until they have specific
tests, listening goals, and maintenance ownership.

### Knowledge And Research

Knowledge work may include bibliographies, summaries, and research questions.
Do not commit copyrighted source books, long copied excerpts, private library
paths, or unlicensed material. Axiom Knowledge should capture citations,
concept summaries, and how a source may affect test design.
