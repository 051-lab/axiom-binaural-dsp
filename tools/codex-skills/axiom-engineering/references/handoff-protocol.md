# Axiom Handoff Protocol

Codex is the orchestrator. Pi is the controlled execution layer. Keep this
boundary clear.

## Codex Handles Directly

- Documentation updates and reconciliation.
- Status summaries and local diff review.
- Non-mutating repo inspection.
- Safe helper CLI commands.
- Knowledge note creation and sanitization.
- PR preparation after approvals and gates are complete.

## Delegate To Pi Or Node Harness

Use `scripts/axiom_team.sh` or
`node tools/axiom-team/bin/axiom-team.mjs <command>` for:

- real-JDSP captures or route-sensitive work;
- candidate creation;
- candidate qualification;
- listening-decision recording;
- candidate commits inside harness worktrees;
- publication and merge flows after explicit approvals.

## Stop For User Approval

Stop before:

- creating a sound-changing listening candidate;
- accepting a candidate;
- publishing to GitHub;
- merging a PR;
- changing `tools/axiom-team/policy.json` accepted-baseline identity;
- adding claims stronger than current repository evidence.

## Default Decision Rule

If the task touches audio behavior, host route state, candidate state, or
accepted-baseline identity, Codex should not improvise. It should create a
scoped plan, identify the correct Pi runbook, and ask for the required approval
when the next step is gated.
