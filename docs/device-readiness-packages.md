# Axiom Device Readiness Packages

## Purpose

Device readiness packages turn the local device matrix into a route-by-route
checklist. They are for local evidence collection before candidate readiness;
they do not certify sound quality and do not modify DSP.

Use them when `scripts/evaluate_axiom_candidate_readiness.py` is blocked by
`device_matrix_strict`.

## Command

```bash
scripts/build_device_readiness_package.py \
  src/axiom_binaural_dsp_v4.1.4.10.eel \
  /tmp/axiom-device-readiness \
  --device-matrix ~/.local/state/axiom-engineering/device-matrix.json
```

The output folder contains:

- `manifest.json`;
- `device-readiness-checklist.md`.

The command exits `0` only when the device matrix already passes strict
coverage and strict setup. It still writes the package when readiness is
blocked so the remaining actions are explicit.

## What It Checks

For every route in the matrix, the package records:

- device class and output label;
- availability and qualification eligibility;
- crossfeed policy;
- script hash confirmation status;
- host-setting confirmation status;
- route-stability status;
- reboot or reconnect persistence status;
- remaining checklist actions.

Generated packages can include private device names and should stay outside the
repository unless sanitized.
