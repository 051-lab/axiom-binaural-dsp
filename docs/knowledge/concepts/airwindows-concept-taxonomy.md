# Airwindows Concept Taxonomy

Source ID: airwindows-open-source-dsp

This taxonomy turns Airwindows into Axiom-safe retrieval vocabulary. It is a
planning aid for clean-room concept extraction, not a catalog of algorithms to
port.

## Concept Families

| Family | Axiom Use | Boundary |
| --- | --- | --- |
| nonlinear saturation and clipping | Ask whether density, edge, or harmonic texture suggests a measurable Labs fixture. | Do not copy transfer curves, constants, or implementation structure. |
| bass and low-frequency reinforcement | Frame questions around punch, blur, headroom, RMS retreat, and limiter pressure. | Do not bypass accepted Sub Harmonics gates or reserve-law evidence. |
| dynamics and envelope behavior | Design probes for transient contrast, release behavior, pumping, or level dependency. | Metrics are investigation context, not listening acceptance. |
| high-frequency air and exciter texture | Improve vocabulary for air-band benefit, harshness, de-essing, and fatigue checks. | Do not justify exciter retuning without Axiom-specific evidence. |
| spatial and utility processing | Explore Labs-only stereo questions while preserving Core device neutrality. | Do not add internal crossfeed or speaker/headphone correction to Core. |
| dithering and noise shaping | Inform future export, offline render, or quantization questions. | Live JDSP Float32 processing does not need a dither stage by default. |
| filtering and tone shaping | Generate diagnostic questions about phase, slewing, and band interaction. | EEL/JDSP constraints and existing stage ownership remain authoritative. |

## Retrieval Rules

- Query the repo-safe source note first, then the local-only Airwindows metadata
  index when effect-family context is needed.
- Return source IDs, effect names, tags, and relative upstream paths only.
- Do not return copied source text, private checkout paths, or implementation
  recipes.
- Convert every useful finding into one of: Knowledge note, Labs hypothesis,
  diagnostic fixture, rejected claim, or no action.

## Candidate Gate

Airwindows-inspired ideas follow the normal Axiom ladder:

```text
Knowledge note
  -> concept taxonomy
  -> Labs hypothesis
  -> diagnostic or temporary fixture
  -> measurement
  -> listening target
  -> candidate creation gate
```

No accepted or historical EEL file may be edited because of this taxonomy.
No `Axiom Clean R012` candidate is justified by Airwindows material alone.
