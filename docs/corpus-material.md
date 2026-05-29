# Axiom Corpus Material

## Purpose

Axiom needs a small but deliberately chosen test corpus. The goal is not a huge
music library. The goal is coverage: every item should expose a known failure
mode or musical question before a DSP candidate is proposed.

Use `scripts/validate_axiom_material_manifest.py` to check whether a local
manifest is runner-compatible and whether it carries enough metadata to explain
why each item exists.

## Privacy Boundary

Most useful music will be private or streamed. Keep source files, decoded
excerpts, and unsanitized manifests outside public git. Public docs should
summarize material classes and findings without distributing copyrighted audio
or private track names.

Recommended local storage:

```bash
~/.local/share/axiom-test-material/
```

## Material Classes

The current taxonomy is:

- `low_level_dynamic`: quiet material where gain-dependent stages should reveal
  useful behavior without being masked by limiter pressure.
- `sibilant_vocal`: exposes vocal edge, lisping, and de-essing risk.
- `cymbals_air`: exposes brilliance, air, hash, and metallic edge.
- `dense_pop_edm`: exposes modern loudness, broad-band density, and limiter
  participation.
- `hiphop_trap_sub`: exposes sustained sub pressure and kick/sub interaction.
- `rock_metal_guitars`: exposes upper-mid congestion and center image.
- `acoustic_bass`: exposes natural low-frequency envelope and pitch definition.
- `piano`: exposes transient clarity, body, and upper-harmonic harshness.
- `orchestral_crescendo`: exposes wide dynamics and complex spatial density.
- `mono_narrow`: exposes center stability and mono compatibility.
- `flawed_source`: exposes whether Axiom flatters or worsens bad masters.
- `speech`: exposes vocal naturalness and fatigue outside music.
- `bass_light`: exposes whether bass enhancement stays tasteful on thin mixes.
- `already_wide_mix`: exposes whether width processing over-expands side-heavy
  material.

## Failure Modes

Use one or more of these per item:

- `low_end_headroom`
- `sub_extension`
- `kick_bass_separation`
- `sibilance`
- `air_harshness`
- `center_image`
- `stereo_width`
- `mono_compatibility`
- `transient_punch`
- `fatigue`
- `distortion_artifacts`
- `speech_naturalness`
- `thin_source`
- `dense_mix_limiter_pressure`

## Manifest Shape

The existing render tools require `label`, `path`, `start_seconds`, and
`duration_seconds`. For decision-grade corpus work, add metadata:

```json
{
  "tracks": [
    {
      "label": "Dense electronic hook",
      "path": "/absolute/local/path/to/source.wav",
      "start_seconds": 42.0,
      "duration_seconds": 20.0,
      "material_class": "dense_pop_edm",
      "failure_modes": ["dense_mix_limiter_pressure", "air_harshness"],
      "license_scope": "private local listening only",
      "provenance": "owned local library",
      "role": "Expose terminal pressure and bright synth edge."
    }
  ]
}
```

## Validation

Runner-compatible validation:

```bash
scripts/validate_axiom_material_manifest.py \
  ~/.local/share/axiom-test-material/axiom-local-material.json \
  --json /tmp/axiom-material-validation.json \
  --markdown /tmp/axiom-material-validation.md
```

Decision-grade metadata validation:

```bash
scripts/validate_axiom_material_manifest.py \
  ~/.local/share/axiom-test-material/axiom-local-material.json \
  --strict-metadata \
  --json /tmp/axiom-material-validation.json \
  --markdown /tmp/axiom-material-validation.md
```

`PASS_WITH_WARNINGS` is expected until every desired material class and failure
mode has at least one registered item.

To create a local draft from an existing runner-compatible manifest:

```bash
scripts/validate_axiom_material_manifest.py \
  ~/.local/share/axiom-test-material/axiom-local-material.json \
  --write-metadata-template ~/.local/share/axiom-test-material/axiom-local-material.enriched.json
```

The enriched copy adds `TODO` placeholders for the decision-grade metadata
fields. Replace those placeholders locally, then rerun strict validation.
