# GitHub Copilot Instructions
# axiom-binaural-dsp — JamesDSP EEL2 DSP Project

<!-- This file is automatically loaded by GitHub Copilot as workspace context. -->

## Project Context

This is **Axiom Binaural DSP**, a 5-layer psychoacoustic audio processing suite written in **EEL2** for the **JamesDSP Linux** (JDSP4Linux) audio effects engine. The primary artifact is `src/axiom_binaural_v3.eel`.

This is NOT a web project. There is no JavaScript, Python, HTML, CSS, or build system. All code is EEL2.

---

## Language: EEL2 (JamesDSP Dialect)

EEL2 is a C-like scripting language. Key syntax:

```eel2
// Comments use C++ style
// Variables are global by default (no declaration needed)
// Sections are prefixed with @

@init      // runs once at startup
@slider    // runs when sliders change
@sample    // runs for every audio sample (hot path)
@block     // runs per audio block
```

### Arithmetic
```eel2
x = a + b;          // addition
x = a * b;          // multiplication  
x = a - b;          // subtraction
x = a / b;          // division
x = a ^ b;          // power (not ^ XOR like C)
x = sqrt(a);        // square root
x = log(a);         // natural log
x = exp(a);         // e^a
x = abs(a);         // absolute value
x = min(a, b);      // minimum
x = max(a, b);      // maximum
x = floor(a);       // floor
x = ceil(a);        // ceiling
```

### Conditionals (NO if/else keywords — use ternary)
```eel2
condition ? (true_expr) : (false_expr);

// Multi-line:
condition ? (
  a = 1;
  b = 2;
) : (
  a = 3;
  b = 4;
);
```

### Functions
```eel2
function myFunc(arg1, arg2) local(x, y) (
  x = arg1 + arg2;
  this.state = x;   // persistent instance state
  x                 // return value = last expression
);
```

### Memory Arrays
```eel2
@init
buf_size = 4096;
buf_ptr = 0;         // start address in flat memory space

@sample
buf_ptr[idx] = spl0;  // write to memory
val = buf_ptr[idx];   // read from memory
```

---

## Critical Constraints — ALWAYS Follow

### DO NOT use these (they cause mute/crash):
```eel2
$pi = 3.14;                    // ERROR: $pi is read-only
FractionalDelayLineInit(...)   // ERROR: does not exist in JDSP4Linux
idx = (idx + 1) % size;       // ERROR: % modulo not supported
```

### ALWAYS use these patterns instead:
```eel2
// Read-only constants:
$pi    // use as-is, never assign
$e     // euler's number

// Circular buffer wrapping (no modulo):
idx = idx + 1;
idx >= buf_size ? idx = 0;

// Instance state in functions:
function myFilter(x) local(y) (
  y = x - this.prev;
  this.prev = x;
  y
);
```

### spl0 / spl1 rules:
```eel2
@sample
// 1. Read inputs FIRST:
in_L = spl0;
in_R = spl1;

// 2. Process through all layers using local variables
// 3. Write outputs LAST (final two lines):
spl0 = out_L;
spl1 = out_R;
```

### Additive mixing (never overwrite mid-chain):
```eel2
// CORRECT:
out_L = dry_L + (processed_L - dry_L) * wet;

// WRONG (breaks downstream layers):
spl0 = processed_L;
```

---

## Signal Chain Order

```
Input (spl0/spl1)
  ↓
Layer 1: Virtual Sub-Bass      [in_L/R -> sub_L/R]
  ↓
Layer 2: Mid/Side Spatializer  [sub_L/R -> mid, side -> wide_L/R]
  ↓
Layer 3: Exciter + FM EQ       [wide_L/R -> ex_L/R]
  ↓
Layer 4: Haas Crossfeed        [ex_L/R -> cf_L/R]
  ↓
Layer 5: Output Limiter        [cf_L/R -> out_L/R]
  ↓
Output (spl0 = out_L; spl1 = out_R;)
```

---

## Sliders

```eel2
slider1:50<0,100,1>Wet Mix (%)
slider2:6<0,12,0.5>Sub-Bass Gain (dB)
slider3:50<0,100,1>Spatial Width (%)
slider4:30<0,100,1>Exciter Amount (%)
slider5:40<0,100,1>Crossfeed Amount (%)
slider6:-0.5<-3,0,0.1>Output Ceiling (dBFS)
```

In `@slider`: convert slider values to normalized form:
```eel2
@slider
wet       = slider1 / 100;
bass_gain = 10^(slider2 / 20);  // dB to linear
width     = slider3 / 100;
```

---

## File Structure

- `src/axiom_binaural_v3.eel` — **ONLY edit this for DSP changes**
- `presets/axiom_default.json` — JSON preset (slider values only)
- `docs/JDSP4Linux_Knowledge_Base.md` — full EEL2/JDSP API reference
- `docs/architecture.md` — DSP signal flow
- `AGENTS.md` — full agent operating guide
- `CONTRIBUTING.md` — commit and PR conventions

---

## When Copilot Suggests Code

- Always suggest EEL2 syntax, not C/C++/JS
- Use `?` ternary, not `if`/`else`
- Use `this.*` for persistent function state
- Never use `%` for modulo
- Never suggest `FractionalDelayLineInit`
- Always end `@sample` with `spl0 = out_L; spl1 = out_R;`
- Never assign to `$pi`
