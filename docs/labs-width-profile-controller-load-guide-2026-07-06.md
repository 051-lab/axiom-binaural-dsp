# Controller Load Guide: Width-Profile Labs Fixture

Date: 2026-07-06

Related task: `AX-TASK-043`

Fixture:

```text
src/labs/axiom_binaural_dsp_v4.1.4.11_width_profile_lab.eel
```

Windows path:

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
4. In `LiveProg source`, browse to the Windows path above.
5. Start or restart the processor if it is not already processing.
6. Keep crossfeed, postgain, limiter, device, player volume, and source material
   unchanged for the whole comparison.

## Restore Accepted Axiom

Use the Controller's `Restore Axiom EEL` button or load the accepted runtime
profile after the listening pass. The accepted repo baseline remains:

```text
src/axiom_binaural_dsp_v4.1.4.11.eel
```

## Listening Reference

Use:

```text
docs/labs-width-profile-listening-target-2026-07-06.md
```

Decision options:

- `.11 preferred`;
- `width lab preferred`;
- `material dependent`;
- `no reliable difference`;
- `stop this path`.

This Labs fixture is not an accepted baseline and is not `Axiom Clean R012`.

