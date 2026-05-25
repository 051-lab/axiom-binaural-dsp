---
name: axiom-engineering
description: Operates Axiom Binaural DSP candidate investigation, EEL safety validation, JDSP qualification, listening acceptance, and gated GitHub release workflows.
---

# Axiom Engineering

Read `AGENTS.md`, `docs/architecture.md`, and `docs/qualification-v4.1.4.8.md`
before proposing or assessing DSP behavior.

Use `/axiom-doctor` before a new workflow and `/axiom-audit-baseline` for the
initial harness acceptance run. Use `/axiom-investigate` before creating any
sound-changing candidate. Host qualification must run through the harness so
the serialized JDSP route lock and local material policy are enforced.

Do not publish captures, private manifests, local paths, or listening notes
that the user identifies as private.
