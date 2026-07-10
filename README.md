# Axiom Binaural DSP

[![Version](https://img.shields.io/badge/version-v4.1.4.11-blue.svg)](https://github.com/051-lab/axiom-binaural-dsp/releases)
[![Platform](https://img.shields.io/badge/platform-JamesDSP-green.svg)](https://github.com/james34602/JamesDSPManager)
[![License](https://img.shields.io/badge/license-MIT-yellow.svg)](LICENSE)

**Measured psychoacoustic stereo enhancement processing for JamesDSP**

Axiom Binaural DSP is a device-neutral EEL2 enhancement core for JamesDSP. `v4.1.4.11` is the accepted listening baseline: it retains the `.10` restrained low-mid width setting and reduces the elevated-bass output reserve slope for more practical density above the default Sub Harmonics setting.

For the shortest system orientation, start with [`AXIOM.md`](AXIOM.md). For
new sound-changing work, use
[`docs/dsp-change-workflow.md`](docs/dsp-change-workflow.md) before creating a
Labs fixture or candidate.

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
- `v4.1.4.10` retained the `.9` reserve behavior and reduced default `150 Hz-4 kHz` side width from `1.890x` to `1.701x`
- `v4.1.4.11` keeps `.10` unchanged at the default `+4 dB` Sub Harmonics
  setting and reduces elevated-bass reserve slope from `0.750 dB/dB` to
  `0.500 dB/dB`
- JDSP supplies the terminal limiter; the qualified Axiom baseline now uses `-1.00 dB`, `60 ms` release, `0 dB` postgain

## Installation

### JamesDSP Android
1. Copy `src/axiom_binaural_dsp_v4.1.4.11.eel` to your JamesDSP liveprog directory
2. Open JamesDSP -> Liveprog -> Load script -> select `axiom_binaural_dsp_v4.1.4.11.eel`
3. Enable the Liveprog engine
4. Set output limiter threshold to `-1.00 dB`, release `60 ms`, and postgain `0.00 dB`
5. For headphones only, enable JamesDSP crossfeed manually if desired

### JamesDSP Linux
1. Run `scripts/hot_reload_liveprog.sh src/axiom_binaural_dsp_v4.1.4.11.eel Axiom-v4.1.4.11-accepted`.
2. The script loads Liveprog with crossfeed disabled, the qualified host limiter settings, and saves the accepted `.11` preset.

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

To validate local-material manifest compatibility and corpus metadata coverage:

```bash
scripts/validate_axiom_material_manifest.py \
  /tmp/axiom-local-material.json \
  --strict-metadata \
  --json /tmp/axiom-material-validation.json \
  --markdown /tmp/axiom-material-validation.md
```

Use `--write-metadata-template` to create a local enriched draft when a manifest
has paths and excerpts but not taxonomy metadata yet.

See [`docs/corpus-material.md`](docs/corpus-material.md) for the current
material-class and failure-mode taxonomy.

To validate a structured human listening record before using it as acceptance
evidence:

```bash
scripts/validate_axiom_listening_record.py \
  ~/.local/state/axiom-engineering/listening-records/v4.1.4.11-phone.json \
  --json /tmp/axiom-listening-validation.json \
  --markdown /tmp/axiom-listening-record.md
```

Full listening records can contain private material names, timestamps, and
device route details. Keep them local unless sanitized. See
[`docs/listening-records.md`](docs/listening-records.md).

To build a local RootlessJamesDSP validation package with script hashes,
settings checklist, and a listening-record template:

```bash
scripts/build_android_validation_package.py \
  src/axiom_binaural_dsp_v4.1.4.11.eel \
  /tmp/axiom-android-v4.1.4.11
```

See [`docs/android-validation.md`](docs/android-validation.md).

To build a local level-matched A/B listening package from matched processed WAV
folders:

```bash
scripts/build_axiom_ab_listening_package.py \
  /tmp/axiom-captures/accepted \
  /tmp/axiom-captures/candidate \
  /tmp/axiom-ab-listening-vNEXT
```

See [`docs/ab-listening-packages.md`](docs/ab-listening-packages.md).

To validate local device and route coverage:

```bash
scripts/validate_axiom_device_matrix.py \
  ~/.local/state/axiom-engineering/device-matrix.json \
  --strict-coverage \
  --strict-setup
```

See [`docs/device-matrix.md`](docs/device-matrix.md).

To snapshot Windows audio endpoint status and the active default render device
from WSL before route checks:

```bash
scripts/audit_windows_audio_endpoints.py \
  --json /tmp/axiom-windows-audio-endpoints.json \
  --markdown /tmp/axiom-windows-audio-endpoints.md
```

Add `--require-default-route wired_or_usb` or
`--require-default-route bluetooth` after switching the Windows default output
to fail fast unless that route is active and healthy.

Endpoint/default-render status is only a setup hint; playback qualification
still requires the device matrix checks.

To create a local route qualification package after switching the Windows
default output to a wired/USB or Bluetooth endpoint:

```bash
scripts/qualify_windows_default_route.py \
  wired_or_usb \
  /tmp/axiom-wired-route-qualification
```

The command blocks before playback if Windows is still using another output.
When it passes preflight, it restarts the managed JDSP route, hot-reloads the
accepted `.11` script, verifies host settings, plays a short probe, and writes
local evidence for user confirmation.

To build a local checklist package for the remaining physical route checks:

```bash
scripts/build_device_readiness_package.py \
  src/axiom_binaural_dsp_v4.1.4.11.eel \
  /tmp/axiom-device-readiness \
  --device-matrix ~/.local/state/axiom-engineering/device-matrix.json
```

See [`docs/device-readiness-packages.md`](docs/device-readiness-packages.md).

To check whether the evidence foundation is ready before proposing another
sound-changing candidate:

```bash
scripts/evaluate_axiom_candidate_readiness.py \
  --json /tmp/axiom-candidate-readiness.json \
  --markdown /tmp/axiom-candidate-readiness.md
```

This gate verifies the accepted baseline hash, strict corpus metadata, strict
device-matrix coverage, and complete setup checks for available routes. A
blocked report means fix evidence inputs before creating a new EEL candidate. See
[`docs/candidate-readiness.md`](docs/candidate-readiness.md).

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

To isolate the accepted STFT stage without creating a sound-changing EEL revision, run the stage audit:

```bash
scripts/run_jdsp_stft_audit.py \
  src/axiom_binaural_dsp_v4.1.4.9.eel \
  /tmp/axiom-v49-stft-audit
```

The audit creates temporary external fixtures at `0%` and accepted `50%` suppression. For mono probes, each fixture routes the pre-STFT path to one output channel and the corresponding STFT-processed path to the other in the same JDSP render. This exposes round-trip and configured-suppression behavior without comparing independently scheduled stage timelines, and it repeats the impulse capture three times by default to qualify transient observations against STFT frame/load variation. It gates mute and clipping failures, but residual measurements are evidence for investigation rather than automatic justification for a new audio candidate.

To map accepted stereo width and mono compatibility against a temporary unity-width reference:

```bash
scripts/run_jdsp_width_mono_audit.py \
  src/axiom_binaural_dsp_v4.1.4.9.eel \
  /tmp/axiom-v49-width-mono-audit
```

This audit renders low-level pure-mid and pure-side multitone probes through real JDSP with the accepted width controls and with a temporary fixture set to `100%` global, mid, and high width. It reports accepted side gain relative to unity, unintended `M->S` and `S->M` leakage, low-frequency side collapse behavior, and integrity or terminal-level observations. Pure-side cancellation in a mono sum is intentional and is not itself classified as a defect.

To determine whether the measured width behavior is materially active in registered music excerpts:

```bash
scripts/run_jdsp_width_material_screen.py \
  src/axiom_binaural_dsp_v4.1.4.9.eel \
  ~/.local/share/axiom-test-material/cc0-opengameart/axiom-external-cc0-manifest.json \
  /tmp/axiom-v49-width-material-screen
```

The material screen compares accepted and temporary unity-width renders using band-specific side-to-mid energy ratios. An increased stereo side ratio is evidence about image character, not a mono-sum failure: a symmetric side-width change cancels from the output mono sum.

To screen restrained low-mid width options before creating an audio candidate:

```bash
scripts/run_jdsp_lowmid_width_screen.py \
  src/axiom_binaural_dsp_v4.1.4.9.eel \
  ~/.local/share/axiom-test-material/cc0-opengameart/axiom-external-cc0-manifest.json \
  /tmp/axiom-v49-lowmid-width-screen
```

The low-mid screen retains accepted `.9` as the reference and creates temporary `slider5 = 126%` and `slider5 = 115%` fixtures, producing effective low-mid side products of `1.701x` and `1.553x` against accepted `1.890x`. It measures `150-300`, `300-800`, `800-2000`, and `2000-4000 Hz` spatial balance and output integrity; a reduced setting becomes a listening candidate only after the measured tradeoff is defensible.

After creating a versioned `slider5 = 126%` candidate, qualify that intentional width change with its scoped gate rather than the generic default-transparency qualifier:

```bash
scripts/run_jdsp_lowmid_width_candidate_qualification.py \
  src/axiom_binaural_dsp_v4.1.4.9.eel \
  src/axiom_binaural_dsp_v4.1.4.10.eel \
  ~/.local/share/axiom-test-material/cc0-opengameart/axiom-external-cc0-manifest.json \
  /tmp/axiom-v410-lowmid-candidate-qualification
```

This qualification rejects any DSP edit beyond the candidate description and the two `slider5` default sites, then verifies real-host integrity and a measurable restrained `S/M` reduction in each affected band. A passing report permits listening; it is not listening acceptance.

To screen the remaining high-frequency width control from the accepted baseline
without creating a new DSP candidate:

```bash
scripts/run_jdsp_high_width_screen.py \
  src/axiom_binaural_dsp_v4.1.4.11.eel \
  ~/.local/share/axiom-test-material/cc0-opengameart/axiom-external-cc0-manifest.json \
  /tmp/axiom-v411-high-width-screen
```

The high-width screen retains accepted `slider6 = 110%` and creates temporary `105%` and `100%` fixtures, producing effective high-band side products of `1.485x`, `1.4175x`, and `1.350x`. It measures `4-7`, `7-12`, and `12-18 kHz` side balance and terminal integrity; no future candidate is justified without a measurable tradeoff and listening target.

The completed `.10` screen found consistent intentional high-band widening,
but no defensible retuning candidate: the `105%` fixture reduced tested
high-band `S/M` by only `0.318 dB` on average and produced the only terminal
observation on dense electronic material. Accepted `.10` remains unchanged;
see [`docs/high-width-screen-v4.1.4.10.md`](docs/high-width-screen-v4.1.4.10.md).

To screen the dynamic exciter sensitivity from the accepted baseline without
creating a new DSP candidate:

```bash
scripts/run_jdsp_exciter_sensitivity_screen.py \
  src/axiom_binaural_dsp_v4.1.4.11.eel \
  ~/.local/share/axiom-test-material/cc0-opengameart/axiom-external-cc0-manifest.json \
  /tmp/axiom-v411-exciter-screen
```

The exciter screen retains accepted `slider3 = 50%` and creates temporary
`35%` and `0%` fixtures. It measures `4-7`, `7-12`, and `12-18 kHz` band RMS,
side balance, and terminal integrity so any exciter retuning proposal is based
on measured clarity, air, and headroom tradeoffs rather than broad brightness
preference.

The completed registered-material screen found no defensible retuning
candidate: reducing or bypassing sensitivity changed tested high-band RMS by
only `0.013 dB` or `0.008 dB` on average, respectively, and all captures stayed
below the terminal observation boundary. Accepted `.10` remains unchanged; see
[`docs/exciter-sensitivity-screen-v4.1.4.10.md`](docs/exciter-sensitivity-screen-v4.1.4.10.md).

To exercise the accepted exciter on generated low-level material without
relying on private music excerpts:

```bash
scripts/run_jdsp_exciter_probe_screen.py \
  src/axiom_binaural_dsp_v4.1.4.11.eel \
  /tmp/axiom-v411-exciter-probes
```

This creates quiet air-bearing, dull-control, sibilance-texture, and louder
air-control probes, then renders accepted `50%`, reduced `35%`, and bypassed
`0%` exciter sensitivity through real JDSP. The intent is to verify whether the
accepted exciter adds measurable air only when low-level material gives it
something useful to lift. The report now includes activation checks for quiet
air lift, accepted/reduced/bypass depth order, dull-control restraint,
high-level-control restraint, and sibilance-presence restraint. These checks
flag investigation evidence; they do not create a candidate by themselves.

The completed generated-probe screen found useful accepted air-band activation
on quiet air-bearing material and correct backoff on louder bright material.
After adding absolute band-RMS context, the dull-control air delta is below the
`-90 dBFS` decision floor and the reduced-vs-bypass ordering difference is
within tolerance. No `.11` exciter candidate is justified; see
[`docs/exciter-probe-screen-v4.1.4.10.md`](docs/exciter-probe-screen-v4.1.4.10.md).

For a low-level deterministic probe and its processed capture, measure the stimulus-conditioned host-path response:

```bash
scripts/analyze_jdsp_transfer.py \
  /tmp/axiom-transfer/stimulus.wav /tmp/axiom-transfer/processed.wav \
  --label v4.1.4.7-mono-probe \
  --json /tmp/axiom-transfer/transfer.json \
  --markdown /tmp/axiom-transfer/transfer.md
```

This report measures the complete processed host path, not Axiom in isolation. It rejects silent, clipped, or louder-than-`-6 dBFS` output and reports identifiable `M->M`, `M->S`, `S->M`, and `S->S` matrix elements only when a pure mono or side-only probe makes that matrix column observable.

To add perceptual-proxy context to any local WAV capture without running JDSP:

```bash
scripts/analyze_audio_perceptual_metrics.py \
  /tmp/axiom-capture.wav \
  --label accepted-v4.1.4.11 \
  --json /tmp/axiom-capture-metrics.json \
  --markdown /tmp/axiom-capture-metrics.md
```

This reports ungated loudness proxy, true-peak proxy, crest/envelope behavior,
20 ms transient contrast, ERB-like band energy, and mid/side balance. These are
engineering proxies, not certified LUFS or true-peak measurements. See
[`docs/perceptual-metrics.md`](docs/perceptual-metrics.md). The same metric
bundle is also attached to A/B, generated corpus, private local-material, and
scoped candidate-qualification reports.

To investigate the user-adjustable bass branch before creating a new DSP revision, sweep its exact nonlinear injection topology over tone level and slider gain:

```bash
scripts/analyze_axiom_subharmonics.py \
  --json /tmp/axiom-subharmonics.json \
  --markdown /tmp/axiom-subharmonics.md
```

This is a branch-local model of the `.7` bass generator and terminal reserve. The historical `.8` full-reserve behavior can be modeled with `--reserve-above-slider-db 4`; the accepted `.9` reserve slope is established by its real-host qualification record. This tool identifies settings that should be verified through real-host captures, but it does not model exciter, STFT, limiter, or music-program behavior.

To investigate whether the accepted host limiter participates at `.11` default
controls without creating a new DSP candidate, run a repeated same-script
limiter-threshold sweep against the registered local-material manifest:

```bash
scripts/run_jdsp_limiter_sweep.py \
  src/axiom_binaural_dsp_v4.1.4.11.eel \
  /absolute/path/to/axiom-external-cc0-manifest.json \
  /tmp/axiom-v411-limiter-sweep
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
  src/axiom_binaural_dsp_v4.1.4.11.eel \
  /absolute/path/to/axiom-external-cc0-manifest.json \
  /tmp/axiom-v411-accepted-stress
```

This renders every registered excerpt three times at the accepted host
setting. Clipping, silence, or an unrepeatable level profile fails the gate;
stable output above the `-0.50 dBFS` observation level is retained as accepted
limiter-pressure evidence for evaluating later candidates.

To identify the usable real-music range of the user-adjustable bass control,
run the accepted `.11` Sub Harmonics Gain map:

```bash
scripts/run_jdsp_sub_slider_map.py \
  src/axiom_binaural_dsp_v4.1.4.11.eel \
  /absolute/path/to/axiom-external-cc0-manifest.json \
  /tmp/axiom-v411-sub-slider-map
```

The map renders temporary external fixtures at `+4`, `+6`, `+8`, `+10`, and
`+12 dB` Sub Harmonics Gain through the accepted `-1.00 dB` host limiter
setting. An elevated-gain clipping result identifies a usable-range boundary;
it does not invalidate the accepted default baseline unless `+4 dB` itself
fails. The map also flags repeatable whole-output RMS retreat beyond `1 dB`
relative to default, since added peak reserve can trade playback loudness for
bass-control headroom.

To locate where bass weight and reserve pressure appear inside the accepted
script, run the stage observability tap runner:

```bash
scripts/run_jdsp_stage_observability.py \
  src/axiom_binaural_dsp_v4.1.4.11.eel \
  /tmp/axiom-v411-stage-observability
```

The initial `bass_reserve` mode creates temporary same-render fixtures only. It
compares `spatial_out` to `bass_post`, then `reserve_pre` to `reserve_post`,
using generated deterministic probes through the accepted host limiter policy.
The report is diagnostic evidence for the bass/host-limiter investigation; it
does not create or justify a new listening candidate by itself.

The completed `.10` stage-observability capture found additive bass behavior
where expected and exact `-1.000 dB` fixed reserve behavior at the accepted
`+4 dB` Sub Harmonics default. No bass or reserve candidate is justified from
that evidence; see
[`docs/stage-observability-v4.1.4.10.md`](docs/stage-observability-v4.1.4.10.md).

The reserve-law commands below reproduce the historical `.10` investigation
that produced `.11`. The `.10` reference law was `0.750 dB/dB`; temporary
fixtures tested lighter reserve slopes at practical elevated bass gain:

```bash
scripts/run_jdsp_reserve_law_screen.py \
  src/axiom_binaural_dsp_v4.1.4.10.eel \
  /absolute/path/to/axiom-external-cc0-manifest.json \
  /tmp/axiom-v410-reserve-screen \
  --label-regex '^(CC0 electronic outlaw high energy|CC0 instrumental hip hop high energy)$' \
  --reserve-slope 0.75 \
  --reserve-slope 0.7 \
  --reserve-slope 0.625 \
  --reserve-slope 0.5 \
  --reference-slope 0.75
```

The focused screen targets the electronic and hip-hop excerpts and tests the
accepted reserve (`0.750`) against reduced slopes. It excludes conditioning
renders before measuring each
fixture/excerpt set so newly loaded host state is not counted as repeatability
evidence. A reduced slope is viable only when every screened excerpt recovers
repeatable RMS level without clipping or exceeding the `-0.50 dBFS` peak
observation boundary. Passing this screen justifies broader qualification; it
does not create or accept a new Axiom script.

To range-qualify the slopes selected by that focused screen, test every
registered material excerpt over elevated bass settings:

```bash
scripts/run_jdsp_reserve_range_qualification.py \
  src/axiom_binaural_dsp_v4.1.4.10.eel \
  /absolute/path/to/axiom-external-cc0-manifest.json \
  /tmp/axiom-v410-reserve-range \
  --reserve-slope 0.5
```

The default qualification begins at
`+12 dB` and descending through `+10`, `+8`, and `+6 dB` only while the slope
remains safe. A verified clipping or peak-margin rejection ends that slope
immediately because it cannot qualify for the full control range. A scalar
repeatability failure receives one fresh conditioned retry before it fails the
measurement, because unstable capture evidence is not a reserve-law rejection.

The completed `.10` reserve-law investigation found `0.500 dB/dB` viable across
the full registered 14-item manifest at `+12`, `+10`, `+8`, and `+6 dB`, with
no normal-material clipped samples. Declared flawed-source clipping remains an
investigation marker, not a normal-material operating-range rejection. See
[`docs/reserve-law-screen-v4.1.4.10.md`](docs/reserve-law-screen-v4.1.4.10.md).

`src/axiom_binaural_dsp_v4.1.4.11.eel` packages that exact measured target and
is the accepted baseline after human listening acceptance against `.10`. See
[`docs/qualification-v4.1.4.11.md`](docs/qualification-v4.1.4.11.md).

### Controlled Pi Engineering Harness

The project includes a local-first Pi harness for disciplined future Axiom
experiments. It isolates the session from globally installed agent extensions,
protects the accepted `.11` file by hash and path, creates candidates in
external worktrees, serializes real-JDSP capture runs, and requires separate
human confirmations for listening acceptance, publication, and merge.

```bash
node tools/axiom-team/bin/axiom-team.mjs init
node tools/axiom-team/bin/axiom-team.mjs doctor
node tools/axiom-team/bin/axiom-team.mjs corpus-status --strict-metadata
scripts/axiom_team.sh
```

Reports, captures, candidate worktrees, and locally registered audio material
remain outside git. See [docs/engineering-harness.md](docs/engineering-harness.md)
for commands and acceptance policy.

The generated low-level exciter probe screen is available through the same
controlled harness flow as:

```bash
node tools/axiom-team/bin/axiom-team.mjs screen-exciter-probes <run-id>
```

## Quick Start: Default Slider Settings

| Slider | Parameter | Default | Range |
|--------|-----------|---------|-------|
| slider1 | Sub Harmonics Gain | 4 dB | -12 to 12 dB |
| slider2 | Global Side Width | 135% | 0 to 200% |
| slider3 | Fletcher-Munson Sensitivity | 50% | 0 to 100% |
| slider5 | Low-Mid Width Multiplier | 126% | 0 to 200% |
| slider6 | High-Frequency Width Multiplier | 110% | 0 to 150% |
| slider7 | STFT Resonance Suppression | 50% | 0 to 100% |

## Repository Structure

```
axiom-binaural-dsp/
  src/
    axiom_binaural_dsp_v4.1.4.6.eel  # Phase-preserving bass predecessor
    axiom_binaural_dsp_v4.1.4.7.eel  # Transparent-headroom comparison reference
    axiom_binaural_dsp_v4.1.4.8.eel  # Previous bass-aware headroom baseline
    axiom_binaural_dsp_v4.1.4.9.eel  # Previous reduced bass-reserve baseline
    axiom_binaural_dsp_v4.1.4.10.eel # Previous restrained low-mid width baseline
    axiom_binaural_dsp_v4.1.4.11.eel # Accepted reduced elevated-bass reserve baseline
  scripts/
    axiom_team.sh                     # Isolated Pi engineering-harness launcher
    hot_reload_liveprog.sh            # JDSP A/B preset loader
    build_android_validation_package.py # RootlessJamesDSP package/checklist builder
    build_axiom_ab_listening_package.py # Local level-matched A/B listening package builder
    build_device_readiness_package.py # Local physical-route checklist package builder
    qualify_windows_default_route.py # Windows default-output route qualification helper
    analyze_axiom_crossfeed.py        # Crossfeed transfer audit
    analyze_axiom_bass_path.py        # Removed dry-phase reconstruction audit
    generate_jdsp_stimuli.py          # Deterministic stereo capture probes
    generate_axiom_program_corpus.py  # Original deterministic bass-heavy passages
    render_jdsp_host.py               # Isolated real-JDSP WAV renderer
    compare_jdsp_captures.py          # Capture metrics and difference reports
    analyze_audio_perceptual_metrics.py # Offline loudness, transient, ERB-like, and M/S proxies
    validate_axiom_material_manifest.py # Corpus manifest metadata and coverage validator
    validate_axiom_listening_record.py # Structured listening-record validator
    validate_axiom_device_matrix.py # Local device/route matrix validator
    audit_windows_audio_endpoints.py # Windows endpoint status snapshot from WSL
    evaluate_axiom_candidate_readiness.py # Evidence-readiness gate before new candidates
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
    run_jdsp_stage_observability.py    # Same-render bass/reserve tap diagnostics
    run_jdsp_reserve_law_screen.py     # Experimental elevated-bass reserve-law screen
    run_jdsp_reserve_range_qualification.py # Reduced-reserve elevated-range qualifier
    run_jdsp_stft_audit.py         # Same-render STFT round-trip / suppression audit
    run_jdsp_width_mono_audit.py   # Accepted width / mono-compatibility audit
    run_jdsp_width_material_screen.py # Program-material spatial-balance screen
    run_jdsp_lowmid_width_screen.py # Restrained low-mid width pre-candidate screen
    run_jdsp_lowmid_width_candidate_qualification.py # Scoped low-mid candidate qualifier
    run_jdsp_high_width_screen.py # Restrained high-frequency width pre-candidate screen
    run_jdsp_exciter_sensitivity_screen.py # Dynamic exciter pre-candidate screen
    run_jdsp_exciter_probe_screen.py # Generated low-level exciter probe screen
  tests/
    test_build_axiom_ab_listening_package.py
    test_build_android_validation_package.py
    test_build_device_readiness_package.py
    test_qualify_jdsp_repeatability.py
    test_analyze_jdsp_transfer.py
    test_analyze_audio_perceptual_metrics.py
    test_validate_axiom_material_manifest.py
    test_validate_axiom_listening_record.py
    test_validate_axiom_device_matrix.py
    test_evaluate_axiom_candidate_readiness.py
    test_analyze_axiom_subharmonics.py
    test_generate_axiom_program_corpus.py
    test_generate_jdsp_stimuli.py
    test_run_jdsp_program_corpus.py
    test_run_jdsp_local_material.py
    test_run_jdsp_wsl_qualification.py
    test_run_jdsp_limiter_sweep.py
    test_run_jdsp_accepted_stress.py
    test_run_jdsp_sub_slider_map.py
    test_run_jdsp_stage_observability.py
    test_run_jdsp_reserve_law_screen.py
    test_run_jdsp_reserve_range_qualification.py
    test_run_jdsp_stft_audit.py
    test_run_jdsp_width_mono_audit.py
    test_run_jdsp_width_material_screen.py
    test_run_jdsp_lowmid_width_screen.py
    test_run_jdsp_lowmid_width_candidate_qualification.py
    test_run_jdsp_high_width_screen.py
    test_run_jdsp_exciter_sensitivity_screen.py
    test_run_jdsp_exciter_probe_screen.py
  docs/
    README.md                # Documentation index and navigation map
    current-state.md         # Accepted baseline, host policy, and state boundary
    architecture.md           # Technical architecture documentation
    axiom-roadmap.md          # 90-day foundations-first roadmap
    ab-listening-packages.md  # Local level-matched A/B listening package workflow
    android-validation.md     # RootlessJamesDSP package and validation workflow
    device-readiness-packages.md # Local physical-route checklist package workflow
    tool-inventory.md         # Script and harness command safety map
    perceptual-metrics.md     # Offline perceptual-proxy metric definitions and use
    corpus-material.md        # Material-class and failure-mode corpus taxonomy
    listening-records.md      # Structured human listening evidence format
    device-matrix.md          # Local device and route validation matrix
    candidate-readiness.md    # Baseline/corpus/device readiness gate
    bass-host-limiter-investigation-plan.md # Bass reserve and host-limiter measurement plan
    stage-observability-v4.1.4.10.md # Historical `.10` bass/reserve stage-tap evidence
    exciter-probe-screen-v4.1.4.10.md # Historical `.10` generated low-level exciter probe evidence
    qualification-v4.1.4.8.md # Previous-baseline evidence and reproduction record
    qualification-v4.1.4.9.md # Previous-baseline evidence and reproduction record
    qualification-v4.1.4.10.md # Previous accepted-baseline evidence record
    qualification-v4.1.4.11.md # Current accepted-baseline evidence record
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
| [`docs/README.md`](docs/README.md) | Documentation index and category map |
| [`docs/current-state.md`](docs/current-state.md) | Current accepted baseline, host policy, product boundary, and local-state rules |
| [`docs/axiom-roadmap.md`](docs/axiom-roadmap.md) | 90-day roadmap from the current notes and concerns |
| [`docs/ab-listening-packages.md`](docs/ab-listening-packages.md) | Level-matched local A/B listening package workflow |
| [`docs/android-validation.md`](docs/android-validation.md) | RootlessJamesDSP validation package and phone-side checklist |
| [`docs/device-readiness-packages.md`](docs/device-readiness-packages.md) | Local physical-route checklist package workflow |
| [`docs/tool-inventory.md`](docs/tool-inventory.md) | Tool purpose, JDSP side effects, and artifact safety map |
| [`docs/perceptual-metrics.md`](docs/perceptual-metrics.md) | Offline loudness, true-peak proxy, transient, ERB-like, and M/S metric scope |
| [`docs/corpus-material.md`](docs/corpus-material.md) | Material-class taxonomy and manifest coverage validation |
| [`docs/listening-records.md`](docs/listening-records.md) | Structured listening evidence format and local privacy rules |
| [`docs/device-matrix.md`](docs/device-matrix.md) | Device/route coverage matrix and crossfeed qualification rule |
| [`docs/candidate-readiness.md`](docs/candidate-readiness.md) | Baseline hash, strict corpus, and strict device readiness before new candidates |
| [`docs/architecture-decision-v4.1.4.10.md`](docs/architecture-decision-v4.1.4.10.md) | Phase 4 decision record for `.10`, `.11`, and v5 direction |
| [`docs/bass-host-limiter-investigation-plan.md`](docs/bass-host-limiter-investigation-plan.md) | Bass reserve and JDSP host-limiter investigation plan before any `.11` candidate |
| [`docs/accepted-stress-v4.1.4.10.md`](docs/accepted-stress-v4.1.4.10.md) | `.10` accepted-setting dense-material stress record |
| [`docs/sub-harmonics-map-v4.1.4.10.md`](docs/sub-harmonics-map-v4.1.4.10.md) | `.10` elevated Sub Harmonics control-range evidence |
| [`docs/reserve-law-screen-v4.1.4.10.md`](docs/reserve-law-screen-v4.1.4.10.md) | `.10` reserve-law screen and full-manifest `0.500 dB/dB` qualification |
| [`docs/stage-observability-plan.md`](docs/stage-observability-plan.md) | Diagnostic stage-tap fixture and reporting plan |
| [`docs/stage-observability-v4.1.4.10.md`](docs/stage-observability-v4.1.4.10.md) | `.10` bass/reserve stage-tap evidence and no-candidate decision |
| [`docs/JDSP4Linux_Knowledge_Base.md`](docs/JDSP4Linux_Knowledge_Base.md) | Full EEL2/JDSP runtime API reference |
| [`docs/architecture.md`](docs/architecture.md) | Current signal chain and ownership documentation |
| [`docs/qualification-v4.1.4.8.md`](docs/qualification-v4.1.4.8.md) | Previous `.8` verification record |
| [`docs/qualification-v4.1.4.9.md`](docs/qualification-v4.1.4.9.md) | Previous `.9` verification record |
| [`docs/qualification-v4.1.4.10.md`](docs/qualification-v4.1.4.10.md) | Previous accepted `.10` verification and listening record |
| [`docs/qualification-v4.1.4.11.md`](docs/qualification-v4.1.4.11.md) | Accepted `.11` reduced elevated-bass reserve record |
| [`docs/stft-audit-v4.1.4.9.md`](docs/stft-audit-v4.1.4.9.md) | Historical `.9` STFT stage investigation record |
| [`docs/width-mono-audit-v4.1.4.9.md`](docs/width-mono-audit-v4.1.4.9.md) | Historical `.9` width and mono-compatibility investigation record |
| [`docs/lowmid-width-screen-v4.1.4.9.md`](docs/lowmid-width-screen-v4.1.4.9.md) | `.9` evidence supporting the accepted `.10` width change |
| [`docs/high-width-screen-v4.1.4.10.md`](docs/high-width-screen-v4.1.4.10.md) | `.10` high-frequency width screen and no-candidate decision |
| [`docs/exciter-sensitivity-screen-v4.1.4.10.md`](docs/exciter-sensitivity-screen-v4.1.4.10.md) | `.10` dynamic exciter registered-material screen and no-candidate decision |
| [`docs/exciter-probe-screen-v4.1.4.10.md`](docs/exciter-probe-screen-v4.1.4.10.md) | `.10` generated low-level exciter probe evidence and no-candidate decision |
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
