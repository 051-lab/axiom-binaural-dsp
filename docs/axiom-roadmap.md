# Axiom 90-Day Roadmap

## Summary

This roadmap turns the questions and answers in `docs/axiom-notes.html` into a staged work plan. The priority is foundations first: protect the accepted `v4.1.4.10` baseline, improve observability, expand evidence, and only then decide whether another v4 refinement or a v5 architecture proposal is justified.

The current product stance is:

- Axiom Clean remains the only accepted product baseline.
- Axiom Lab is where fixtures, metrics, corpus work, and analog-color research happen.
- Axiom Color is not a public product unless future evidence proves it deserves separate ownership.
- No sound-changing EEL edit happens without a scoped candidate, qualification, and listening acceptance.

## Roadmap Lanes

| Lane | Questions Covered | Outcome |
| --- | --- | --- |
| Source of truth and repo hygiene | q1, q2, q6, q9, q15 | Future users and agents can identify the accepted baseline, local paths, rules, and current state without stale instructions. |
| Measurement and observability | q3, q4, q10, q11, q14 | The test suite explains stage behavior, not only final pass/fail output. |
| Corpus and listening evidence | q5, q7, q12, q13, q14 | Listening and test material cover real user playback classes, not only high-energy stress excerpts. |
| Android and device validation | q12, q14, q17 | RootlessJamesDSP/Android behavior is documented and repeatable enough to trust field results. |
| Architecture and product direction | q8, q9, q16, q18 | Axiom Clean stays focused while v5 and Color remain gated by evidence. |

## Phase 0: Immediate Stabilization

Goal: remove avoidable confusion before deeper technical work.

- Create a source-of-truth cleanup issue or checklist covering stale baseline references, especially `.github/copilot-instructions.md`, `tools/axiom-team/skills/axiom-engineering/SKILL.md`, and hot-reload defaults.
- Treat `docs/axiom-roadmap.md`, `docs/current-state.md`, and `docs/axiom-system-overview.html` as public repo docs. Keep `docs/axiom-notes.html` local-only unless it is sanitized first.
- Add or resolve the missing `LICENSE` file mismatch because the README advertises MIT.
- Add a current-state doc or generated section that records accepted baseline, hash, host policy, active docs, and local/private artifact boundaries.
- Keep the accepted EEL baseline unchanged during this phase.

Done when:

- No current-facing assistant or user doc identifies `.8` or `.9` as the accepted baseline.
- The repo has an explicit decision about local HTML docs and license state.
- A fresh agent can identify `src/axiom_binaural_dsp_v4.1.4.10.eel` as the accepted baseline from one starting document.

## Phase 1: Measurement Foundation

Goal: make Axiom's existing stages more observable before proposing more DSP changes.

- Maintain `docs/tool-inventory.md` so every script has a clear purpose, JDSP side-effect label, output policy, and artifact safety rule.
- Expand the implemented stage-tap fixture runner for pre/post bass, spatial width, exciter, STFT, and output reserve paths from `docs/stage-observability-plan.md`.
- Follow `docs/bass-host-limiter-investigation-plan.md` for `Sub Harmonics Gain` and host-limiter evidence around `+4`, `+6`, `+8`, `+10`, and `+12 dB`.
- Keep expanding the first perceptual metrics layer in `scripts/analyze_audio_perceptual_metrics.py`: loudness proxy, true-peak proxy, crest/envelope behavior, ERB-like band energy, transient measures, and side/mid balance now exist as standalone offline metrics and are wired into candidate, corpus, local-material, and A/B reports.
- Use `scripts/run_jdsp_exciter_probe_screen.py` for lower-level generated exciter probes because high-energy material does not meaningfully exercise the current exciter behavior.

Done when:

- A future agent can determine which stage caused a measured change.
- Bass/reserve/host-limiter behavior and offline capture behavior are measurable beyond sample peak.
- Candidate, corpus, local-material, and A/B reports expose perceptual metric deltas without turning them into unsupported automatic gates.
- Exciter usefulness can be tested on material where it should actually activate.

## Phase 2: Corpus And Listening Evidence

Goal: build a small, brutal, legally clean corpus where every item has a job.

- Categorize missing material classes: low-level dynamic material, sibilant vocals, cymbals, dense modern pop/EDM, hip-hop/trap sub bass, rock/metal guitars, acoustic bass, piano, orchestral crescendos, mono/narrow recordings, flawed sources, speech, bass-light material, and already-wide mixes.
- Record provenance and license rules for every shared test item. Keep private/local tracks outside git.
- Add a structured listening notes template that captures device, output path, host settings, Axiom version, slider settings, material, comparison version, fatigue, bass, punch, width, center, air, harshness, loudness, and decision.
- Define level-matched A/B package requirements for future listening candidates.
- Keep subjective listening as the acceptance gate, but make the notes searchable and comparable across versions.

Done when:

- New candidates can be checked against several material classes instead of one favorite track.
- Listening results can be compared across versions and devices.
- The corpus explains why each excerpt exists and which failure mode it exposes.

## Phase 3: Android And Device Validation

Goal: stop treating WSL/JDSP as proof of Android behavior.

- Create an Android validation document for RootlessJamesDSP with host settings, file deployment, hash/filename checks, reboot persistence, and route sanity checks.
- Build a phone-test package workflow that exports accepted and candidate scripts, SHA-256 hashes, settings checklist, material list, and listening form.
- Define manual fallback checks for cases where adb or direct app paths are unavailable.
- Add a device matrix: primary Android phone, one speaker path, one wired or USB path if available, one Bluetooth path, and WSL/JDSP lab route.
- Track whether host crossfeed is off for qualification and manually enabled only for compatibility/listening checks.

Done when:

- The same candidate can be tested on Android without guessing which file or settings are active.
- Android listening notes identify device, route, settings, and version with enough detail to reproduce the test.
- WSL evidence and Android evidence are clearly separated.

## Phase 4: Architecture Decision Gate

Goal: decide the next DSP direction only after the foundations are stronger.

- Review Phase 1-3 evidence and choose one of three paths:
  - continue v4 refinement with no new architecture;
  - create a narrow v4 candidate for bass/reserve, exciter, STFT, or spatial behavior;
  - draft a v5 architecture proposal.
- Keep v5 gated by architecture-level change only: adaptive material-aware laws, redesigned gain architecture, major new proven stage, formal device/profile architecture, or validated Clean/Color split.
- Keep Axiom Color in Axiom Lab until analog processing passes aliasing, IMD, headroom, CPU, mono, side/mid, limiter, and listening tests.
- Apply the removal policy before adding features: delete or retire complexity that is not audible, measurable, protective, or explanatory.

Done when:

- The next sound-changing candidate has a clear hypothesis, measured target, scoped edit boundary, and listening target.
- v5 is either explicitly deferred or justified by a written architecture proposal.
- Axiom Clean remains stable and trusted regardless of lab experiments.

## Acceptance Criteria For The Roadmap

- The roadmap improves the development system before adding audio features.
- Every lane maps back to one or more questions in `docs/axiom-notes.html`.
- The accepted `.10` baseline remains immutable until a future qualified candidate passes listening.
- Roadmap work does not require committing audio captures, private tracks, or local manifests.
- Documentation distinguishes public repo state from local/private engineering state.
