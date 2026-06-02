# Axiom Documentation Index

This directory contains public engineering documentation for Axiom Binaural
DSP. Use this file as the map before opening individual investigation records.

## Start Here

| File | Purpose |
| --- | --- |
| [current-state.md](current-state.md) | Accepted baseline, policy anchor, host settings, and local/private state boundary. |
| [architecture.md](architecture.md) | Current DSP signal chain, processing math, and host ownership model. |
| [axiom-roadmap.md](axiom-roadmap.md) | Current development roadmap and candidate discipline. |
| [tool-inventory.md](tool-inventory.md) | What each script does, whether it touches JDSP, and where outputs belong. |
| [engineering-harness.md](engineering-harness.md) | Controlled Pi workflow, gates, local-state policy, and release commands. |

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
| [corpus-material.md](corpus-material.md) | Material-class taxonomy, manifest rules, and local/private corpus boundary. |
| [listening-records.md](listening-records.md) | Structured human listening evidence format. |
| [ab-listening-packages.md](ab-listening-packages.md) | Local level-matched A/B listening package workflow. |
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
