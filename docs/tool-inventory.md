# Axiom Tool Inventory

Last updated: 2026-06-09

This inventory maps the repository's operational tools so humans and agents can
choose the right command without guessing. It is descriptive, not an execution
order. Use `docs/current-state.md` for the accepted baseline and
`docs/axiom-roadmap.md` for roadmap priority. Use
`docs/bass-host-limiter-investigation-plan.md` before running reserve-law, Sub
Harmonics, or host-limiter sweeps for candidate decisions. Use
`docs/stage-observability-plan.md` before implementing diagnostic stage taps.

Generated WAV, JSON, Markdown reports, private manifests, local captures, and
temporary fixtures must remain outside git unless a document explicitly says
the artifact is safe to commit.

## Safety And Loading

| Tool | Purpose | Touches JDSP | Repo writes | Output policy |
| --- | --- | --- | --- | --- |
| `scripts/validate_axiom_static.sh` | Static EEL2/JDSP safety gate for reserved constants, forbidden APIs, STFT signatures, final output assignment, and version-specific invariants. Defaults to accepted `.11`. | No | No | Console only. |
| `scripts/hot_reload_liveprog.sh` | Load a selected EEL script into JDSP Liveprog, normalize host settings, update `axiom_current.eel`, save a preset, and restore the accepted limiter threshold if JDSP resets it during preset save. Defaults to accepted `.11`. | Yes | No | Updates JDSP config, preset files, and user Liveprog symlink outside repo. |
| `scripts/build_android_validation_package.py` | Build a local RootlessJamesDSP validation package with scripts, SHA-256 hashes, checklist, and listening template. | No | No | Package output belongs outside repo unless sanitized for release. |
| `scripts/build_axiom_ab_listening_package.py` | Build a local blinded A/B listening package with loudness-proxy gain recommendations from matched WAV folders; supports include/exclude filters for focused package selection. | No | No | Package output belongs outside repo because it may contain private captures. |
| `scripts/build_device_readiness_package.py` | Build a local route-by-route checklist package from the device matrix and accepted script hash. | No | No | Package output belongs outside repo because it may contain private device names. |
| `scripts/evaluate_axiom_candidate_readiness.py` | Combine accepted-baseline hash, strict corpus metadata, and strict device-matrix checks before another sound-changing candidate. | No | No | JSON/Markdown reports belong outside repo unless summarized. |
| `scripts/audit_windows_audio_endpoints.py` | Snapshot Windows audio endpoint status and the active default render endpoint from WSL, emit route-class hints, and optionally fail unless the default route matches speaker, wired/USB, or Bluetooth. | No | No | JSON/Markdown reports belong outside repo unless sanitized. |
| `scripts/qualify_windows_default_route.py` | Build a local evidence report for a Windows default-output route by requiring the route class, restarting the managed JDSP route, hot-reloading accepted `.11`, verifying host settings, and playing a probe for user confirmation. | Yes | No | Output directory belongs outside repo because it may contain private device names. |
| `scripts/axiom_team.sh` | Launch the isolated Pi engineering harness with Axiom-specific tools and policy. | Indirect | No | Harness state remains under local state roots. |
| `tools/install_axiom_codex_skill.py` | Preview or install the repo-tracked Axiom Codex skill into `~/.codex/skills/axiom-engineering`. | No | No | Local install destination is outside repo and requires explicit `--install`. |
| `tools/axiom-codex/axiom_codex.py` | Safe Codex-side orchestration helpers for status, local review snapshots, task-state validation, next-action planning, ready checks, command surface discovery, guard preflights, role profiles, multi-role review scaffolds, Knowledge search/source audits, Pi handoff briefs, and skill behavior eval fixtures. | No | No | Console output only unless report output flags are provided; private Knowledge paths are hidden by default; guard findings block unsafe publication scope but do not approve release. |

## Offline Analysis And Fixture Inputs

| Tool | Purpose | Touches JDSP | Repo writes | Output policy |
| --- | --- | --- | --- | --- |
| `scripts/analyze_axiom_response.py` | Offline coefficient/crossover response analysis for the Axiom filter structure. | No | No | Console/report output only. |
| `scripts/analyze_axiom_bass_path.py` | Offline audit of historical dry bass-path reconstruction and group-delay behavior. | No | No | Console/report output only. |
| `scripts/analyze_axiom_crossfeed.py` | Offline transfer analysis for the removed internal crossfeed path and host ownership comparison. | No | No | Console/report output only. |
| `scripts/analyze_axiom_subharmonics.py` | Characterize Sub Harmonics branch behavior across frequencies, slider values, and input levels. | No | No | Optional JSON/Markdown outside repo unless intentionally documenting summarized findings. |
| `scripts/generate_jdsp_stimuli.py` | Generate deterministic stereo probes for host capture tests. | No | No | WAV outputs belong in `/tmp` or local artifact folders. |
| `scripts/generate_axiom_program_corpus.py` | Generate deterministic program-like bass-heavy passages for repeatable engineering tests. | No | No | WAV outputs belong outside repo. |
| `scripts/analyze_jdsp_transfer.py` | Analyze stimulus-conditioned host-path transfer from an original WAV and processed capture. | No | No | JSON/Markdown reports outside repo unless summarized. |
| `scripts/analyze_audio_perceptual_metrics.py` | Report offline loudness proxy, true-peak proxy, transient, ERB-like band, and M/S metrics for a stereo WAV. | No | No | JSON/Markdown reports outside repo unless summarized. |
| `scripts/validate_axiom_material_manifest.py` | Validate local-material manifest compatibility plus material-class and failure-mode coverage metadata. | No | No | Full manifests stay local unless sanitized. |
| `scripts/validate_axiom_listening_record.py` | Validate structured human listening records for required version, device, host, slider, material, and observation fields. | No | No | Full records stay local unless sanitized. |
| `scripts/validate_axiom_device_matrix.py` | Validate local device/route coverage, qualification eligibility, setup checks, and crossfeed policy. Use `--strict-setup` before candidate readiness. | No | No | Full matrices stay local unless sanitized. |
| `scripts/compare_jdsp_captures.py` | Compare reference and candidate processed WAV captures for level, alignment, clipping, and difference metrics. | No | No | JSON/Markdown reports outside repo unless summarized. |
| `scripts/qualify_jdsp_repeatability.py` | Check repeated WAV captures for silence, clipping, alignment, metric spread, and correlation confidence. | No | No | JSON/Markdown reports outside repo unless summarized. |

## Real-JDSP Render And Baseline Measurement

| Tool | Purpose | Touches JDSP | Repo writes | Output policy |
| --- | --- | --- | --- | --- |
| `scripts/render_jdsp_host.py` | Render one input WAV through one EEL script using the real JDSP Liveprog path. | Yes | No | Processed WAV belongs outside repo. |
| `scripts/run_jdsp_ab_testbench.py` | Generate probes, render baseline/candidate through JDSP, and compare captures. | Yes | No | Output directory belongs outside repo. |
| `scripts/run_jdsp_wsl_qualification.py` | Managed WSL qualification route for baseline/candidate, elevated bass fixtures, and corpus checks. | Yes | No | Output directory and temporary fixtures stay outside repo. |
| `scripts/run_jdsp_program_corpus.py` | Render deterministic program-like corpus through baseline/candidate at default controls. | Yes | No | Output directory belongs outside repo. |
| `scripts/run_jdsp_local_material.py` | Render private manifest excerpts through baseline/candidate for local material checks. | Yes | No | Manifest, decoded excerpts, and reports stay outside repo. |
| `scripts/run_jdsp_limiter_sweep.py` | Measure accepted-baseline sensitivity to different JDSP limiter thresholds on registered material; supports an explicit reference threshold for safe comparisons when a looser threshold clips. | Yes | No | Output directory belongs outside repo. |
| `scripts/run_jdsp_accepted_stress.py` | Repeat accepted-baseline captures on dense registered material at accepted host settings; declared `flawed_source` clipping is retained as investigation evidence while normal-material clipping still fails. | Yes | No | Output directory belongs outside repo. |

## Pre-Candidate Screens And Stage Audits

| Tool | Purpose | Touches JDSP | Repo writes | Output policy |
| --- | --- | --- | --- | --- |
| `scripts/run_jdsp_sub_slider_map.py` | Map accepted baseline behavior across Sub Harmonics Gain settings on registered material. | Yes | No | Temporary fixtures/reports stay outside repo. |
| `scripts/run_jdsp_stage_observability.py` | Create same-render diagnostic tap fixtures for the accepted baseline, starting with bass/reserve path comparisons. | Yes | No | Temporary fixtures/reports stay outside repo. |
| `scripts/run_jdsp_reserve_law_screen.py` | Screen temporary elevated-bass reserve slopes before a candidate exists; defaults to the accepted baseline reserve law and two conditioning renders. | Yes | No | Temporary fixtures/reports stay outside repo. |
| `scripts/run_jdsp_reserve_range_qualification.py` | Range-qualify viable reserve slopes across elevated bass settings before candidate creation; defaults to two conditioning renders per measured set. | Yes | No | Temporary fixtures/reports stay outside repo. |
| `scripts/run_jdsp_stft_audit.py` | Create diagnostic STFT fixtures and measure pre-STFT versus processed paths in same-render captures. | Yes | No | Temporary fixtures/reports stay outside repo. |
| `scripts/run_jdsp_width_mono_audit.py` | Compare accepted width behavior against temporary unity-width fixtures using pure M/S probes. | Yes | No | Temporary fixtures/reports stay outside repo. |
| `scripts/run_jdsp_width_material_screen.py` | Compare accepted and unity-width behavior on registered material by band-specific S/M balance. | Yes | No | Temporary fixtures/reports stay outside repo. |
| `scripts/run_jdsp_lowmid_width_screen.py` | Screen restrained low-mid width fixtures before proposing a candidate. | Yes | No | Temporary fixtures/reports stay outside repo. |
| `scripts/run_jdsp_high_width_screen.py` | Screen restrained high-frequency width fixtures from the accepted baseline. | Yes | No | Temporary fixtures/reports stay outside repo. |
| `scripts/run_jdsp_exciter_sensitivity_screen.py` | Screen temporary exciter sensitivity fixtures from the accepted baseline. | Yes | No | Temporary fixtures/reports stay outside repo. |
| `scripts/run_jdsp_exciter_probe_screen.py` | Generate low-level exciter probes and screen accepted/reduced/bypassed sensitivity with activation and restraint checks through JDSP. | Yes | No | Generated probes, fixtures, and reports stay outside repo. |

## Candidate Qualification

| Tool | Purpose | Touches JDSP | Repo writes | Output policy |
| --- | --- | --- | --- | --- |
| `scripts/run_jdsp_lowmid_width_candidate_qualification.py` | Scoped `.9` versus `.10`-style low-mid width candidate qualification that allows intentional spatial change. | Yes | No | Output directory belongs outside repo; summarized findings may become docs. |

Generic candidate qualification is normally orchestrated through the Pi harness
instead of being run as a standalone script.

## Pi Harness Commands

Run the harness with `scripts/axiom_team.sh` or use
`node tools/axiom-team/bin/axiom-team.mjs <command>`.

| Command | Purpose | Touches JDSP |
| --- | --- | --- |
| `init` | Create local harness configuration. | No |
| `doctor` | Check repository, accepted baseline hash, route helper, tools, and registered material validity. | No |
| `corpus-status` | Report configured local-material manifest validity and corpus taxonomy coverage. | No |
| `status` / `show` | Inspect local run state and evidence records. | No |
| `audit-baseline` | Static/tooling audit of the accepted baseline without a candidate. | No |
| `investigate` | Create an investigation anchored to the accepted baseline. | No |
| `hypothesis` | Record a falsifiable hypothesis and listening target. | No |
| `measure-limiter` | Run accepted-baseline limiter threshold sweep. | Yes |
| `stress-accepted` | Repeat dense-material accepted-baseline captures. | Yes |
| `map-sub-gain` | Map accepted baseline across Sub Harmonics Gain settings. | Yes |
| `stage-observability` | Measure accepted-baseline bass/reserve diagnostic taps. | Yes |
| `screen-reserve-law` | Screen temporary reserve-law fixtures. | Yes |
| `qualify-reserve-range` | Range-qualify reserve-law survivors. | Yes |
| `audit-stft` | Run same-render STFT stage audit. | Yes |
| `audit-width-mono` | Run accepted width and mono-compatibility audit. | Yes |
| `screen-width-material` | Screen accepted spatial balance on registered material. | Yes |
| `screen-lowmid-width` | Screen restrained low-mid width fixtures. | Yes |
| `screen-high-width` | Screen restrained high-frequency width fixtures. | Yes |
| `screen-exciter` | Screen dynamic exciter sensitivity fixtures. | Yes |
| `screen-exciter-probes` | Screen generated low-level exciter activation probes. | Yes |
| `create-candidate` | Create an external candidate worktree and copied versioned EEL file. | No |
| `qualify` | Run unit/static gates and serialized real-JDSP candidate qualification. | Yes |
| `qualify-lowmid-candidate` | Run scoped low-mid width candidate qualification. | Yes |
| `record-listening` | Record explicit human accept/reject decision. | No |
| `commit` | Commit qualified candidate changes locally. | No |
| `publish` / `merge` | Push/open PR or merge after separate explicit approvals. | No direct JDSP |

## Selection Rules

- Use static and offline tools before real-JDSP capture when the question is
  syntax, topology, or coefficient behavior.
- Use real-JDSP tools when the question involves host limiter behavior,
  Liveprog reloads, routing, clipping, silence, material response, or accepted
  host policy.
- Use pre-candidate screens for temporary settings. Create a versioned EEL
  candidate only after a measured hypothesis and listening target exist.
- Keep public docs to summarized findings. Keep raw audio, local manifests,
  decoded excerpts, and generated run folders outside git.
