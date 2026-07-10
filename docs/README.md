# Axiom Documentation Index

This is the active documentation map for Axiom Binaural DSP.

Start here when you need the current system state or the active workflow. Older
reviews, completed Labs notes, and previous planning records are in
`archive/`.

## Start Here

| File | Purpose |
| --- | --- |
| [../AXIOM.md](../AXIOM.md) | Plain-language front door for the Axiom system. |
| [system-status.md](system-status.md) | Current baseline, active candidate state, and safe next step. |
| [dsp-change-workflow.md](dsp-change-workflow.md) | Current sound-description to DSP-change workflow. |
| [architecture.md](architecture.md) | Current DSP signal chain and host ownership model. |
| [current-state.md](current-state.md) | Accepted baseline, policy anchor, host settings, and local/private boundary. |
| [release-gates.md](release-gates.md) | Documentation, Labs, candidate, listening, and accepted-baseline gates. |
| [task-backlog.md](task-backlog.md) | Machine-readable task-state source and completed roadmap history. |
| [axiom-clean-r012-candidate-readiness-plan-2026-07-08.md](axiom-clean-r012-candidate-readiness-plan-2026-07-08.md) | Plan-only gate for a possible future `Axiom Clean R012` candidate. |

## Active Work Areas

| Area | Files |
| --- | --- |
| Core DSP | `src/`, [architecture.md](architecture.md), [versioning-and-naming.md](versioning-and-naming.md) |
| Labs | `src/labs/`, [labs-policy.md](labs-policy.md), [dsp-change-workflow.md](dsp-change-workflow.md) |
| Knowledge | [knowledge/README.md](knowledge/README.md), `docs/knowledge/` |
| Qualification | [candidate-readiness.md](candidate-readiness.md), [listening-protocol.md](listening-protocol.md), [listening-records.md](listening-records.md) |
| Agentic tooling | [codex-operating-guide.md](codex-operating-guide.md), [pi-runbooks.md](pi-runbooks.md), [tool-inventory.md](tool-inventory.md) |
| Archive | [archive/README.md](archive/README.md), `docs/archive/` |

## Current Evidence And Gates

| File | Purpose |
| --- | --- |
| [qualification-v4.1.4.11.md](qualification-v4.1.4.11.md) | Accepted `Axiom Clean R011 / v4.1.4.11` qualification record. |
| [sub-harmonics-follow-up-v4.1.4.11.md](sub-harmonics-follow-up-v4.1.4.11.md) | Closed `.11` Sub Harmonics follow-up and watch-item result. |
| [perceptual-metrics.md](perceptual-metrics.md) | Offline loudness, true-peak proxy, transient, M/S, and ERB-like metric scope. |
| [corpus-material.md](corpus-material.md) | Material-class taxonomy and local/private corpus boundary. |
| [device-matrix.md](device-matrix.md) | Device and route validation matrix. |

## Helper Commands

```bash
python3 tools/axiom-codex/axiom_codex.py status-summary
python3 tools/axiom-codex/axiom_codex.py task-state
python3 tools/axiom-codex/axiom_codex.py next-action
python3 tools/axiom-codex/axiom_codex.py guard-check
python3 tools/axiom-codex/axiom_codex.py ready-check
```

Use `scripts/validate_axiom_static.sh` for EEL safety checks.

## Local-Only Material

Private PDFs, audio, manifests, captures, and listening records stay local.
Repo-safe summaries and concept notes live under `docs/knowledge/`.

`docs/knowledge/pdfs/` and `docs/knowledge/source-index.local.json` are local
working locations and should not publish source material.
