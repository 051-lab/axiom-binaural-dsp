# Axiom Binaural DSP

[![Version](https://img.shields.io/badge/version-v4.1.4.8-blue.svg)](https://github.com/051-lab/axiom-binaural-dsp/releases)
[![Platform](https://img.shields.io/badge/platform-JamesDSP-green.svg)](https://github.com/james34602/JamesDSPManager)
[![License](https://img.shields.io/badge/license-MIT-yellow.svg)](LICENSE)

**Phase-coherent mastering-grade binaural processing for JamesDSP**

Axiom Binaural DSP is a device-neutral EEL2 enhancement core for JamesDSP. `v4.1.4.8` is the accepted listening baseline: it preserves the transparent default behavior established in `.7` and adds bass-aware output reserve when Sub Harmonics Gain is raised above its `+4 dB` default.

## Features

### M/S Spatializer
- Three-way spatial processing with bass below 150 Hz folded to mono
- Independent low-mid and high-frequency width control

### Virtual Sub-Bass Generator
- Psychoacoustic sub-bass synthesis via soft-clip saturation
- 90 Hz low-band extraction and harmonic isolation with cascaded biquads
- Direct dry path in `v4.1.4.6` and later; generated harmonics are additive only
- Harmonic blending for perceived bass extension on small drivers
- Gain control: -12 to 12 dB

### Dynamic Exciter
- Dynamic high-frequency excitation based on equal-loudness contours
- Sample-rate-derived loudness envelope timing
- Air band extraction above 11 kHz
- Sensitivity control: 0-100%

### STFT Resonance Suppressor
- Stereo-linked per-bin attenuation in the 2-6 kHz region
- Adaptive per-bin floor and smoothed gain control

### Host-Owned Output Stages
- Crossfeed is not part of the Axiom script; enable JamesDSP crossfeed manually when wanted
- `v4.1.4.7` adds a fixed `-1.0 dB` transparent output reserve before the host stage
- `v4.1.4.8` retains the `.7` reserve and adds matching output reserve only for Sub Harmonics gain above `+4 dB`
- JDSP supplies the terminal limiter; the qualified Axiom baseline now uses `-1.00 dB`, `60 ms` release, `0 dB` postgain

## Installation

### JamesDSP Android
1. Copy `src/axiom_binaural_dsp_v4.1.4.8.eel` to your JamesDSP liveprog directory
2. Open JamesDSP -> Liveprog -> Load script -> select `axiom_binaural_dsp_v4.1.4.8.eel`
3. Enable the Liveprog engine
4. Set output limiter threshold to `-1.00 dB`, release `60 ms`, and postgain `0.00 dB`
5. For headphones only, enable JamesDSP crossfeed manually if desired

### JamesDSP Linux
1. Run `scripts/hot_reload_liveprog.sh src/axiom_binaural_dsp_v4.1.4.8.eel`.
2. The script loads Liveprog with crossfeed disabled, the qualified host limiter settings, and saves `Axiom-v4.1.4.8-accepted`.

`presets/axiom-preset.conf` records the neutral accepted-baseline host configuration as a JDSP `audio.conf`-style template. Update its `liveprog_file` path before loading it directly; the hot-reload script writes the active absolute path automatically.

### Real-Host A/B Testbench

For development comparisons, run both scripts through the actual JDSP Liveprog engine:

```bash
scripts/run_jdsp_ab_testbench.py \
  src/axiom_binaural_dsp_v4.1.4.7.eel \
  src/axiom_binaural_dsp_v4.1.4.8.eel \
  /tmp/axiom-v47-v48-host-suite \
  --pulse-server unix:/run/user/1000/pulse/native
```

The testbench generates deterministic probes, including a sustained `90 Hz` bass-pressure input that exposes default-setting terminal-limiter pressure, routes only JDSP's processed output into a private temporary capture sink, rejects silent captures, and produces WAV, JSON, and Markdown comparisons. Each render snapshots and restores the loaded Liveprog file and every neutral-host setting it changes. Loading a script necessarily reinitializes its internal DSP history, so run this in a dedicated development JDSP session rather than during normal listening. The specified Pulse server must be the server used by the running JDSP process.

On this WSL development workstation, run the managed qualification workflow to set up the capture route, exercise the default and elevated Sub Harmonics cases, and restore ordinary PipeWire-Pulse audio afterward:

```bash
scripts/run_jdsp_wsl_qualification.py \
  src/axiom_binaural_dsp_v4.1.4.7.eel \
  src/axiom_binaural_dsp_v4.1.4.8.eel \
  /tmp/axiom-v47-v48-wsl-qualification
```

This command expects the local route launcher at `~/.local/bin/jdsp-audio-reset`, which provides a native PulseAudio `JamesDSP` sink backed by the Windows output route. It sets the qualified host limiter threshold to `-1.00 dB` once for the managed test session, restores the preceding setting afterward, and creates temporary `+8 dB` and `+12 dB` slider fixtures in its output directory without modifying source EEL files. It also renders an original deterministic three-passage, bass-heavy program-like corpus at default controls; these are engineering stimuli, not commercial music excerpts. At default controls, any pressure or corpus capture above `-0.50 dBFS` is reported as `PASS_WITH_INVESTIGATION`: it records probable terminal-limiter involvement rather than asserting an EEL regression. Use `--skip-route-start` only when an equivalent JamesDSP route is already active, and `--keep-route-running` only when the dedicated test audio session should remain active.

To include private excerpts from locally owned audio, create a manifest outside the repository, for example `/tmp/axiom-local-material.json`:

```json
{
  "tracks": [
    {
      "label": "bass-heavy excerpt 1",
      "path": "/absolute/path/to/local-track.flac",
      "start_seconds": 30.0,
      "duration_seconds": 20.0
    }
  ]
}
```

Then add `--local-material-manifest /tmp/axiom-local-material.json` to `run_jdsp_wsl_qualification.py`. The runner decodes only the selected excerpt windows to temporary analysis WAVs without gain normalization, and does not copy source audio or manifest paths into the repository.

The accepted `.8` baseline was additionally checked with four CC0 high-energy music excerpts outside the repository. With a persistent JDSP limiter threshold of `-1.00 dB`, all four candidate captures remained unclipped; dense electronic material remained close enough to the ceiling to be recorded as limiter involvement rather than hidden by further EEL attenuation.

### Measurement Qualification

Before treating small A/B differences as DSP behavior, qualify repeated captures of the same script and stimulus:

```bash
scripts/qualify_jdsp_repeatability.py \
  /tmp/axiom-repeat/run-1.wav /tmp/axiom-repeat/run-2.wav /tmp/axiom-repeat/run-3.wav \
  /tmp/axiom-repeat/run-4.wav /tmp/axiom-repeat/run-5.wav \
  --max-peak-spread-db 0.10 --max-rms-spread-db 0.10 --min-correlation 0.999 \
  --json /tmp/axiom-repeat/repeatability.json \
  --markdown /tmp/axiom-repeat/repeatability.md
```

The acceptance limits are caller-selected policy until enough repeated real-host renders establish tighter tolerances. The report qualifies relative capture repeatability only; it does not establish absolute host latency.

For a low-level deterministic probe and its processed capture, measure the stimulus-conditioned host-path response:

```bash
scripts/analyze_jdsp_transfer.py \
  /tmp/axiom-transfer/stimulus.wav /tmp/axiom-transfer/processed.wav \
  --label v4.1.4.7-mono-probe \
  --json /tmp/axiom-transfer/transfer.json \
  --markdown /tmp/axiom-transfer/transfer.md
```

This report measures the complete processed host path, not Axiom in isolation. It rejects silent, clipped, or louder-than-`-6 dBFS` output and reports identifiable `M->M`, `M->S`, `S->M`, and `S->S` matrix elements only when a pure mono or side-only probe makes that matrix column observable.

To investigate the user-adjustable bass branch before creating a new DSP revision, sweep its exact nonlinear injection topology over tone level and slider gain:

```bash
scripts/analyze_axiom_subharmonics.py \
  --json /tmp/axiom-subharmonics.json \
  --markdown /tmp/axiom-subharmonics.md
```

This is a branch-local model of the `.7` bass generator and terminal reserve. To model the accepted `.8` baseline's additional reserve, pass `--reserve-above-slider-db 4`. It identifies settings that should be verified through real-host captures, but it does not model exciter, STFT, limiter, or music-program behavior.

### Controlled Pi Engineering Harness

The project includes a local-first Pi harness for disciplined future Axiom
experiments. It isolates the session from globally installed agent extensions,
protects the accepted `.8` file by hash and path, creates candidates in
external worktrees, serializes real-JDSP capture runs, and requires separate
human confirmations for listening acceptance, publication, and merge.

```bash
node tools/axiom-team/bin/axiom-team.mjs init
node tools/axiom-team/bin/axiom-team.mjs doctor
scripts/axiom_team.sh
```

Reports, captures, candidate worktrees, and locally registered audio material
remain outside git. See [docs/engineering-harness.md](docs/engineering-harness.md)
for commands and acceptance policy.

## Quick Start: Default Slider Settings

| Slider | Parameter | Default | Range |
|--------|-----------|---------|-------|
| slider1 | Sub Harmonics Gain | 4 dB | -12 to 12 dB |
| slider2 | Global Side Width | 135% | 0 to 200% |
| slider3 | Fletcher-Munson Sensitivity | 50% | 0 to 100% |
| slider5 | Low-Mid Width Multiplier | 140% | 0 to 200% |
| slider6 | High-Frequency Width Multiplier | 110% | 0 to 150% |
| slider7 | STFT Resonance Suppression | 50% | 0 to 100% |

## Repository Structure

```
axiom-binaural-dsp/
  src/
    axiom_binaural_dsp_v4.1.4.6.eel  # Phase-preserving bass predecessor
    axiom_binaural_dsp_v4.1.4.7.eel  # Transparent-headroom comparison reference
    axiom_binaural_dsp_v4.1.4.8.eel  # Accepted bass-aware headroom baseline
  scripts/
    axiom_team.sh                     # Isolated Pi engineering-harness launcher
    hot_reload_liveprog.sh            # JDSP A/B preset loader
    analyze_axiom_crossfeed.py        # Crossfeed transfer audit
    analyze_axiom_bass_path.py        # Removed dry-phase reconstruction audit
    generate_jdsp_stimuli.py          # Deterministic stereo capture probes
    generate_axiom_program_corpus.py  # Original deterministic bass-heavy passages
    render_jdsp_host.py               # Isolated real-JDSP WAV renderer
    compare_jdsp_captures.py          # Capture metrics and difference reports
    run_jdsp_ab_testbench.py          # End-to-end host A/B suite
    run_jdsp_program_corpus.py        # Default-control corpus margin report
    run_jdsp_local_material.py        # Private local-excerpt margin report
    run_jdsp_wsl_qualification.py     # Managed WSL route and bass-headroom qualification
    qualify_jdsp_repeatability.py     # Repeated-capture qualification
    analyze_jdsp_transfer.py          # Stimulus-conditioned host-path matrix analysis
    analyze_axiom_subharmonics.py     # Sub Harmonics Gain branch characterization
  tests/
    test_qualify_jdsp_repeatability.py
    test_analyze_jdsp_transfer.py
    test_analyze_axiom_subharmonics.py
    test_generate_axiom_program_corpus.py
    test_generate_jdsp_stimuli.py
    test_run_jdsp_program_corpus.py
    test_run_jdsp_local_material.py
    test_run_jdsp_wsl_qualification.py
  docs/
    architecture.md           # Technical architecture documentation
    qualification-v4.1.4.8.md # Accepted-baseline evidence and reproduction record
    engineering-harness.md    # Controlled Pi candidate and release workflow
  tools/axiom-team/
    extensions/index.ts       # Restricted Pi tools and approval commands
    policy.json               # Immutable baseline and host-policy anchor
    lib/core.mjs              # State machine and gated local automation
  presets/
    axiom-preset.conf         # JDSP accepted-baseline configuration template
  README.md
  CHANGELOG.md
```

## Architecture

See [docs/architecture.md](docs/architecture.md) for the full technical documentation including signal chain diagram, DSP math, filter coefficient tables, and tuning guides.

## License

MIT License - see LICENSE for details.

## Acknowledgments

- Bauer BS2B crossfeed algorithm
- Fletcher-Munson equal-loudness research
- JamesDSP EEL2 runtime by James34602

---

## AI Agent Setup

This repository is configured for AI agent collaboration. The following files provide complete context for any AI assistant working on this codebase:

| File | Purpose |
|------|---------|
| [`AGENTS.md`](AGENTS.md) | **Start here** — complete operating instructions, EEL2 constraints, file editing rules |
| [`.github/copilot-instructions.md`](.github/copilot-instructions.md) | GitHub Copilot workspace context (auto-loaded) |
| [`CONTRIBUTING.md`](CONTRIBUTING.md) | Commit conventions, code standards, testing checklist |
| [`docs/JDSP4Linux_Knowledge_Base.md`](docs/JDSP4Linux_Knowledge_Base.md) | Full EEL2/JDSP runtime API reference |
| [`docs/architecture.md`](docs/architecture.md) | Current signal chain and ownership documentation |
| [`docs/qualification-v4.1.4.8.md`](docs/qualification-v4.1.4.8.md) | Accepted `.8` verification record |
| [`docs/engineering-harness.md`](docs/engineering-harness.md) | Controlled Pi experimentation and release gates |

### Quick Reference for AI Agents

```eel2
// Critical rules (violations cause mute/crash):
// 1. Never assign to $pi
// 2. No FractionalDelayLineInit (use manual circular buffers)
// 3. No % modulo (use conditional wrap)
// 4. Use this.* for persistent state inside function()
// 5. Additive mixing only (never replace spl0/spl1 mid-chain)
// 6. Final @sample lines MUST be: spl0 = out_L; spl1 = out_R;
// 7. Initialize ALL variables in @init
```
