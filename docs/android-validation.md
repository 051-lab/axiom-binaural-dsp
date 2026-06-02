# Axiom Android Validation

## Purpose

WSL/JDSP measurements are lab evidence. Android listening through
RootlessJamesDSP is field evidence. Keep those two evidence types separate.

Use `scripts/build_android_validation_package.py` to create a local package
containing the script files, SHA-256 hashes, host-setting checklist, and a
structured listening-record template.

Use `scripts/validate_axiom_device_matrix.py` and `docs/device-matrix.md` to
track which Android, speaker, wired/USB, Bluetooth, and WSL/JDSP routes are
available for validation.

## Build A Package

Accepted-baseline package:

```bash
scripts/build_android_validation_package.py \
  src/axiom_binaural_dsp_v4.1.4.11.eel \
  /tmp/axiom-android-v4.1.4.11
```

Accepted-versus-candidate package:

```bash
scripts/build_android_validation_package.py \
  src/axiom_binaural_dsp_v4.1.4.11.eel \
  /tmp/axiom-android-candidate \
  --candidate-eel src/axiom_binaural_dsp_vNEXT.eel \
  --package-name axiom-vNEXT-android-validation
```

The output folder contains:

- `manifest.json`;
- `android-validation-checklist.md`;
- `listening-record-template.json`;
- `scripts/*.eel`.

Generated packages are local artifacts. Do not commit them unless explicitly
sanitized and needed for a public release process.

## Qualification Settings

Use these settings for qualification unless a test explicitly says otherwise:

- JDSP limiter threshold: `-1.00 dB`;
- JDSP limiter release: `60 ms`;
- JDSP postgain: `0 dB`;
- JDSP crossfeed: disabled.

Crossfeed can be enabled manually for separate headphone compatibility
listening, but that result is not the measured Axiom core baseline.

## Phone-Side Checks

Before listening:

- copy the selected `.eel` file into the RootlessJamesDSP Liveprog location;
- confirm the active filename;
- compute or otherwise verify the SHA-256 against `manifest.json`;
- confirm limiter, postgain, and crossfeed settings;
- restart RootlessJamesDSP if script reload is uncertain;
- after a reboot, repeat the filename/hash check.

During listening:

- keep material order stable between accepted and candidate scripts;
- avoid changing sliders mid-pass unless the test asks for that;
- record route, output device, material, observations, and decision in the
  structured listening template;
- validate the completed record with
  `scripts/validate_axiom_listening_record.py`.

## Evidence Boundary

Android acceptance requires human listening evidence. The package builder only
reduces file and settings ambiguity; it does not certify sound quality.
