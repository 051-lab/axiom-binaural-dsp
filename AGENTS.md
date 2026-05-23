# AGENTS.md — AI Agent Operating Instructions

> **axiom-binaural-dsp** | JamesDSP Linux / JDSP4Linux 5-Layer Binaural DSP Suite

This file defines how AI agents (GitHub Copilot, Claude, Qwen, ChatGPT, Cursor, etc.) should understand and contribute to this repository. Read this file **before** making any changes.

---

## Repository Overview

| Item | Detail |
|------|--------|
| **Project** | Axiom Binaural DSP — 5-layer audio effects suite |
| **Runtime** | JamesDSP Linux (JDSP4Linux) EEL2 scripting engine |
| **Language** | EEL2 (JamesDSP dialect) |
| **Target** | Linux desktop audio via PipeWire / PulseAudio |
| **Version** | v3.0 stable |

---

## Directory Structure

```
axiom-binaural-dsp/
├── AGENTS.md                  <- YOU ARE HERE — read before editing
├── CONTRIBUTING.md            <- Contribution workflow
├── README.md                  <- Project overview
├── CHANGELOG.md               <- Version history
├── .github/
│   └── copilot-instructions.md  <- Copilot-specific context
├── src/
│   └── axiom_binaural_v3.eel  <- MAIN EEL2 SCRIPT (primary artifact)
├── presets/
│   └── axiom_default.json     <- Default preset values
└── docs/
    ├── JDSP4Linux_Knowledge_Base.md  <- Full EEL2/JDSP runtime reference
    └── architecture.md        <- 5-layer DSP architecture documentation
```

---

## Primary Artifact

`src/axiom_binaural_v3.eel` is the main deliverable. All DSP logic lives here.

### 5-Layer Architecture (in order)

| Layer | Name | Purpose |
|-------|------|---------|
| 1 | Virtual Sub-Bass | Harmonic synthesis for bass extension |
| 2 | Mid/Side Spatializer | M/S encode/decode for stereo width |
| 3 | Dynamic Exciter + Fletcher-Munson EQ | Perceptual loudness compensation |
| 4 | Haas / Crossfeed Matrix | Binaural crossfeed for headphone imaging |
| 5 | Output Limiter | Peak limiting, final spl0/spl1 write-back |

---

## CRITICAL EEL2 Constraints — NEVER Violate These

The JDSP4Linux EEL2 engine has strict runtime rules. Violating them causes **silent output (mute), crashes, or undefined behavior**.

### 1. Reserved Variables — READ ONLY
```eel2
// NEVER assign to these:
$pi   // mathematical constant — read only
spl0  // input left  — read at @sample start, write at @sample END only
spl1  // input right — read at @sample start, write at @sample END only
```

### 2. Delay Buffers — Manual Circular Buffers ONLY
```eel2
// CORRECT — raw memory buffer with manual index wrapping:
buf_L[buf_idx] = spl0;
buf_idx = buf_idx + 1;
buf_idx >= BUF_SIZE ? buf_idx = 0;

// WRONG — FractionalDelayLineInit does NOT exist in JDSP4Linux:
// FractionalDelayLineInit(...)  <-- DO NOT USE
```

### 3. No Modulo Operator
```eel2
// WRONG:
idx = (idx + 1) % BUF_SIZE;

// CORRECT:
idx = idx + 1;
idx >= BUF_SIZE ? idx = 0;
```

### 4. Instance Variables in Functions
```eel2
// All persistent state inside function() blocks MUST use this.*:
function myFunc() local(x) (
  this.state += x;   // CORRECT
  state += x;        // WRONG — not persistent across calls
);
```

### 5. Additive Mixing — Never Replace
```eel2
// CORRECT — additive mix:
out_L = dry_L * (1 - wet) + processed_L * wet;
out_R = dry_R * (1 - wet) + processed_R * wet;

// WRONG — replacing spl0/spl1 mid-chain kills downstream layers:
spl0 = processed_L;  // DO NOT do this mid-chain
```

### 6. Final spl0/spl1 Write-Back — Required Last Lines of @sample
```eel2
// The LAST two lines of every @sample block MUST be:
spl0 = out_L;
spl1 = out_R;
```

### 7. Initialize All Variables in @init
```eel2
@init
// Every slider variable, buffer size, and state variable
// MUST be initialized here before use in @sample or @slider.
wet = slider1 / 100;
bass_gain = slider2 / 100;
// etc.
```

---

## Slider Conventions

```eel2
slider1:50<0,100,1>Wet Mix (%)
slider2:6<0,12,0.5>Sub-Bass Gain (dB)
slider3:50<0,100,1>Spatial Width (%)
slider4:30<0,100,1>Exciter Amount (%)
slider5:40<0,100,1>Crossfeed Amount (%)
slider6:-0.5<-3,0,0.1>Output Ceiling (dBFS)
```

---

## File Editing Rules for Agents

1. **Only edit `src/axiom_binaural_v3.eel`** for DSP logic changes.
2. **Update `CHANGELOG.md`** with every meaningful change using semver.
3. **Do not** rename the main EEL file — JDSP loads it by exact filename.
4. **Do not** add `npm`, `pip`, `cargo`, or other package managers — this is a pure EEL2 project with no build system.
5. **Do not** split the EEL script into multiple files — JDSP loads a single `.eel` file.
6. **Presets** in `presets/` are JSON; valid fields are slider key/value pairs only.
7. **Docs** in `docs/` are Markdown reference material — update if architecture changes.

---

## Reference Documents

| Document | Purpose |
|----------|---------|
| `docs/JDSP4Linux_Knowledge_Base.md` | Complete EEL2 syntax, JDSP API, all sections/blocks reference |
| `docs/architecture.md` | 5-layer DSP signal flow diagram and algorithm details |
| `CONTRIBUTING.md` | Commit conventions, PR process, testing checklist |
| `.github/copilot-instructions.md` | Copilot-specific inline coding context |

---

## Testing

JDSP4Linux has no unit test framework. Validation is done by:

1. Loading the `.eel` file in JamesDSP Linux.
2. Playing audio and verifying:
   - No silence / muted output
   - No clipping on loud transients
   - Stereo field is widened but not phase-inverted
   - Sub-bass is audible on headphones
   - Crossfeed effect is perceptible
3. Checking CPU usage stays below 5% on typical hardware.

---

## Commit Message Convention

```
type(scope): short description

Types: feat | fix | docs | refactor | perf | chore
Scopes: dsp | layer1 | layer2 | layer3 | layer4 | layer5 | preset | docs | ci

Examples:
feat(layer2): increase M/S spatial width range to 200%
fix(layer5): prevent limiter from zeroing spl0/spl1 prematurely
docs(agents): update EEL2 constraint examples
```

---

*Last updated: v3.0 — maintained by 051-lab*
