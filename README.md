# Axiom Binaural DSP

[![Version](https://img.shields.io/badge/version-v4.1.4.9-blue.svg)](https://github.com/051-lab/axiom-binaural-dsp/releases)
[![Platform](https://img.shields.io/badge/platform-JamesDSP-green.svg)](https://github.com/james34602/JamesDSPManager)
[![License](https://img.shields.io/badge/license-MIT-yellow.svg)](LICENSE)

**Measured psychoacoustic stereo enhancement processing for JamesDSP**

Axiom Binaural DSP is a device-neutral EEL2 enhancement core for JamesDSP. `v4.1.4.9` is the accepted listening baseline: it preserves `.8` behavior at default controls and reduces excess output retreat when Sub Harmonics Gain is raised above its `+4 dB` default.

## Features

### M/S Spatializer
- Three-way spatial processing with bass below 150 Hz folded to mono
- Independent low-mid and high-frequency width control

### Bass Harmonic Enhancement
- Psychoacoustic virtual-bass enhancement via soft-clip saturation
- 90 Hz low-band extraction and harmonic isolation with cascaded biquads
- Direct dry path in `v4.1.4.6` and later; generated harmonics are additive only
- Harmonic blending for perceived bass extension on small drivers
- Gain control: -12 to 12 dB

### Dynamic Exciter
- Level-dependent high-frequency excitation for perceived air and clarity
- Sample-rate-derived loudness envelope timing
- Air band extraction above 11 kHz
- Sensitivity control: 0-100%

### STFT Resonance Suppressor
- Stereo-linked per-bin attenuation in the 2-6 kHz region
- Adaptive per-bin floor and smoothed gain control

### Host-Owned Output Stages
- Crossfeed is not part of the Axiom script; enable JamesDSP crossfeed manually when wanted
- `v4.1.4.7` adds a fixed `-1.0 dB` transparent output reserve before the host stage
- `v4.1.4.9` retains the `.7` fixed reserve and applies the accepted `0.750 dB/dB` additional reserve only for Sub Harmonics gain above `+4 dB`
- JDSP supplies the terminal limiter; the qualified Axiom baseline now uses `-1.00 dB`, `60 ms` release, `0 dB` postgain

## Installation

### JamesDSP Android
1. Copy `src/axiom_binaural_dsp_v4.1.4.9.eel` to your JamesDSP liveprog directory
2. Open JamesDSP -> Liveprog -> Load script -> select `axiom_binaural_dsp_v4.1.4.9.eel`
3. Enable the Liveprog engine
4. Set output limiter threshold to `-1.00 dB`, release `60 ms`, and postgain `0.00 dB`
5. For headphones only, enable JamesDSP crossfeed manually if desired

### JamesDSP Linux
1. Run `scripts/hot_reload_liveprog.sh src/axiom_binaural_dsp_v4.1.4.9.eel`.
2. The script loads Liveprog with crossfeed disabled, the qualified host limiter settings, and saves `Axiom-v4.1.4.9-accepted`.

`presets/axiom-preset.conf` records the neutral accepted-baseline host configuration as a JDSP `audio.conf`-style template. Update its `liveprog_file` path before loading it directly; the hot-reload script writes the active absolute path automatically.

### Real-Host A/B Testbench

For development comparisons, run both scripts through the actual JDSP Liveprog engine:

```bash
scripts/run_jdsp_ab_testbench.py \
  src/axiom_binaural_dsp_v4.1.4.8.eel \
  src/axiom_binaural_dsp_v4.1.4.9.eel \
  /tmp/axiom-v48-v49-host-suite \
  --pulse-server unix:/run/user/1000/pulse/native
```

The testbench generates deterministic probes, including a sustained `90 Hz` bass-pressure input that exposes default-setting terminal-limiter pressure, routes only JDSP's processed output into a private temporary capture sink, rejects silent captures, and produces WAV, JSON, and Markdown comparisons. Each render snapshots and restores the loaded Liveprog file and every neutral-host setting it changes. Loading a script necessarily reinitializes its internal DSP history, so run this in a dedicated development JDSP session rather than during normal listening. The specified Pulse server must be the server used by the running JDSP process.

On this WSL development workstation, run the managed qualification workflow to set up the capture route, exercise the default and elevated Sub Harmonics cases, and restore ordinary PipeWire-Pulse audio afterward:

```bash
scripts/run_jdsp_wsl_qualification.py \
  src/axiom_binaural_dsp_v4.1.4.8.eel \
  src/axiom_binaural_dsp_v4.1.4.9.eel \
  /tmp/axiom-v48-v49-wsl-qualification
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

The accepted `.9` baseline was qualified against `.8` with four CC0 high-energy music excerpts outside the repository. With a persistent JDSP limiter threshold of `-1.00 dB`, all four `.9` captures remained unclipped; dense electronic material remained close enough to the ceiling to be recorded as existing limiter involvement rather than hidden by further EEL attenuation.

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

This is a branch-local model of the `.7` bass generator and terminal reserve. The historical `.8` full-reserve behavior can be modeled with `--reserve-above-slider-db 4`; the accepted `.9` reserve slope is established by its real-host qualification record. This tool identifies settings that should be verified through real-host captures, but it does not model exciter, STFT, limiter, or music-program behavior.

To investigate whether the accepted host limiter participates at `.9` default
controls without creating a new DSP candidate, run a repeated same-script
limiter-threshold sweep against the registered local-material manifest:

```bash
scripts/run_jdsp_limiter_sweep.py \
  src/axiom_binaural_dsp_v4.1.4.9.eel \
  /absolute/path/to/axiom-external-cc0-manifest.json \
  /tmp/axiom-v49-limiter-sweep
```

By default this targets the high-energy electronic excerpt and compares `-0.50`,
`-1`, and `-3 dB` JDSP limiter thresholds with five renders each. It reports
waveform-repeatability evidence and threshold-correlated peak, RMS, crest, and
short-window envelope shifts. The classification uses only non-clipping
metrics that repeat within policy; it identifies host-limiter behavior, not an
EEL regression by itself.

After limiter participation is established, capture the accepted-setting
dense-material stress profile at the qualified `-1.00 dB` threshold:

```bash
scripts/run_jdsp_accepted_stress.py \
  src/axiom_binaural_dsp_v4.1.4.9.eel \
  /absolute/path/to/axiom-external-cc0-manifest.json \
  /tmp/axiom-v49-accepted-stress
```

This renders every registered excerpt three times at the accepted host
setting. Clipping, silence, or an unrepeatable level profile fails the gate;
stable output above the `-0.50 dBFS` observation level is retained as accepted
limiter-pressure evidence for evaluating later candidates.

To identify the usable real-music range of the user-adjustable bass control,
run the accepted `.9` Sub Harmonics Gain map:

```bash
scripts/run_jdsp_sub_slider_map.py \
  src/axiom_binaural_dsp_v4.1.4.9.eel \
  /absolute/path/to/axiom-external-cc0-manifest.json \
  /tmp/axiom-v49-sub-slider-map
```

The map renders temporary external fixtures at `+4`, `+6`, `+8`, `+10`, and
`+12 dB` Sub Harmonics Gain through the accepted `-1.00 dB` host limiter
setting. An elevated-gain clipping result identifies a usable-range boundary;
it does not invalidate the accepted default baseline unless `+4 dB` itself
fails. The map also flags repeatable whole-output RMS retreat beyond `1 dB`
relative to default, since added peak reserve can trade playback loudness for
bass-control headroom.

The following reserve-law commands reproduce the pre-`.9` investigation that
identified `.8` output retreat. To screen whether `.8` is over-reserving output above its default without
creating a DSP candidate, test reduced reserve slopes at practical `+8 dB`
bass gain:

```bash
scripts/run_jdsp_reserve_law_screen.py \
  src/axiom_binaural_dsp_v4.1.4.8.eel \
  /absolute/path/to/axiom-external-cc0-manifest.json \
  /tmp/axiom-v48-reserve-screen
```

The focused default screen targets the electronic and hip-hop excerpts and
tests full reserve (`1.000`) against reduced slopes (`0.875`, `0.750`, and
`0.500`). It excludes one conditioning render before measuring each
fixture/excerpt set so newly loaded host state is not counted as repeatability
evidence. A reduced slope is viable only when every screened excerpt recovers
repeatable RMS level without clipping or exceeding the `-0.50 dBFS` peak
observation boundary. Passing this screen justifies broader qualification; it
does not create or accept a new Axiom script.

To range-qualify the slopes selected by that focused screen, test every
registered material excerpt over elevated bass settings:

```bash
scripts/run_jdsp_reserve_range_qualification.py \
  src/axiom_binaural_dsp_v4.1.4.8.eel \
  /absolute/path/to/axiom-external-cc0-manifest.json \
  /tmp/axiom-v48-reserve-range
```

The default qualification tests slopes `0.750` and `0.500`, beginning at
`+12 dB` and descending through `+10`, `+8`, and `+6 dB` only while the slope
remains safe. A verified clipping or peak-margin rejection ends that slope
immediately because it cannot qualify for the full control range. A scalar
repeatability failure receives one fresh conditioned retry before it fails the
measurement, because unstable capture evidence is not a reserve-law rejection.

### Controlled Pi Engineering Harness

The project includes a local-first Pi harness for disciplined future Axiom
experiments. It isolates the session from globally installed agent extensions,
protects the accepted `.9` file by hash and path, creates candidates in
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
    axiom_binaural_dsp_v4.1.4.8.eel  # Previous bass-aware headroom baseline
    axiom_binaural_dsp_v4.1.4.9.eel  # Accepted reduced bass-reserve baseline
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
    run_jdsp_limiter_sweep.py         # Same-script host-limiter participation probe
    run_jdsp_accepted_stress.py        # Repeated accepted-setting dense-material baseline
    run_jdsp_sub_slider_map.py         # Real-music Sub Harmonics Gain range map
    run_jdsp_reserve_law_screen.py     # Experimental elevated-bass reserve-law screen
    run_jdsp_reserve_range_qualification.py # Reduced-reserve elevated-range qualifier
  tests/
    test_qualify_jdsp_repeatability.py
    test_analyze_jdsp_transfer.py
    test_analyze_axiom_subharmonics.py
    test_generate_axiom_program_corpus.py
    test_generate_jdsp_stimuli.py
    test_run_jdsp_program_corpus.py
    test_run_jdsp_local_material.py
    test_run_jdsp_wsl_qualification.py
    test_run_jdsp_limiter_sweep.py
    test_run_jdsp_accepted_stress.py
    test_run_jdsp_sub_slider_map.py
    test_run_jdsp_reserve_law_screen.py
    test_run_jdsp_reserve_range_qualification.py
  docs/
    architecture.md           # Technical architecture documentation
    qualification-v4.1.4.8.md # Previous-baseline evidence and reproduction record
    qualification-v4.1.4.9.md # Accepted-baseline evidence and reproduction record
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
| [`docs/qualification-v4.1.4.8.md`](docs/qualification-v4.1.4.8.md) | Previous `.8` verification record |
| [`docs/qualification-v4.1.4.9.md`](docs/qualification-v4.1.4.9.md) | Accepted `.9` verification record |
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
