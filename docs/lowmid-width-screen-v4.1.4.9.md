# v4.1.4.9 Low-Mid Width Screen

## Status

The accepted `v4.1.4.9` low-mid side width has been screened through real
JDSP capture using temporary fixtures only. The accepted EEL script was not
modified.

Harness run: `20260526T213323-determine-whether-the-ac-559f5e`

Conclusion: **a restrained listening candidate is justified**. The accepted
low-mid width product consistently exceeds source side-to-mid balance through
fundamentals, presence, and articulation in the four registered CC0 excerpts.
A restrained temporary setting reduces that emphasis modestly while retaining
capture integrity and terminal margin. The more conservative alternative is
not preferred for first listening because one dense electronic render crossed
the terminal-pressure observation boundary.

## Temporary Settings

Only `slider5`, the `150 Hz-4 kHz` width multiplier, changed in the temporary
fixtures. Global width, high-frequency width, bass generation, STFT behavior,
and terminal reserve remained accepted `.9` behavior.

| Setting | `slider5` | Effective low-mid side product | Purpose |
| --- | ---: | ---: | --- |
| Accepted | `140%` | `1.8900x` | Current baseline |
| Restrained | `126%` | `1.7010x` | Preferred first listening trial |
| Conservative | `115%` | `1.5525x` | Boundary/reference only |

## Aggregate Findings

Values below are means across the four registered excerpts.

| Band | Accepted minus source `S/M` (dB) | Restrained minus accepted (dB) | Conservative minus accepted (dB) |
| --- | ---: | ---: | ---: |
| Body, `150-300 Hz` | `+3.115` | `-0.968` | `-1.751` |
| Fundamentals, `300-800 Hz` | `+5.266` | `-0.901` | `-1.680` |
| Presence, `800 Hz-2 kHz` | `+5.426` | `-0.893` | `-1.669` |
| Articulation, `2-4 kHz` | `+5.279` | `-0.788` | `-1.481` |

The accepted presentation is consistently side-forward relative to source
material from `300 Hz` through `4 kHz`, rather than showing a genre-specific
outlier. The restrained setting does not collapse width: it removes less than
`1 dB` of side emphasis in each measured band while preserving the majority
of the accepted widening.

## Integrity Results

All renders were free of clipped PCM samples. Accepted and restrained settings
remained below the `-0.50 dBFS` observation boundary for every excerpt.

The conservative `115%` fixture produced `-0.361 dBFS` peak output on the
dense electronic excerpt, above the observation boundary. Reducing side energy
can increase coincident left/right peak concentration, so narrower spatial
settings are not automatically safer for headroom.

## Decision

Create one listening candidate based on the restrained temporary setting:

- change only the default `slider5` value from `140%` to `126%`;
- retain global width at `135%`, high-frequency width at `110%`, and all other
  accepted `.9` behavior;
- listen specifically for improved vocal and snare focus, coherent speakers,
  preserved synth immersion, and no unacceptable flattening of the accepted
  soundstage.

The candidate must be evaluated against `.9` by listening before any baseline
promotion. The conservative `115%` alternative is not advanced.
