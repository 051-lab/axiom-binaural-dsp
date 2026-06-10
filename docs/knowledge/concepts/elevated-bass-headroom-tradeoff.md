# Elevated Bass Headroom Tradeoff

Type: concept note
Source IDs:

- `dafx-digital-audio-effects`
- `accurate-sound-reproduction-using-dsp`
- `spatial-hearing-revised-edition`

## Purpose

This note frames the current Sub Harmonics question as a tradeoff between added
low-end weight, terminal headroom, and perceived musical punch.

## Axiom Test-Design Use

When Sub Harmonics Gain is raised above the accepted `+4 dB` default, test
design should separate these observations:

- clipping or terminal-margin failure;
- broadband RMS or short-window RMS retreat;
- kick or transient softening;
- bass blur or low-end crowding;
- bass image detaching from the kick, vocal, or center image;
- short-session fatigue or limiter pressure;
- whether added bass weight is musically useful despite the measurable retreat.

## Axiom Questions

- Does `+10 dB` or `+12 dB` sound practically quieter after fair level handling?
- Does elevated Sub Harmonics reduce punch more than it increases useful bass
  weight?
- Is the measured RMS retreat audible only on some material classes?
- Would a future `.12` hypothesis need less reserve, different reserve timing,
  or no DSP change at all?

## Boundary

This concept helps interpret measurements and design listening tasks. It does
not justify changing the reserve law without repeatable listening evidence.
