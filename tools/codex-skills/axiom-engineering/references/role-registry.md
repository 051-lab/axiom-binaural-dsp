# Axiom Role Registry

Codex may consult these roles conceptually during planning and review. Pi has
tracked role prompts under `tools/axiom-team/roles/`; those prompts remain the
execution-layer source for specialist Pi consultations.

Codex-specific profile specs live under `tools/axiom-codex/agent_profiles/`.
Use `python3 tools/axiom-codex/axiom_codex.py agent-profiles` to list them or
`--role <name>` to print one profile.

| Role | Owner Layer | Purpose | Required Output |
| --- | --- | --- | --- |
| Coordinator | Codex/Pi | Own run flow, delegation, and unresolved decisions. | Work plan, role assignments, blocked decisions. |
| DSP Architecture Lead | Codex/Pi | Assess signal-chain intent and falsifiable hypotheses. | Affected stage, benefit, risk, listening target. |
| EEL Engineer | Codex/Pi | Enforce EEL2/JDSP implementation constraints. | Safety findings, minimal edit boundary, static checks. |
| Measurement Engineer | Codex/Pi | Decide whether tests can support the conclusion. | Measurement plan, uncertainty, pass/fail meaning. |
| Qualification Lead | Codex/Pi | Decide whether evidence is strong enough for listening. | Gate status, missing evidence, listening eligibility. |
| Safety Auditor | Codex/Pi | Find regressions, policy violations, and unsafe scope. | Findings-first review and residual risk. |
| Tooling Engineer | Codex/Pi | Maintain scripts, validators, reports, and repeatability. | Tool change scope and tests. |
| Signal Researcher | Codex/Pi | Connect research, prior evidence, and algorithm options. | Research summary and Axiom-specific questions. |
| Release Steward | Codex/Pi | Check publication, PR, docs, policy hash, and merge readiness. | Release checklist and blockers. |

## Codex Multi-Role Review Format

Use this compact review shape:

```text
Topic:
Scope:
Forbidden scope:

Role findings:
- DSP Architecture Lead:
- EEL Engineer:
- Measurement Engineer:
- Safety Auditor:
- Release Steward:

Decision:
- continue / stop / delegate-to-Pi / needs-user-approval

Evidence still needed:
-
```
