# Axiom

Axiom is an audio-DSP project for JamesDSP. Its purpose is simple: turn human
descriptions of better sound into safe, testable EEL2 DSP improvements.

The current accepted baseline is:

```text
Axiom Clean R011
src/axiom_binaural_dsp_v4.1.4.11.eel
```

There is no active official candidate. `Axiom Clean R012` is only a future
candidate-readiness plan until explicitly approved.

## How To Ask Axiom For DSP Work

Describe the sound in plain language:

- what sounds wrong;
- what should sound better;
- what music or material exposes it;
- what output device or route you are using;
- what you are hearing after a test.

The system should translate that into:

1. a clear sound goal;
2. a DSP hypothesis;
3. a narrow Labs fixture or test plan;
4. listening instructions in ordinary language;
5. a keep, reject, retest, or candidate-readiness decision.

You should not need to understand every tool, document, or agent role to guide
the project.

## Active Workflow

Use `docs/dsp-change-workflow.md` as the current workflow for sound-changing
work.

The short version:

```text
human sound description
  -> Axiom interprets the goal
  -> one narrow DSP hypothesis
  -> Labs fixture or analysis
  -> listening/measurement
  -> keep, reject, or candidate-readiness
```

No accepted or historical EEL file is edited in place.

## Current Active Areas

- Core DSP source: `src/`
- Labs fixtures: `src/labs/`
- Knowledge notes: `docs/knowledge/`
- Main docs map: `docs/README.md`
- Current status: `docs/system-status.md`
- Release gates: `docs/release-gates.md`
- Agent/orchestration helpers: `tools/axiom-codex/`

Completed reviews, old planning docs, and previous Labs step records live under
`docs/archive/`.

## Agent Rule

Agents should communicate in plain language first. Technical detail belongs
after the decision, not before it. If a change needs specialist work, the agent
may use skills, subagents, or helper tools internally, but the user-facing
workflow should stay understandable.
