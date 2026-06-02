# Axiom Perceptual Metrics

## Status

The first reusable offline perceptual-proxy analyzer is implemented as
`scripts/analyze_audio_perceptual_metrics.py`.

This is a measurement-foundation tool. It does not change the accepted
`v4.1.4.11` EEL script, does not touch JDSP, and does not replace listening.

## Scope

The analyzer reads a stereo PCM WAV and reports:

- ungated loudness proxy;
- combined RMS and crest factor;
- cubic-oversampled true-peak proxy;
- 20 ms envelope percentiles and transient contrast;
- mid/side RMS balance and left/right correlation;
- ERB-like band energy from sub-bass through air;
- per-band mid, side, `S/M`, and correlation context.

These are engineering proxies. They are useful for A/B direction, regression
checks, and deciding where a deeper measurement is needed. They are not
certified BS.1770 gated LUFS, certified true peak, or a psychoacoustic model of
preference.

## Command

```bash
scripts/analyze_audio_perceptual_metrics.py \
  /tmp/axiom-capture.wav \
  --label accepted-v4.1.4.11 \
  --json /tmp/axiom-capture-metrics.json \
  --markdown /tmp/axiom-capture-metrics.md
```

Generated reports should remain outside git unless a public decision document
summarizes the findings.

## Intended Use

Use this tool before a sound-changing candidate when a question is about
perceived loudness, punch, brightness, stereo spread, or tonal balance. It is
especially useful for:

- comparing accepted and candidate captures without relying only on sample
  peak or broad RMS;
- separating loudness change from spectral balance change;
- checking whether a change moves side energy, not only total level;
- spotting transient-envelope changes that can explain punch or softness;
- building summarized evidence for future candidate qualification records.

## Report Integration

The analyzer remains directly usable from the command line, and its output is
also attached to the primary report paths:

- deterministic real-host A/B summaries;
- generated program-corpus summaries;
- private local-material summaries;
- scoped low-mid candidate qualification records.

These metrics are evidence context, not an automatic approval gate. Current
pass/fail behavior still comes from existing integrity, clipping, level-margin,
and scoped-candidate checks.

The next metrics step is policy work: decide which deltas deserve warning
thresholds after enough repeated measurements exist.
