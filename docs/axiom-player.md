# Axiom Player

## Purpose

Axiom Player is a local browser player for Windows/WSL listening through
JDSP4Linux. It uses the managed WSL JamesDSP route, plays the Windows music
library through the `JamesDSP` Pulse sink with `mpv`, and can launch the live
JamesDSP noVNC UI on demand for real-time control.

This is for casual listening and focused EEL testing. It does not replace
qualification records, Android validation, or human listening acceptance.

## Prerequisites

Required commands:

- `mpv`;
- `ffmpeg`;
- `pactl` and `pacat`;
- `jamesdsp`;
- the managed `~/.local/bin/jdsp-audio-reset` route helper.

Install the tracked Python dependencies with:

```bash
python3 -m pip install -r tools/axiom-player/requirements.txt
```

The launcher checks these requirements before changing the audio route.

## Start

From the repository root:

```bash
scripts/start_axiom_player.sh
```

The launcher:

- starts the managed WSL/JDSP route;
- loads the accepted `v4.1.4.11` script by default;
- starts the local web app at `http://127.0.0.1:8765/`;
- opens the Windows browser.

The server is intentionally loopback-only. `AXIOM_PLAYER_HOST` may be
`127.0.0.1`, `::1`, or `localhost`; network-facing binds are rejected.

The default music library is:

```text
C:\Users\soloa\Music
```

From WSL this is:

```text
/mnt/c/Users/soloa/Music
```

Override it with:

```bash
AXIOM_MUSIC_LIBRARY=/mnt/c/Users/soloa/Music scripts/start_axiom_player.sh
```

## Player Features

- album and track browsing;
- search by title, artist, album, folder, or filename;
- play, pause, seek, next, previous, and volume;
- loop A/B points for repeating a test section;
- position bookmarks stored locally;
- on-demand JamesDSP UI through noVNC;
- repo EEL script list plus optional local `.eel` path loading.

## Smooth Playback Tuning

The browser player uses `mpv` as the audio engine. The defaults favor smooth
WSL-to-Windows listening while keeping DSP-control latency low enough
for setting tests:

```text
AXIOM_JDSP_OUTPUT_BACKEND=ffplay
AXIOM_JDSP_START_UI=0
AXIOM_JDSP_WARMUP_SECONDS=20
AXIOM_JDSP_FFPLAY_BUFFER_LATENCY_MSEC=150
AXIOM_PLAYER_MPV_AUDIO_BUFFER=0.2
AXIOM_PLAYER_MPV_PULSE_BUFFER=150
AXIOM_PLAYER_MPV_DEMUXER_READAHEAD=16
AXIOM_PLAYER_MPV_CACHE_SECS=120
AXIOM_PLAYER_LOCAL_AUDIO_CACHE=1
AXIOM_JDSP_PULSE_HIGH_PRIORITY=yes
```

`AXIOM_JDSP_OUTPUT_BACKEND=ffplay` routes the processed JamesDSP output through
a direct FIFO bridge into Windows `ffplay.exe`. This is the default for setting
edits because control changes need to reach the listener quickly.

The alternatives are `AXIOM_JDSP_OUTPUT_BACKEND=ffplay-buffered` for a smoother
but much higher-latency monitor bridge and `AXIOM_JDSP_OUTPUT_BACKEND=wslg` for
WSLg PulseAudio. The WSLg path depends on WSLg/RDP audio state and may be
silent on some Windows sessions.

`AXIOM_PLAYER_LOCAL_AUDIO_CACHE=1` copies the selected track from the Windows
music library to local WSL storage before handing it to `mpv`. This avoids
real-time reads from `/mnt/c` during playback. Cached files live under:

```text
~/.local/state/axiom-engineering/player/audio-cache/
```

The JamesDSP UI is intentionally not started by default. Use `Load UI` only
while changing JamesDSP settings, then use `Unload` for critical listening. The
audio processing continues either way; unloading the VNC view removes browser
rendering load, while the default no-UI route also avoids `x11vnc`,
`websockify`, the window manager, and cursor helper during listening.

The route also plays silent audio through JamesDSP for 20 seconds after loading
the EEL script. This lets JamesDSP finish its first-play benchmark and internal
buffer refresh before music playback begins. Set `AXIOM_JDSP_WARMUP_SECONDS=0`
to skip that startup delay.

If audio still skips, increase `AXIOM_PLAYER_MPV_PULSE_BUFFER` to `250` first,
then `350` if needed, before starting the player. Larger values add control
latency but reduce underruns from Windows/WSL scheduling and audio-route
scheduling. If direct FIFO playback is still unstable, use
`AXIOM_JDSP_OUTPUT_BACKEND=ffplay-buffered` for casual listening rather than
live setting edits.

## EEL Loading

The player validates a selected `.eel` file with
`scripts/validate_axiom_static.sh` before hot-reloading it into JamesDSP. The
accepted host policy remains owned by `scripts/hot_reload_liveprog.sh`:

- limiter threshold `-1.00 dB`;
- limiter release `60 ms`;
- postgain `0 dB`;
- crossfeed disabled.

Use script switching with loop points or bookmarks to replay the same section.
V1 intentionally does not automate A/B slot switching.

## Local State

Player runtime state is local-only:

```text
~/.local/state/axiom-engineering/player/
```

Do not commit music files, local library indexes, private paths, captures, or
listening notes unless they are explicitly sanitized.

Track IDs are resolved and must remain inside the configured music library.
Symlinks or forged IDs that resolve outside that root are rejected.
