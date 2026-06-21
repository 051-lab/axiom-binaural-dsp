# WSL JamesDSP Listening Route

## Purpose

This workflow lets a Windows user listen to Axiom through JDSP4Linux from WSL.
It starts a private PulseAudio route in WSL, sends the processed audio to the
Windows default output through a buffered Windows `ffplay.exe` bridge by
default. The JamesDSP noVNC UI is optional so critical listening can run with
less background load.

This is a local listening environment. It is not a replacement for structured
qualification, Android/RootlessJamesDSP listening, or final human acceptance.

## Start The Route

From the repository root:

```bash
scripts/start_wsl_jdsp_listening.sh
```

The start command:

- starts the managed private Pulse server at `unix:/tmp/jdsp-win/native`;
- exposes a `JamesDSP` sink;
- exposes `WinSink` as a buffered Windows output bridge;
- loads `src/axiom_binaural_dsp_v4.1.4.11.eel`;
- applies the accepted host policy: limiter `-1.00 dB`, release `60 ms`,
  postgain `0 dB`, crossfeed disabled;
- warms JamesDSP with silent audio for 20 seconds so first-play initialization
  does not happen during the first music track;
- leaves the JamesDSP noVNC UI stopped unless `AXIOM_JDSP_START_UI=1` is set.

To start with the UI already running:

```bash
AXIOM_JDSP_START_UI=1 scripts/start_wsl_jdsp_listening.sh
```

The WSLg tunnel backend is also available:

```bash
AXIOM_JDSP_OUTPUT_BACKEND=wslg scripts/start_wsl_jdsp_listening.sh
```

Use the WSLg backend only after confirming it is audible on the current Windows
session. The default stays on `ffplay-buffered` because it keeps the reliable
Windows bridge but adds buffering before the interop handoff.

For diagnosis, the older direct FIFO bridge is available with:

```bash
AXIOM_JDSP_OUTPUT_BACKEND=ffplay scripts/start_wsl_jdsp_listening.sh
```

## Play Audio Through Axiom/JDSP

Use:

```bash
scripts/play_wsl_jdsp_audio.sh "C:/Users/soloa/Music/example.wav"
```

The player accepts normal Windows-style paths such as `C:/...` or WSL paths
such as `/mnt/c/...`. It uses `ffmpeg` to decode the file, then streams 44.1 kHz
stereo PCM to the managed `JamesDSP` sink.

For quieter playback:

```bash
scripts/play_wsl_jdsp_audio.sh --volume 22000 "C:/Users/soloa/Music/example.wav"
```

Volume is PulseAudio linear volume in the range `1..65536`; `32768` is the
default.

## Use The Existing Music Library

The default local music library is:

```text
C:\Users\soloa\Music
```

From WSL, that same folder is:

```text
/mnt/c/Users/soloa/Music
```

List album folders:

```bash
scripts/axiom_music_library.sh albums
```

List tracks:

```bash
scripts/axiom_music_library.sh tracks
```

Filter tracks:

```bash
scripts/axiom_music_library.sh tracks emotions
```

Play a single matching track through Axiom/JDSP:

```bash
scripts/axiom_music_library.sh play "Electric Feel"
```

If the filter matches multiple tracks, the script prints the matches and asks
for a more specific filter.

For a full browser player with library browsing, queue controls, loop points,
EEL script loading, and an embedded JamesDSP UI, use:

```bash
scripts/start_axiom_player.sh
```

## Stop The Route

When done:

```bash
scripts/stop_wsl_jdsp_listening.sh
```

The stop command shuts down the private JDSP route and attempts to restore the
normal WSLg PulseAudio route at `unix:/mnt/wslg/PulseServer`.

## Listening Notes

- Keep Windows volume moderate before starting playback.
- Use this route for informal Axiom/JDSP listening and comparison checks.
- For qualification-grade evidence, keep using the existing Pi/JDSP harness and
  structured listening records.
- If headphone crossfeed is enabled manually in JamesDSP, record that separately
  because it is outside the measured Axiom Core baseline.
