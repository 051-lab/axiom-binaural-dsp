# Axiom System Status

Last updated: 2026-06-21

This is the quick-start dashboard for Codex, Pi sessions, and future agents.
Read this before choosing new work. It summarizes the current accepted line,
active investigations, operating-system state, and the next recommended
tasks.

## Accepted Baseline

| Item | Value |
| --- | --- |
| Human-facing label | `Axiom Clean R011` |
| Accepted version | `v4.1.4.11` |
| Accepted script | `src/axiom_binaural_dsp_v4.1.4.11.eel` |
| SHA-256 | `ad7dd7b33f2e62ff03ae08d7101c7ac333d707baef26b952806990ad979b0b0e` |
| Qualification record | `qualification-v4.1.4.11.md` |
| Policy anchor | `../tools/axiom-team/policy.json` |

`v4.1.4.11` is the current accepted listening baseline. It keeps the `.10`
restrained low-mid width baseline and changes only the elevated-bass reserve
slope above the default `+4 dB` Sub Harmonics setting from `0.750 dB/dB` to
`0.500 dB/dB`.

Future Axiom Clean EEL iterations should use the `Axiom Clean R012+` release
label and matching `src/axiom_clean_r012.eel` style filenames. Historical
`v4.1.4.x` files remain evidence anchors; do not continue that sequence for
new sound-changing candidates. See `versioning-and-naming.md`.

## Active Candidate

None.

No sound-changing `Axiom Clean R012` or v5 candidate should be created until
the candidate readiness gate passes and a new scoped hypothesis has measurement
support.

## Host Baseline

| Host Setting | Accepted Qualification Value |
| --- | --- |
| JDSP master processing | enabled |
| Master limiter threshold | `-1.00 dB` |
| Master limiter release | `60 ms` |
| Master postgain | `0 dB` |
| Crossfeed during qualification | disabled |

JamesDSP crossfeed may be enabled manually for headphone listening, but it is
not part of the measured Axiom comparison baseline.

## Current Open Investigation

| Run | Status | Meaning |
| --- | --- | --- |
| `20260603T004349-post-acceptance-v4-1-4-1-0d309b` | `closed_watch_item` | `.11` elevated Sub Harmonics follow-up closed after blinded listening; no candidate justified. |

Known result:

- accepted-setting dense-material stress: `pass_with_investigation`;
- Sub Harmonics map: recorded `fail` because the old one-hour wrapper timeout
  stopped the full sweep before the aggregate report was written;
- completed partial evidence showed normal material stayed unclipped through
  the completed `+4`, `+6`, `+8`, and partial `+10 dB` cases;
- a 2026-06-08 route reset restored the JDSP capture path and the corrected
  targeted map completed at `+4`, `+10`, and `+12 dB`;
- the corrected map still recorded `fail`, but not because of normal-material
  clipping: normal material stayed unclipped through `+12 dB`, while the gate
  failed on a default `+4 dB` dense-electronic repeatability qualification and
  investigation findings for terminal-pressure observations plus elevated
  RMS retreat;
- a 2026-06-09 confirmatory rerun with the same command repeated the same
  conclusion: no normal-material clipping through `+12 dB`, `fail` caused by
  the default dense-electronic repeatability qualification, and elevated
  RMS-retreat observations at `+10 dB` and `+12 dB`;
- the summarized evidence record is
  `sub-harmonics-follow-up-v4.1.4.11.md`;
- the interpretation record is
  `sub-harmonics-interpretation-v4.1.4.11.md`: no `Axiom Clean R012`
  candidate is justified yet; the next step is focused listening around
  elevated-setting punch, practical loudness, bass clarity, limiter pumping,
  and fatigue;
- the listening target is
  `sub-harmonics-listening-target-v4.1.4.11.md`, with a local-copy JSON
  template at `templates/sub-harmonics-listening-record-v4.1.4.11.json`;
- filtered local A/B packages can now be generated from completed Sub Harmonics
  map render folders, excluding flawed stress material from normal-material
  listening checks;
- 2026-06-21 blinded listening split `+4` versus `+10` 2-2 by material and
  preferred `+4` over `+12` in all four material classes;
- combined preference was `+4` in six of eight comparisons; earlier listening
  retained clarity and clean kick impact at elevated settings but noted reduced
  aliveness, quicker fatigue, and slight pumping;
- outcome: close as a watch item, keep `Axiom Clean R011` accepted, and do not
  create `Axiom Clean R012`.

Historical follow-up command, only if new evidence later justifies a rerun:

```bash
node tools/axiom-team/bin/axiom-team.mjs map-sub-gain \
  20260603T004349-post-acceptance-v4-1-4-1-0d309b \
  --slider-db 4 --slider-db 10 --slider-db 12 \
  --label-regex 'electronic|hip hop|bass|flawed'
```

Run this only when the JDSP capture route is available and no other real-host
measurement is active. Targeted maps must include the accepted `+4 dB` default
so elevated settings can be compared to the baseline control point.

## Operating-System Foundation

The AI development ecosystem has been converted from the local
`axiom-idea.html` brainstorm into repository workflow. The foundation merged in
PR #10 as commit `c498688`.

| Layer | Status | Document |
| --- | --- | --- |
| Role and flow spec | merged | `ai-development-ecosystem.md` |
| Codex operating guide | merged | `codex-operating-guide.md` |
| Product/profile roadmap | merged | `axiom-system-roadmap.md` |
| Ordered implementation plan | complete | `axiom-operating-system-implementation-plan.md` |
| Labs policy | merged | `labs-policy.md` |
| Knowledge structure | initial structure merged | `knowledge/README.md` |
| Labs/review templates | merged | `templates/` |
| GitHub issue forms | merged | `.github/ISSUE_TEMPLATE/` |
| Pi runbooks | merged | `pi-runbooks.md` |
| Session work log PDF workflow | merged | `session-work-log.md`, `session-work-log.pdf` |
| Agentic engineering blueprint | local v1 source-ready | `axiom-agentic-engineering-blueprint.md` |
| Axiom Codex skill | local v1 installed | `~/.codex/skills/axiom-engineering` from `../tools/codex-skills/axiom-engineering/` |
| Axiom Codex helper CLI | contract-hardened v3 | `../tools/axiom-codex/axiom_codex.py` |
| Agentic contract audit | complete | `agentic-audit`; command, profile, approval, and skill-eval contracts |
| Multi-role review records | complete | `agent-review --json`; validated draft findings schema |
| Maintenance-aware planning | complete | `next-action --include-maintenance`; explicit opt-in for initial hardening |
| Foundational Agentic tasks | complete | `AX-TASK-018` through `AX-TASK-021`; contracts and regressions pass |
| Airwindows Knowledge intake | local metadata workflow | `knowledge/airwindows-open-source-dsp.md`, `knowledge/concepts/airwindows-concept-taxonomy.md`, `airwindows-index` helper |
| Qualification evidence ingestion | initial implementation complete | `evidence-ingest` helper; local-only normalized bundles |
| Qualification evidence status | initial implementation complete | `evidence-status`; optional `status-summary --evidence` and `next-action --evidence` |
| Automatic evidence discovery | initial implementation complete | `evidence-catalog`; local-only default directory |

These docs and templates are workflow infrastructure. They do not change DSP
behavior. Larger product lanes such as Axiom Reference, Immersive, Night, and
Studio Path are defined but not built as official products.

## Native Windows Listening Host

The local Axiom JamesDSP Controller is implemented under the external
`JamesDSP4Windows_Decluttered/AxiomConsoleHarness` workspace. It provides a
native Windows WASAPI route from VB-CABLE through JamesDSP/Axiom to a physical
output. This is local tooling and does not alter the accepted Axiom EEL.

Completed host capabilities:

- portable package, ZIP archive, and Inno Setup installer/uninstaller;
- upgrade-safe Local AppData settings, profiles, runtime files, and diagnostics;
- named multi-profile management with a protected qualification baseline;
- persistent health telemetry, threshold warnings, and session summaries;
- stable-ID Windows default-route ownership and restoration;
- optional tray, sign-in startup, automatic processor start, and restore-on-exit;
- automated first-run, route, single-instance, crash-recovery, telemetry, and
  package smoke tests;
- unattended soak tooling with generated audio, mixed crash/parameter events,
  default-route restoration, and JSON/Markdown evidence;
- low-latency Axiom slider updates through `LiveProgSetVar`, avoiding EEL
  recompilation for normal control changes;
- DSP packet-deadline and full-buffer critical-stall telemetry;
- typed EEL variable writes that match NSEEL's `float` storage;
- differential config reloads that avoid reapplying the complete DSP graph for
  slider-only changes;
- High process priority, MMCSS `Pro Audio / Critical` scheduling, and a
  resilient `200 ms` buffer with approximately `40 ms` steady queued latency;
- soak evidence that separates audio-integrity failures from AC/battery
  environment changes;
- centralized `0.2.0` controller/installer version metadata;
- release preflight checks for stable AC power, High performance mode, disabled
  AC sleep/hibernate, pending reboot state, package/install hashes, route
  availability, and competing processes;
- an overnight wrapper that temporarily disables AC sleep and restores the
  exact preceding timeout in all exit paths;
- a certificate-aware Authenticode signing and verification tool that keeps
  private keys, passwords, and certificate thumbprints outside the repository.

The final 2026-06-20 package smoke suite passed. A stressed 12-minute portable
gate passed with 72,498 packets, 24/24 reloads, one crash recovery, zero drops,
zero starvation, zero deadline misses, and 27.64% maximum buffer use. A
15-minute loaded-desktop gate passed with 91,500 packets, 15/15 reloads, zero
losses, zero deadline misses, and 25.83% maximum buffer use.

The installed one-hour endurance run at
`%LOCALAPPDATA%\Axiom\SoakTests\20260620-042409` processed 361,987 packets and
passed every audio-integrity gate: zero dropped frames, zero render starvation,
12/12 reloads, a 0.3036% deadline-miss rate, and 42.67% maximum buffer use.
Windows changed from battery to AC during the run, producing 19 non-lossy
capture discontinuity notifications; the historical report therefore recorded
`fail` under the older combined gate. Future reports classify that condition as
an environment warning instead of a processor failure.

The `0.2.0` package, installer, and installed application pass the full smoke
suite. A short end-to-end overnight-wrapper simulation passed and confirmed
that the preceding 10-minute AC sleep timeout was restored after cleanup.

The 2026-06-20 manual recovery qualification passed on the VB-CABLE to USB-C
EarPods route. Removing the EarPods stopped processing and placed the controller
in route-recovery waiting while preserving the stable endpoint ID. Reconnecting
the same endpoint restored VB-CABLE route ownership and restarted processing
automatically. A Modern Standby cycle preserved the route and resumed with zero
drops, starvation, conversion errors, render errors, deadline misses, or
critical stalls. Local evidence is retained under
`%LOCALAPPDATA%\Axiom\ManualRecovery\20260620-074834`.

The Agentic Layer can now ingest the soak and manual-recovery JSON schemas into
one source-hashed evidence bundle. It preserves the historical soak report's
raw `fail` while classifying its audio result as
`pass_with_environment_warning`, and it classifies the manual recovery record
as `pass`. The normalized bundle remains local, hides private paths by default,
and does not constitute listening acceptance or release promotion. The first
bundle is retained at
`%LOCALAPPDATA%\Axiom\AgenticEvidence\20260620-windows-host-qualification.json`.

Remaining productization work is the full power-stable overnight installed
gate and provisioning a trusted code-signing certificate before external
distribution. Windows SDK `signtool.exe` is installed, but no usable
code-signing certificate is currently present; all four release artifacts
correctly verify as unsigned.

## Latest Assessment

The current full-system readiness review is
`axiom-full-system-review-2026-06-08.md`.

Summary:

- `v4.1.4.11` remains the accepted Core baseline.
- Full Python tests passed with 170 tests.
- Pi doctor, strict corpus metadata, candidate readiness, Codex helper
  readiness, guard checks, skill evals, and Knowledge source audit passed.
- Candidate readiness is `READY`, but no `Axiom Clean R012` candidate is
  justified yet; the completed `.11` Sub Harmonics follow-up produced a
  listening target, not an EEL edit boundary.
- The 2026-06-08 corrected targeted rerun and 2026-06-09 confirmatory rerun
  both produced full reports: no normal-material clipping through `+12 dB`,
  but failed gates due to default dense-electronic repeatability qualification
  plus terminal-pressure and elevated RMS-retreat investigation findings.
- Listening records now require structured spatial fields for center image,
  lateral spread, localization blur, depth impression, bass-image coupling, and
  route context.
- Airwindows is available as an external open-source Knowledge source through
  repo-safe notes and local-only metadata indexing; it can inform Labs
  questions but not justify candidate creation by itself.
- PR #12 merged the Codex/Knowledge hardening batch after explicit approval.
- Axiom Knowledge has six local-source-backed seed notes and a passing source
  audit.

## Current Best Next Actions

1. Continue Agentic Layer hardening with
   `next-action --include-maintenance --no-evidence` when intentionally working
   on initial Agentic tasks.
2. Keep the completed `.11` Sub Harmonics result as a watch item; do not draft
   `Axiom Clean R012` without a new repeatable normal-material problem.
3. Use Knowledge seed notes to support specific test-design questions, not to
   justify DSP changes by themselves.

## Refresh Commands

Use these commands when updating this dashboard:

```bash
git status -sb
python3 tools/axiom-codex/axiom_codex.py agentic-audit
node tools/axiom-team/bin/axiom-team.mjs doctor
node tools/axiom-team/bin/axiom-team.mjs status
scripts/evaluate_axiom_candidate_readiness.py \
  --json /tmp/axiom-candidate-readiness.json \
  --markdown /tmp/axiom-candidate-readiness.md
```

Generated reports and captures remain local unless a sanitized summary is
explicitly added to `docs/`.
