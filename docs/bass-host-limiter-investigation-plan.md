# Axiom Bass and Host Limiter Investigation Plan

This plan defines the next evidence-gathering pass for the accepted Axiom Clean
baseline, `src/axiom_binaural_dsp_v4.1.4.10.eel`. It is intentionally a
measurement and listening plan, not a candidate plan. No `.11` script should be
created from bass or limiter assumptions until this investigation produces a
clear failure, opportunity, or "do not change" result.

## Current Baseline

Accepted DSP:

```text
src/axiom_binaural_dsp_v4.1.4.10.eel
sha256: 2b72288048f3e6a180eb5a0e3d951f34fc463d113bb8d716c03cfda8aeafffc5
```

Host policy for qualification:

```text
JDSP limiter: enabled
threshold: -1.00 dB
release: 60 ms
postgain: 0.00 dB
crossfeed: disabled
```

The host limiter remains part of the current accepted playback contract. This
investigation is meant to understand that contract, not remove it casually.

## Background

Version `.8` added bass-aware terminal reserve above the default Sub Harmonics
Gain value. It preserved the accepted `.7` default behavior at `+4 dB`, while
preventing elevated bass settings from exceeding the target ceiling on dense
material.

Version `.8` also exposed the main weakness in the reserve law: as Sub
Harmonics Gain rose, RMS level retreated on dense excerpts even though clipping
remained controlled. The strongest measured retreat happened at `+8 dB` through
`+12 dB`.

Version `.9` reduced the elevated bass reserve slope to `0.750 dB/dB`. That
recovered roughly `0.86 dB` to `0.97 dB` of RMS on the critical `+8 dB`
electronic and hip-hop excerpts without crossing the `-0.50 dBFS` candidate
boundary. It became the accepted bass/reserve behavior.

Version `.10` changed only the low-mid width default, from `140%` to `126%`.
It inherited the accepted `.9` bass/reserve law unchanged.

The remaining unresolved signal is that some dense material can sit close to
the ceiling at default settings. The `.9` qualification treated this as
existing host-limiter participation rather than a new DSP regression because
the behavior matched `.8`.

## Primary Question

Does the accepted `.10` bass/reserve law preserve perceived punch, density, and
loudness across elevated Sub Harmonics Gain settings, or does the interaction
between internal reserve and the JDSP host limiter create avoidable level
retreat?

The question must be answered with repeatable captures, corpus coverage, and
human listening notes. A single attractive metric is not enough to justify
changing the accepted DSP.

## Non-Goals

- Do not edit `src/axiom_binaural_dsp_v4.1.4.10.eel`.
- Do not create a `.11` candidate during this investigation.
- Do not change the accepted host limiter policy without a separate host policy
  review.
- Do not use crossfeed during qualification captures.
- Do not commit rendered audio, private material manifests, or machine-specific
  capture paths.
- Do not optimize for loudness alone. Bass extension, transient shape, stereo
  stability, and fatigue risk matter.

## Investigation Stages

### 1. Accepted Baseline Stress

Run the accepted stress harness against `.10` at default controls:

```bash
python3 scripts/run_jdsp_accepted_stress.py
```

Purpose:

- Confirm `.10` still behaves as the accepted baseline after any environment or
  corpus changes.
- Reconfirm no silence, clipping, unstable routing, or unexpected level drift.
- Establish the current baseline report before any focused bass work.

Required result:

- Capture integrity passes.
- Repeatability remains within the existing accepted tolerance.
- Any near-ceiling result is labeled as host-contract behavior until proven
  otherwise.

### 2. Sub Harmonics Slider Map

Run the Sub Harmonics Gain map on `.10`:

```bash
python3 scripts/run_jdsp_sub_slider_map.py
```

Minimum slider points:

```text
+4 dB, +6 dB, +8 dB, +10 dB, +12 dB
```

Purpose:

- Rebuild the `.8` and `.9` bass evidence on the current accepted `.10` script.
- Measure whether elevated bass settings still trade too much loudness or punch
  for headroom.
- Identify the material and slider positions that deserve focused limiter and
  stage-observability work.

Required metrics:

- Per-channel peak dBFS.
- Clipped sample count.
- RMS dBFS.
- Crest factor.
- 20 ms envelope peak and percentile.
- Low-band and low-mid-band energy.
- Mid/Side balance.
- Per-excerpt pass, warning, or investigation status.

### 3. Host Limiter Threshold Sweep

Run the limiter sweep only on excerpts flagged by the accepted stress or slider
map:

```bash
python3 scripts/run_jdsp_limiter_sweep.py
```

Suggested threshold points:

```text
-0.50 dB, -1.00 dB, -3.00 dB
```

Purpose:

- Separate internal DSP behavior from host-limiter behavior.
- Determine whether close-to-ceiling captures are being audibly shaped by the
  host limiter.
- Identify whether the accepted `-1.00 dB` host threshold is a stable policy or
  a hidden tuning dependency.

Decision bias:

- Keep `-1.00 dB` as the default host policy unless the sweep shows a repeatable
  quality or stability problem.
- Do not use a lower host threshold as a workaround for an internal gain-stage
  problem.

### 4. Stage Observability Capture

After `scripts/run_jdsp_stage_observability.py` exists, run its first
`bass_reserve` mode on the same flagged excerpts.

Target taps:

```text
dc_input
bass_harmonic
bass_post
reserve_pre
reserve_post
```

Purpose:

- Measure where the gain law is actually changing the signal.
- Compare bass-generation behavior against terminal reserve behavior.
- Determine whether reserve is controlling true excess energy or reducing
  usable punch before the host limiter would need to work.

Required output:

- Accepted script path and hash.
- Temporary fixture path and hash.
- Host policy.
- Material label.
- Tap integrity result.
- Peak, RMS, crest, 20 ms envelope, band energy, and M/S metrics per tap.
- Stage deltas between bass and reserve taps.

### 5. Temporary Reserve-Law Screen

Only run this stage if the previous stages show a repeatable opportunity.

Existing tools:

```bash
python3 scripts/run_jdsp_reserve_law_screen.py
python3 scripts/run_jdsp_reserve_range_qualification.py
```

Candidate slopes may include:

```text
0.625 dB/dB
0.700 dB/dB
0.750 dB/dB
0.875 dB/dB
1.000 dB/dB
```

Purpose:

- Test whether the accepted `0.750 dB/dB` slope is still the best compromise.
- Avoid creating a permanent `.11` file until a temporary fixture proves a
  better law across the full slider range.

Required result before any candidate:

- At least `0.50 dB` repeatable recovery in RMS or 20 ms envelope on the
  critical excerpts.
- No peak above the `-0.50 dBFS` candidate boundary.
- No clipped samples.
- No new M/S instability.
- No audible bass smear, pumping, harshness, or stereo collapse in listening
  notes.

## Corpus Requirements

Use only legal material. Public or generated material may be registered through
the repo tooling, but rendered audio and private manifests stay outside git.

Minimum useful coverage:

- High-energy electronic or EDM.
- Trap or hip-hop with strong 808 content.
- Dense modern pop.
- Rock or metal with sustained bass guitar and kick overlap.
- Jazz or acoustic upright bass.
- Orchestral or cinematic low-frequency swells.
- Low-level dynamic material where over-reserve would be obvious.

The key requirement is not genre count. The corpus must contain material that
can reveal bass reserve failures, host-limiter dependency, stereo instability,
and loudness retreat.

## Metrics and Interpretation

Hard failure:

- Silence or invalid capture.
- Any clipped sample in accepted baseline qualification.
- Non-repeatable routing or capture results.
- Output assignment or syntax violation in any temporary fixture.

Investigation warning:

- Default accepted `.10` output exceeds the `-0.50 dBFS` candidate boundary but
  does not clip.
- Host limiter threshold changes produce large RMS or envelope differences on
  the same excerpt.
- Elevated bass settings lose more than `1.0 dB` RMS or 20 ms envelope compared
  with default without a corresponding reduction in peak risk.
- M/S ratio shifts enough to imply stereo image instability.

No-change result:

- `.10` remains repeatable and safe.
- Elevated bass behavior stays within useful loudness and envelope limits.
- Limiter threshold sweep shows the accepted host limiter is not doing
  excessive corrective work.
- Listening notes prefer the accepted balance over all temporary reserve-law
  alternatives.

Candidate-worthy result:

- A temporary reserve law improves critical excerpts by at least `0.50 dB` in
  repeatable RMS or 20 ms envelope.
- Peaks remain below `-0.50 dBFS`.
- Clipping remains zero.
- The improvement survives the full slider range and corpus screen.
- Human listening confirms better punch or density without added fatigue.

## Deliverables

Committed to repo:

- This investigation plan.
- Future runner code when implemented.
- Future summary reports that contain only aggregate metrics and legal metadata.

Kept outside git:

- Rendered audio captures.
- Private corpus manifests.
- Machine-specific paths.
- Temporary diagnostic EEL fixtures unless promoted into a reviewed tool.

## Exit Criteria

This investigation is complete when one of these decisions can be made with
evidence:

1. Keep `.10` unchanged and document why the bass/host-limiter contract is
   acceptable.
2. Create a narrowly scoped `.11` candidate with a measured bass/reserve target.
3. Stop candidate work and improve tooling or corpus coverage first because the
   current evidence is not strong enough.

