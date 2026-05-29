# Axiom Perceptual Metrics

## Status

The first reusable offline perceptual-proxy analyzer is implemented as
`scripts/analyze_audio_perceptual_metrics.py`.

This is a measurement-foundation tool. It does not change the accepted
`v4.1.4.10` EEL script, does not touch JDSP, and does not replace listening.

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
  --label accepted-v4.1.4.10 \
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

## Current Boundary

The analyzer is standalone. The next metrics step is to wire its output into
candidate and corpus workflows so future reports include the same loudness,
true-peak proxy, transient, ERB-like band, and M/S context by default.
