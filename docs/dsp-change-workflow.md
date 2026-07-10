# Axiom DSP Change Workflow

This is the active workflow for creating or modifying Axiom audio-DSP behavior.

## 1. Start With Sound

The user describes the desired sound in ordinary language. Useful input:

- what should improve;
- what feels wrong now;
- example material or genre;
- playback device and route;
- fatigue, punch, bass, clarity, width, image, or loudness notes.

The agent must restate the sound goal plainly before proposing code work.

## 2. Convert Sound Into One Hypothesis

Each DSP step should test one main idea.

Good:

```text
Reduce global width to see if the image becomes more coherent.
```

Bad:

```text
Import an entire experimental script with width, bass, modulation, smoothing,
STFT, and claim-language changes at once.
```

## 3. Use Labs Before Candidates

Labs fixtures are allowed under `src/labs/`. They are research artifacts, not
accepted behavior.

Every Labs step needs:

- hypothesis;
- changed variable;
- forbidden scope;
- static validation;
- listening question;
- keep/reject/material-dependent/no-difference decision.

## 4. Explain Listening In Plain Language

Every listening pass should answer:

- which file is A;
- which file is B;
- what music/material to use;
- what to listen for;
- what result means keep, reject, or retest.

Avoid vague instructions like "test it and see." The user should know exactly
what audible behavior matters.

## 5. Promote Only Through Gates

A Labs result can lead to candidate-readiness planning, not direct promotion.

Candidate creation requires:

- explicit user approval;
- a new EEL file using current naming policy;
- accepted baseline preserved;
- static validation;
- qualification scope;
- listening plan.

Accepted-baseline promotion requires the full release gate in
`docs/release-gates.md`.

## Current Candidate Boundary

`Axiom Clean R012` is not created. The current plan-only gate is:

```text
docs/axiom-clean-r012-candidate-readiness-plan-2026-07-08.md
```

Do not create `src/axiom_clean_r012.eel` without explicit approval.
