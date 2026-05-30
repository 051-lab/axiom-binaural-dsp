# Axiom Device Matrix

## Purpose

Axiom needs separate lab and field evidence. The device matrix records which
routes are available, which ones are allowed for qualification, and which setup
checks have actually been completed.

Use `scripts/validate_axiom_device_matrix.py` for local validation. Full device
matrices can contain private device names and routes, so keep them outside
public git unless sanitized.

Recommended local storage:

```bash
~/.local/state/axiom-engineering/device-matrix.json
```

## Required Device Classes

The strict matrix expects at least one available entry for:

- `primary_android`: RootlessJamesDSP phone validation;
- `speaker_path`: real speaker listening path;
- `wired_or_usb`: wired headphone, USB DAC, or USB-C route;
- `bluetooth`: Bluetooth route if used by end users;
- `wsl_jdsp_lab`: WSL/JDSP lab route.

## Template

```json
{
  "schema_version": 1,
  "devices": [
    {
      "label": "Primary Android phone",
      "device_class": "primary_android",
      "platform": "Android",
      "route": "RootlessJamesDSP",
      "output_device": "wired earbuds or phone route",
      "validation_role": "primary field listening",
      "available": true,
      "qualification_allowed": true,
      "crossfeed_policy": "off_for_qualification",
      "checks": {
        "active_script_hash_verified": false,
        "host_settings_verified": false,
        "route_stability_checked": false,
        "reboot_persistence_checked": false
      }
    },
    {
      "label": "WSL JDSP lab",
      "device_class": "wsl_jdsp_lab",
      "platform": "WSL2",
      "route": "JDSP4Linux managed Pulse route",
      "output_device": "Windows output route",
      "validation_role": "measurement lab",
      "available": true,
      "qualification_allowed": true,
      "crossfeed_policy": "not_applicable",
      "checks": {
        "active_script_hash_verified": true,
        "host_settings_verified": true,
        "route_stability_checked": true,
        "reboot_persistence_checked": true
      }
    }
  ]
}
```

## Validation

```bash
scripts/validate_axiom_device_matrix.py \
  ~/.local/state/axiom-engineering/device-matrix.json \
  --strict-coverage \
  --strict-setup \
  --json /tmp/axiom-device-matrix-validation.json \
  --markdown /tmp/axiom-device-matrix-validation.md
```

Use non-strict validation while building the matrix. Use `--strict-coverage`
and `--strict-setup` before relying on device coverage for a candidate
decision. `--strict-setup` fails any available route with incomplete script
hash, host setting, route stability, or reboot persistence checks.

To snapshot Windows endpoint status from WSL before deciding whether speaker,
wired/USB, or Bluetooth routes are currently available:

```bash
scripts/audit_windows_audio_endpoints.py \
  --json /tmp/axiom-windows-audio-endpoints.json \
  --markdown /tmp/axiom-windows-audio-endpoints.md
```

Endpoint status is only a setup hint. It does not replace playback, script
hash, host setting, stability, or reboot/reconnect checks in the matrix.

To create a local route-by-route checklist package from the current matrix:

```bash
scripts/build_device_readiness_package.py \
  src/axiom_binaural_dsp_v4.1.4.10.eel \
  /tmp/axiom-device-readiness \
  --device-matrix ~/.local/state/axiom-engineering/device-matrix.json
```

See `docs/device-readiness-packages.md`.

## Crossfeed Rule

Qualification routes must use `off_for_qualification` or `not_applicable`.
Manual crossfeed checks are allowed as compatibility listening, but they are
not the measured Axiom core baseline.
