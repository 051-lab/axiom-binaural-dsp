# Axiom A/B Listening Packages

## Purpose

Future sound-changing candidates need listening evidence that is not biased by
simple loudness differences. `scripts/build_axiom_ab_listening_package.py`
creates a local A/B package from matched reference and candidate WAV folders.

The tool does not run JDSP and does not change audio content. It analyzes the
captures, creates blinded `A.wav` and `B.wav` copies, and writes recommended
playback gain values from the existing ungated loudness proxy.

## Command

```bash
scripts/build_axiom_ab_listening_package.py \
  /tmp/axiom-captures/accepted \
  /tmp/axiom-captures/candidate \
  /tmp/axiom-ab-listening-vNEXT \
  --label axiom-vNEXT-phone-listening
```

The reference and candidate folders must contain matching `.wav` filenames. The
output folder contains:

- `ab-listening-package.json`;
- `ab-listening-package.md`;
- `audio/<pair>/A.wav`;
- `audio/<pair>/B.wav`.

## Rules

- Use processed WAV captures from the same source material and route.
- Keep JDSP limiter, postgain, crossfeed, route, device, and Axiom sliders fixed
  across both versions.
- Apply the recommended playback gain for each A/B slot before judging tone,
  bass, punch, air, harshness, fatigue, or preference.
- Keep the A/B slot identity hidden until notes are complete.
- Store generated packages outside git; they may contain private material.
- Record the final result with `scripts/validate_axiom_listening_record.py`.

## Boundaries

The package uses Axiom's offline loudness proxy and true-peak proxy. These are
engineering controls, not certified loudness normalization. A package can still
require human judgment and may still need retesting if the material, playback
route, or device gain changed mid-session.
