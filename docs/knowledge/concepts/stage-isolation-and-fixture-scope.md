# Stage Isolation And Fixture Scope

Type: concept note
Source IDs:

- `dafx-digital-audio-effects`
- `designing-audio-effect-plug-ins-in-cpp`
- `the-audio-programming-book`

## Purpose

This note describes how Axiom should turn broad DSP ideas into narrow,
testable changes. It is intended for Codex/Pi planning before any EEL candidate
exists.

## Axiom Test-Design Use

Before creating a sound-changing candidate, identify:

- the exact stage under test;
- the smallest temporary fixture that changes one variable;
- the expected measurable result;
- the expected listening target;
- the forbidden scope;
- the route or host settings that must remain fixed.

For Axiom, useful fixture questions include:

- bass branch only, reserve only, or their interaction?
- low-mid width, high-width, or global width?
- exciter sensitivity, threshold, or output balance?
- STFT stage behavior or non-STFT chain behavior?
- host limiter behavior or script behavior?

## Axiom Questions

- Can the issue be measured with a temporary fixture before a new `.eel`
  version exists?
- Is the proposed change actually one variable, or a bundle of changes?
- Does the measurement require real JDSP because host limiter or Liveprog
  behavior is involved?
- Can the evidence support a listening target without overclaiming?

## Boundary

Stage isolation is a planning discipline. It does not make a candidate safe by
itself; EEL2/JDSP static rules, real-host qualification, and listening gates
still apply.
