# Labs Listening Target: Width-Profile Isolation

Date: 2026-07-06

Related task: `AX-TASK-043`

Baseline:

- Accepted: `src/axiom_binaural_dsp_v4.1.4.11.eel`
- Labs fixture: `src/labs/axiom_binaural_dsp_v4.1.4.11_width_profile_lab.eel`

Status: Ready for controlled listening. This is not acceptance evidence for a
new baseline.

## Exact Change Under Test

Only the global side-width default changed:

```text
slider2: 135 -> 100
```

Effective default width products:

```text
Low-mid side product: 1.701 -> 1.260
High side product:    1.485 -> 1.100
```

Bass harmonic generation, exciter, STFT suppression, output reserve, crossfeed
ownership, and host limiter policy are unchanged.

## Listening Question

Does the unity-global-width Labs fixture preserve the energy and clarity of the
accepted `.11` baseline while improving image stability, reducing low-mid
spread/blur, or lowering fatigue?

## Fixed Host Conditions

Keep these unchanged for the full comparison:

- same Windows route;
- same JamesDSP terminal limiter settings;
- same postgain;
- same crossfeed state;
- same output device;
- same player volume;
- same Axiom sliders other than the fixture default under test.

If crossfeed is enabled for headphone listening, leave it enabled for both
scripts. If it is disabled, leave it disabled for both scripts.

## Suggested Material

Use short repeatable sections from:

- centered vocal or piano;
- dense electronic;
- hip-hop or kick-forward material;
- upright/electric bass material;
- bright acoustic or cymbal-heavy material.

## What To Listen For

Record whether the Labs fixture is better, worse, or same for:

- center image stability;
- vocal/kick/snare focus;
- bass staying anchored;
- low-mid width versus blur;
- high-frequency openness versus shimmer;
- perceived energy and aliveness;
- fatigue after repeats;
- whether the track feels smaller or less immersive.

## Decision Format

Use one of:

- `.11 preferred`;
- `width lab preferred`;
- `material dependent`;
- `no reliable difference`;
- `stop this path`.

Add short notes for any pumping, dullness, image drift, or fatigue. Do not
promote the fixture from Labs based on one casual pass.

Use `labs-width-profile-post-listening-decision-map-2026-07-06.md` after the
listening pass to decide whether to stop, continue Labs, or prepare a separate
candidate discussion.

## Local Record Template

Copy the template before editing it with private material details:

```bash
mkdir -p ~/.local/state/axiom-engineering/listening-records
cp docs/templates/width-profile-listening-record-2026-07-06.json \
  ~/.local/state/axiom-engineering/listening-records/width-profile-labs-2026-07-06-local.json
```

Validate the completed local record with:

```bash
scripts/validate_axiom_listening_record.py \
  ~/.local/state/axiom-engineering/listening-records/width-profile-labs-2026-07-06-local.json \
  --json /tmp/axiom-width-profile-listening-validation.json \
  --markdown /tmp/axiom-width-profile-listening-record.md
```
