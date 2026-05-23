# Contributing to Axiom Binaural DSP

Thank you for contributing to **axiom-binaural-dsp**. This document covers the contribution workflow for both human developers and AI agents.

> **AI agents**: Also read `AGENTS.md` and `.github/copilot-instructions.md` before making any changes.

---

## Quick Start

1. Read `AGENTS.md` — understand EEL2 constraints before touching code
2. Read `docs/JDSP4Linux_Knowledge_Base.md` — full runtime API reference
3. Read `docs/architecture.md` — 5-layer signal chain
4. Make changes in `src/axiom_binaural_v3.eel` only
5. Update `CHANGELOG.md`
6. Commit with conventional commit message

---

## What Can Be Changed

| File | Who Can Change | Notes |
|------|---------------|-------|
| `src/axiom_binaural_v3.eel` | Anyone | Primary artifact — all DSP logic |
| `presets/*.json` | Anyone | Slider value presets only |
| `docs/*.md` | Anyone | Keep in sync with code |
| `CHANGELOG.md` | Anyone | Required with every code change |
| `README.md` | Anyone | Keep accurate |
| `AGENTS.md` | Maintainer | Core operating instructions |
| `.github/copilot-instructions.md` | Maintainer | Copilot context |

---

## Commit Message Format

Use **Conventional Commits**:

```
type(scope): short description (imperative, <72 chars)

[optional body]

[optional footer]
```

### Types

| Type | When to Use |
|------|-------------|
| `feat` | New DSP feature or layer enhancement |
| `fix` | Bug fix (mute, distortion, crash) |
| `perf` | CPU/performance optimization |
| `refactor` | Code restructure without behavior change |
| `docs` | Documentation only |
| `chore` | Repo maintenance (presets, CI, etc.) |

### Scopes

```
dsp       — general DSP changes
layer1    — Virtual Sub-Bass
layer2    — Mid/Side Spatializer
layer3    — Dynamic Exciter + Fletcher-Munson EQ
layer4    — Haas Crossfeed Matrix
layer5    — Output Limiter
preset    — preset JSON files
docs      — documentation
agents    — agent configuration files
ci        — CI/CD workflows
```

### Examples

```
feat(layer1): add octave-down sub harmonic synthesis
fix(layer5): prevent limiter from muting output at threshold boundary
perf(layer2): reduce M/S matrix computation by 30%
docs(architecture): update signal flow diagram for v3.1
chore(preset): add 'Wide Stage' preset for orchestral listening
```

---

## EEL2 Code Standards

All EEL2 code in `src/axiom_binaural_v3.eel` MUST follow these rules.

### Structure

```eel2
// 1. Slider declarations at TOP
slider1:50<0,100,1>Wet Mix (%)
// ...

// 2. @init block: initialize ALL variables
@init
wet = slider1 / 100;
// ...

// 3. @slider block: update variables from slider values
@slider
wet = slider1 / 100;
// ...

// 4. @sample block: process audio
@sample
in_L = spl0;   // read inputs FIRST
in_R = spl1;
// ... layer processing ...
spl0 = out_L;  // write outputs LAST
spl1 = out_R;
```

### Naming Conventions

```eel2
// Layer intermediates: layer prefix + signal name
L1_sub_L, L1_sub_R      // Layer 1 outputs
L2_wide_L, L2_wide_R    // Layer 2 outputs
L3_ex_L, L3_ex_R        // Layer 3 outputs
L4_cf_L, L4_cf_R        // Layer 4 outputs

// Buffers: descriptive + _buf / _ptr / _idx
delay_L_buf, delay_L_idx

// Slider-derived: descriptive
wet, dry, width, bass_gain, crossfeed_amt, ceil_lin
```

### Forbidden Patterns

```eel2
$pi = anything;              // NEVER: read-only
FractionalDelayLineInit();   // NEVER: doesn't exist
(x + 1) % N;                // NEVER: no modulo
if (condition) { ... }      // NEVER: no if/else
spl0 = midchain_value;      // NEVER: mid-chain assignment
```

### Required Patterns

```eel2
// Circular buffer wrap:
idx = idx + 1;
idx >= buf_size ? idx = 0;

// Conditional:
condition ? (expr_true) : (expr_false);

// Instance state in functions:
this.state = value;   // inside function() blocks

// Final write-back (last 2 lines of @sample):
spl0 = out_L;
spl1 = out_R;
```

---

## Changelog Format

Update `CHANGELOG.md` with every code change:

```markdown
## [X.Y.Z] - YYYY-MM-DD

### Added
- Description of new feature

### Changed
- Description of changed behavior

### Fixed
- Description of bug fix

### Performance
- Description of optimization
```

---

## Testing Checklist

Before committing any DSP change, verify:

- [ ] File loads in JamesDSP Linux without errors
- [ ] Audio plays (no silent/muted output)
- [ ] No clipping on -6 dBFS test signal
- [ ] Stereo field is correct (not mono-collapsed or phase-inverted)
- [ ] All 6 sliders respond correctly
- [ ] CPU usage is reasonable (< 5% on typical hardware)
- [ ] CHANGELOG.md is updated

---

## Repository Structure Reference

```
axiom-binaural-dsp/
├── .github/
│   └── copilot-instructions.md   ← Copilot workspace context
├── docs/
│   ├── JDSP4Linux_Knowledge_Base.md  ← Full EEL2 API reference
│   └── architecture.md           ← Signal chain documentation  
├── presets/
│   └── axiom_default.json        ← Default slider preset
├── src/
│   └── axiom_binaural_v3.eel     ← PRIMARY EEL2 SCRIPT
├── AGENTS.md                     ← AI agent instructions
├── CHANGELOG.md                  ← Version history
├── CONTRIBUTING.md               ← This file
└── README.md                     ← Project overview
```

---

*Maintained by 051-lab — Axiom Binaural DSP v3.0*
