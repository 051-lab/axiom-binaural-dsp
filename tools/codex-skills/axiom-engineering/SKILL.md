---
name: axiom-engineering
description: Use when working inside the Axiom-DSP repository on audio-DSP architecture, EEL2/JDSP safety, Codex/Pi orchestration, candidate planning, qualification review, Knowledge notes, release gates, or Axiom workflow documentation.
---

# Axiom Engineering

Use this skill for Axiom-DSP repository work. Codex is the orchestration layer:
it reads the repo state, keeps docs aligned, plans changes, runs safe local
checks, and delegates controlled execution to the Pi harness when real-JDSP or
candidate state is involved.

## Start Here

1. Read `docs/system-status.md`.
2. Read `AGENTS.md` before any EEL, JDSP, or host-policy decision.
3. Classify the work: Core, Labs, Knowledge, Qualification, tooling, docs, or
   local-only.
4. Use `python3 tools/axiom-codex/axiom_codex.py status-summary` for a compact
   repo state check when available.
5. Use `python3 tools/axiom-codex/axiom_codex.py guard-check` before preparing
   publication scope or when changed paths may include EEL, policy, private
   artifacts, manifests, credentials, or private paths.
6. Use Pi for real-JDSP measurements, candidate creation, candidate
   qualification, publication, and merge workflows.

## Hard Boundaries

- Do not edit accepted or historical EEL files in place.
- Do not create sound-changing candidates without a scoped hypothesis and
  listening target.
- Do not run competing real-JDSP captures.
- Do not treat external LLM feedback, research, or metrics as listening
  acceptance.
- Do not commit private source audio, captures, manifests, credentials, private
  paths, or copyrighted book contents.
- Publication, merge, accepted-baseline changes, and stronger public claims
  require explicit user approval.

## References

Load only the reference needed for the current task:

- `references/role-registry.md`: specialist roles and expected outputs.
- `references/handoff-protocol.md`: when Codex should delegate to Pi or stop.
- `references/approval-matrix.md`: user approval gates and stop conditions.
- `references/knowledge-policy.md`: repo-safe Knowledge and local-only source
  index rules.
- `references/helper-cli.md`: Axiom Codex helper command behavior.

## Default Workflow

1. Inspect state and current diff.
2. Name the current work area and forbidden scope.
3. Choose the narrowest tool path:
   - docs/tooling review: Codex can handle directly;
   - real-JDSP or candidate workflow: delegate to Pi/harness;
   - research context: use Knowledge notes and cite limits.
4. Validate based on risk.
5. Update docs and session logs when state changes.
6. Ask for explicit approval before publication, merge, accepted-baseline
   promotion, or any irreversible external action.
