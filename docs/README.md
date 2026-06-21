# Axiom Documentation Index

This directory contains public engineering documentation for Axiom Binaural
DSP. Use this file as the map before opening individual investigation records.

## Start Here

| File | Purpose |
| --- | --- |
| [system-status.md](system-status.md) | Quick dashboard: accepted baseline, active candidate, open investigations, and next work. |
| [session-work-log.md](session-work-log.md) | Source log for session work summaries; generates `session-work-log.pdf`. |
| [current-state.md](current-state.md) | Accepted baseline, policy anchor, host settings, and local/private state boundary. |
| [architecture.md](architecture.md) | Current DSP signal chain, processing math, and host ownership model. |
| [versioning-and-naming.md](versioning-and-naming.md) | Future EEL naming policy: preserve legacy `v4.1.4.x` evidence IDs while using `Axiom Clean R012+` release labels going forward. |
| [axiom-roadmap.md](axiom-roadmap.md) | Current development roadmap and candidate discipline. |
| [axiom-system-roadmap.md](axiom-system-roadmap.md) | Product/profile system roadmap for Core, Labs, Knowledge, and Qualification. |
| [axiom-full-system-review-2026-06-08.md](axiom-full-system-review-2026-06-08.md) | Current full-system readiness review across Core DSP, Qualification, Pi/JDSP workflow, Codex tooling, Knowledge, documentation, and release posture. |
| [axiom-full-system-review-2026-06-08.html](axiom-full-system-review-2026-06-08.html) | Rendered HTML copy of the current full-system readiness review. |
| [axiom-layer-progression-2026-06-10.md](axiom-layer-progression-2026-06-10.md) | Progression tracker for each major Axiom system layer, including Core DSP, Qualification, Codex orchestration, Agentic Layer, Knowledge, and release gates. |
| [axiom-change-batch-reconciliation-2026-06-20.md](axiom-change-batch-reconciliation-2026-06-20.md) | Findings-first review of the current uncommitted naming, Agentic, Knowledge, and Player work, including blockers and proposed commit groups. |
| [axiom-full-state-assessment-2026-06-04.md](axiom-full-state-assessment-2026-06-04.md) | Previous full-system assessment across Core DSP, Qualification, Agentic tooling, Knowledge, and repository housekeeping. |
| [profile-matrix.md](profile-matrix.md) | Operational matrix for profile status, ownership, allowed changes, and tests. |
| [axiom-operating-system-implementation-plan.md](axiom-operating-system-implementation-plan.md) | Ordered implementation plan for making the AI development ecosystem operational. |
| [axiom-agentic-engineering-blueprint.md](axiom-agentic-engineering-blueprint.md) | Living blueprint for native Axiom agents, Codex/Pi handoffs, knowledge use, and approval gates. |
| [ai-development-ecosystem.md](ai-development-ecosystem.md) | Codex, Pi, user, and advisory LLM operating model extracted from the ecosystem vision. |
| [codex-operating-guide.md](codex-operating-guide.md) | Practical Codex responsibilities, prohibitions, branch discipline, and review workflow. |
| [pi-runbooks.md](pi-runbooks.md) | Repeatable terminal missions for Pi/Codex sessions. |
| [labs-policy.md](labs-policy.md) | Branch, experiment, artifact, and promotion rules for Axiom Labs. |
| [task-backlog.md](task-backlog.md) | Lightweight issue/task breakdown for the Axiom operating framework. |
| [tool-inventory.md](tool-inventory.md) | What each script does, whether it touches JDSP, and where outputs belong. |
| [engineering-harness.md](engineering-harness.md) | Controlled Pi workflow, gates, local-state policy, and release commands. |

## Operating Templates

| File | Purpose |
| --- | --- |
| [knowledge/README.md](knowledge/README.md) | Knowledge bibliography and research-note rules. |
| [knowledge/airwindows-open-source-dsp.md](knowledge/airwindows-open-source-dsp.md) | Repo-safe Airwindows provenance and clean-room concept boundary. |
| [knowledge/concepts/airwindows-concept-taxonomy.md](knowledge/concepts/airwindows-concept-taxonomy.md) | Curated Airwindows effect-family taxonomy for Labs and test-design questions. |
| [templates/labs-experiment.md](templates/labs-experiment.md) | Markdown template for Labs experiment notes. |
| [templates/external-review-triage.md](templates/external-review-triage.md) | Markdown template for advisory LLM or human review triage. |
| [templates/sub-harmonics-listening-record-v4.1.4.11.json](templates/sub-harmonics-listening-record-v4.1.4.11.json) | Local-copy template for the accepted-`.11` Sub Harmonics listening target. |

## Session Work Log

`docs/session-work-log.md` is the editable source. Refresh both PDF copies with:

```bash
python3 tools/generate_session_work_log_pdf.py
```

The generator writes `docs/session-work-log.pdf` and
`C:\Users\soloa\Documents\Axiom-DSP-Session-Work-Log.pdf`.

## Agentic Engineering Blueprint

`docs/axiom-agentic-engineering-blueprint.md` is the editable source for the
future native Axiom agentic-system architecture. Refresh both PDF copies with:

```bash
python3 tools/generate_agentic_blueprint_pdf.py
```

The generator writes `docs/axiom-agentic-engineering-blueprint.pdf` and
`C:\Users\soloa\Documents\Axiom-DSP-Agentic-Engineering-Blueprint.pdf`.

The repo-tracked Axiom Codex skill source lives at
`tools/codex-skills/axiom-engineering/`. Preview the local install with:

```bash
python3 tools/install_axiom_codex_skill.py --dry-run
```

Use the safe Codex helper CLI for orchestration support:

```bash
python3 tools/axiom-codex/axiom_codex.py status-summary
python3 tools/axiom-codex/axiom_codex.py ready-check
python3 tools/axiom-codex/axiom_codex.py agentic-audit
python3 tools/axiom-codex/axiom_codex.py agent-review --topic "review topic"
python3 tools/axiom-codex/axiom_codex.py agent-review --topic "review topic" --json
python3 tools/axiom-codex/axiom_codex.py knowledge-query "search terms"
```

## Accepted Baseline

| File | Purpose |
| --- | --- |
| [qualification-v4.1.4.11.md](qualification-v4.1.4.11.md) | Accepted `v4.1.4.11` baseline qualification and listening acceptance. |
| [qualification-v4.1.4.10.md](qualification-v4.1.4.10.md) | Previous accepted `.10` restrained low-mid width record. |
| [qualification-v4.1.4.9.md](qualification-v4.1.4.9.md) | Previous `.9` reduced bass-reserve record. |
| [qualification-v4.1.4.8.md](qualification-v4.1.4.8.md) | Previous `.8` bass-aware headroom record. |

## Evidence Records

| File | Purpose |
| --- | --- |
| [architecture-decision-v4.1.4.10.md](architecture-decision-v4.1.4.10.md) | Decision record for the `.10` to `.11` promotion and v5 deferral. |
| [accepted-stress-v4.1.4.10.md](accepted-stress-v4.1.4.10.md) | Dense-material stress behavior that informed the `.11` reserve work. |
| [sub-harmonics-follow-up-v4.1.4.11.md](sub-harmonics-follow-up-v4.1.4.11.md) | Targeted post-acceptance `.11` Sub Harmonics follow-up and investigation result. |
| [sub-harmonics-interpretation-v4.1.4.11.md](sub-harmonics-interpretation-v4.1.4.11.md) | No-candidate-yet interpretation and listening target for the `.11` Sub Harmonics follow-up. |
| [sub-harmonics-listening-target-v4.1.4.11.md](sub-harmonics-listening-target-v4.1.4.11.md) | Focused accepted-`.11` listening target for `+4`, `+10`, and `+12 dB` Sub Harmonics. |
| [sub-harmonics-map-v4.1.4.10.md](sub-harmonics-map-v4.1.4.10.md) | Elevated Sub Harmonics control-range evidence. |
| [reserve-law-screen-v4.1.4.10.md](reserve-law-screen-v4.1.4.10.md) | Reserve-law screen and full-manifest `0.500 dB/dB` qualification behind `.11`. |
| [stage-observability-v4.1.4.10.md](stage-observability-v4.1.4.10.md) | Bass/reserve stage-tap evidence. |
| [exciter-probe-screen-v4.1.4.10.md](exciter-probe-screen-v4.1.4.10.md) | Low-level exciter probe evidence and no-candidate decision. |
| [exciter-sensitivity-screen-v4.1.4.10.md](exciter-sensitivity-screen-v4.1.4.10.md) | Registered-material exciter sensitivity screen and no-candidate decision. |
| [high-width-screen-v4.1.4.10.md](high-width-screen-v4.1.4.10.md) | High-frequency width screen and no-candidate decision. |
| [lowmid-width-screen-v4.1.4.9.md](lowmid-width-screen-v4.1.4.9.md) | Low-mid width evidence that produced `.10`. |
| [width-mono-audit-v4.1.4.9.md](width-mono-audit-v4.1.4.9.md) | Width and mono-compatibility audit. |
| [stft-audit-v4.1.4.9.md](stft-audit-v4.1.4.9.md) | STFT stage audit and no-candidate decision. |
| [external-review-assessment-v4.1.4.9.md](external-review-assessment-v4.1.4.9.md) | External critique triage and roadmap assessment. |

## Validation Workflows

| File | Purpose |
| --- | --- |
| [candidate-readiness.md](candidate-readiness.md) | Baseline hash, strict corpus, and strict device readiness gate. |
| [release-gates.md](release-gates.md) | Publication, candidate, listening, and accepted-baseline promotion gates. |
| [listening-protocol.md](listening-protocol.md) | Practical listening setup, material selection, comparison method, and decision rules. |
| [corpus-material.md](corpus-material.md) | Material-class taxonomy, manifest rules, and local/private corpus boundary. |
| [listening-records.md](listening-records.md) | Structured human listening evidence format. |
| [ab-listening-packages.md](ab-listening-packages.md) | Local level-matched A/B listening package workflow. |
| [axiom-player.md](axiom-player.md) | Local browser music player for Windows/WSL playback through JDSP4Linux, with embedded JamesDSP UI and EEL testing controls. |
| [wsl-jdsp-listening.md](wsl-jdsp-listening.md) | Local Windows/WSL route for informal playback through JDSP4Linux and the accepted Axiom Liveprog script. |
| [android-validation.md](android-validation.md) | RootlessJamesDSP package and phone-side validation checklist. |
| [device-matrix.md](device-matrix.md) | Device and route validation matrix. |
| [device-readiness-packages.md](device-readiness-packages.md) | Local route-checklist package workflow. |
| [perceptual-metrics.md](perceptual-metrics.md) | Offline loudness, true-peak proxy, transient, ERB-like, and M/S metric scope. |
| [stage-observability-plan.md](stage-observability-plan.md) | Diagnostic stage-tap fixture plan. |
| [bass-host-limiter-investigation-plan.md](bass-host-limiter-investigation-plan.md) | Bass reserve and JDSP limiter investigation plan. |

## Reference

| File | Purpose |
| --- | --- |
| [JDSP4Linux_Knowledge_Base.md](JDSP4Linux_Knowledge_Base.md) | EEL2, JDSP runtime, preset, and CLI reference. |
| [axiom-system-overview.html](axiom-system-overview.html) | Visual project/system map. |

## Local-Only Planning

`axiom-notes.html` is intentionally excluded from public git through local
repo excludes because it can contain private paths, listening notes, and working
conversation context. Keep it local unless it is explicitly sanitized first.
