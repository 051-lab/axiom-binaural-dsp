# Controller Load Guide: Bass-Saturation Labs Fixture

Date: 2026-07-06

Related task: `AX-TASK-044`

Fixture:

```text
src/labs/axiom_binaural_dsp_v4.1.4.11_width_bass_saturation_lab.eel
```

Windows path:

```text
\\wsl.localhost\Ubuntu\home\soloarch\dsp-dev\axiom-binaural-dsp\src\labs\axiom_binaural_dsp_v4.1.4.11_width_bass_saturation_lab.eel
```

Comparison fixture:

```text
\\wsl.localhost\Ubuntu\home\soloarch\dsp-dev\axiom-binaural-dsp\src\labs\axiom_binaural_dsp_v4.1.4.11_width_profile_lab.eel
```

Controller executable:

```text
C:\Users\soloa\dsp-dev\external\JamesDSP4Windows_Decluttered\AxiomConsoleHarness\dist\AxiomJamesDSPController-win-x64\AxiomJamesDSPController.exe
```

## Load Steps

1. Open Axiom JamesDSP Controller.
2. Keep the same capture and processed-output route used for normal listening.
3. Go to the `Files` tab.
4. In `LiveProg source`, load the comparison fixture first if you need to reset
   your ear to the supported width result.
5. Load the bass-saturation fixture from the Windows path above.
6. Keep crossfeed, postgain, limiter, device, player volume, and source material
   unchanged for the whole comparison.

## Compare Against Width Fixture First

This pass should answer whether the bass-saturation ingredient improves the
already preferred width fixture. Do not compare directly against accepted `.11`
until you have a clear impression of the width fixture versus the
width-plus-bass fixture.

## Restore Accepted Axiom

Use the Controller's `Restore Axiom EEL` button or load the accepted runtime
profile after the listening pass. The accepted repo baseline remains:

```text
src/axiom_binaural_dsp_v4.1.4.11.eel
```

## Listening Reference

Use:

```text
docs/labs-bass-saturation-ab-sequence-2026-07-06.md
docs/labs-bass-saturation-listening-target-2026-07-06.md
```

Decision options:

- `keep`;
- `reject`;
- `material dependent`;
- `no reliable difference`.

This Labs fixture is not an accepted baseline and is not `Axiom Clean R012`.
