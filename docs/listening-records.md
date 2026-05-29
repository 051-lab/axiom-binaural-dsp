# Axiom Listening Records

## Purpose

Listening remains the acceptance gate for sound-changing Axiom candidates. The
test suite can show level, clipping, stage behavior, spectral movement, and
stereo balance, but it cannot decide whether a change is musically better.

Use structured listening records so acceptance decisions are reproducible
instead of being free-form chat notes.

## Privacy Boundary

Listening records may contain private song titles, timestamps, device names, or
route details. Keep full records outside public git unless they are sanitized.
Public qualification documents should summarize the decision and the non-private
evidence only.

Recommended local storage:

```bash
~/.local/state/axiom-engineering/listening-records/
```

## Required Fields

The validator expects a JSON object with:

- `schema_version: 1`;
- ISO `recorded_at`;
- listener, Axiom version, comparison version, decision, device, and route;
- JDSP limiter, postgain, and crossfeed host settings;
- all current Axiom slider values;
- one or more material entries with license/provenance scope;
- observations for bass, punch, center image, width, air, harshness, loudness,
  fatigue, artifacts, and overall judgment;
- acceptance rationale when the decision is `accept`;
- rejection rationale when the decision is `reject`.

Valid decisions are `accept`, `reject`, `needs_retest`, and `no_decision`.

## Template

```json
{
  "schema_version": 1,
  "recorded_at": "2026-05-29T18:00:00-05:00",
  "listener": "local tester",
  "axiom_version": "v4.1.4.10",
  "comparison_version": "v4.1.4.9",
  "decision": "no_decision",
  "acceptance_rationale": "",
  "rejection_rationale": "",
  "device": "Android phone, PC speakers, or headphone chain",
  "route": "RootlessJamesDSP, JDSP4Linux WSL route, wired DAC, Bluetooth, speakers, etc.",
  "host_settings": {
    "jdsp_limiter_threshold_db": -1.0,
    "jdsp_limiter_release_ms": 60.0,
    "jdsp_postgain_db": 0.0,
    "crossfeed_enabled": false
  },
  "slider_settings": {
    "sub_harmonics_gain_db": 4.0,
    "global_side_width_percent": 135.0,
    "fletcher_munson_sensitivity_percent": 50.0,
    "low_mid_width_percent": 126.0,
    "high_width_percent": 110.0,
    "stft_resonance_suppression_percent": 50.0
  },
  "material": [
    {
      "label": "private track or public test item",
      "source_type": "private_owned",
      "license_scope": "local listening only",
      "comparison_target": "v4.1.4.10 versus previous candidate",
      "timestamp_or_excerpt": "0:45-1:30",
      "notes": "Why this material was chosen and what failure mode it exposes."
    }
  ],
  "observations": {
    "bass": "",
    "punch": "",
    "center_image": "",
    "width": "",
    "air": "",
    "harshness": "",
    "loudness": "",
    "fatigue": "",
    "artifacts": "",
    "overall": ""
  }
}
```

## Validation

```bash
scripts/validate_axiom_listening_record.py \
  ~/.local/state/axiom-engineering/listening-records/v4.1.4.10-phone.json \
  --json /tmp/axiom-listening-validation.json \
  --markdown /tmp/axiom-listening-record.md
```

The validator checks structure and required fields. It does not decide whether
the listening conclusion is correct.

## Source Types

Use one of these source types per material item:

- `private_owned`: personal library material, local record only;
- `streamed_reference`: streamed or subscription material, local record only;
- `cc0`: public-domain or CC0 material that can be referenced publicly;
- `generated`: in-repository or locally generated test material;
- `unknown`: allowed only for rough notes, not public qualification evidence.
