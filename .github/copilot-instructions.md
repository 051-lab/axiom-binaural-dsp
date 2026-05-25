# GitHub Copilot Instructions
# axiom-binaural-dsp - JamesDSP EEL2 DSP Project

## Project Context

Axiom Binaural DSP is a JamesDSP / JDSP4Linux EEL2 Liveprog enhancement core.
The accepted reference artifact is `src/axiom_binaural_dsp_v4.1.4.8.eel`.
Python and shell files in this repository provide offline analysis, real-host
capture, and preset-loading support for the EEL artifact.

The accepted script is device-neutral. It does not implement crossfeed or a
limiter. Optional crossfeed is configured in JamesDSP for headphone playback;
the qualified terminal limiter is JDSP's master limiter at `-1.00 dB`,
`60 ms` release, and `0 dB` postgain.

## Current Processing Order

```text
Input -> DC protection -> virtual sub-harmonic injection
      -> band-dependent mid-side width shaping
      -> dynamic exciter and loudness contour
      -> STFT resonance suppression
      -> fixed and bass-aware output reserve
      -> JDSP host limiter -> Output
```

## Mandatory EEL2 Rules

```eel2
// Read-only compiler constants; never assign to these.
$pi;
$e;
$eps;

// Wrap flat-buffer indices without modulo.
idx += 1;
idx >= max ? idx = 0;

// Persistent function state and declared locals.
function my_filter(x) local(y) (
  y = x - this.prev;
  this.prev = x;
  y
);

// Required final two lines of @sample.
spl0 = out_L;
spl1 = out_R;
```

- Do not use `%`, `FractionalDelayLineInit`, `pfb_init`, or
  `InitPolyphaseFilterbank`.
- Initialize every processing variable and allocated memory area in `@init`.
- Use exactly `stftCheckMemoryRequirement`, `stftInit`, `stftForward`, and
  `stftBackward` as documented in `docs/JDSP4Linux_Knowledge_Base.md`.
- Allocate STFT and analysis memory through monotonic flat-pointer arithmetic;
  never overlap blocks.
- Do not modify an accepted `.eel` artifact for a new sound change; create the
  next versioned script and compare against the accepted reference.

## Repository Conventions

- `presets/axiom-preset.conf` is a complete JDSP `audio.conf`-style key/value
  preset template, not JSON slider state.
- Generated captures, downloaded audio, private manifests, and reports remain
  outside the repository.
- Update `CHANGELOG.md` and relevant documentation after qualification or
  architectural decisions.
- Run `scripts/validate_axiom_static.sh` and the Python unit suite before
  committing relevant changes.

See `AGENTS.md`, `docs/architecture.md`, and
`docs/qualification-v4.1.4.8.md` for active engineering context.
