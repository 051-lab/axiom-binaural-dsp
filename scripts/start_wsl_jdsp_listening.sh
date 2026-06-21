#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
route_helper="${AXIOM_JDSP_ROUTE_HELPER:-${HOME}/.local/bin/jdsp-audio-reset}"
pulse_server="${AXIOM_JDSP_PULSE_SERVER:-unix:/tmp/jdsp-win/native}"
accepted_eel="${1:-${repo_root}/src/axiom_binaural_dsp_v4.1.4.11.eel}"
preset_name="${2:-Axiom-v4.1.4.11-WSL-listening}"
start_ui="${AXIOM_JDSP_START_UI:-0}"
warmup_seconds="${AXIOM_JDSP_WARMUP_SECONDS:-20}"

if [ ! -x "$route_helper" ]; then
  echo "error: route helper not executable: $route_helper" >&2
  exit 1
fi

if [ ! -f "$accepted_eel" ]; then
  echo "error: EEL script not found: $accepted_eel" >&2
  exit 1
fi

"$route_helper"

PULSE_SERVER="$pulse_server" pactl list short sinks | grep -q '[[:space:]]JamesDSP[[:space:]]' || {
  echo "error: JamesDSP sink is not available on $pulse_server" >&2
  exit 1
}

PULSE_SERVER="$pulse_server" jamesdsp --is-connected >/dev/null
"${repo_root}/scripts/hot_reload_liveprog.sh" "$accepted_eel" "$preset_name"

if [[ "$warmup_seconds" != "0" && "$warmup_seconds" != "false" && "$warmup_seconds" != "no" && "$warmup_seconds" != "off" ]]; then
  echo "Warming JamesDSP for ${warmup_seconds}s with silent audio..."
  PULSE_SERVER="$pulse_server" timeout "${warmup_seconds}s" pacat \
    --playback \
    --device=JamesDSP \
    --raw \
    --format=s16le \
    --rate=44100 \
    --channels=2 \
    --latency-msec="${AXIOM_PLAYER_MPV_PULSE_BUFFER:-150}" \
    /dev/zero >/dev/null 2>&1 || true
fi

echo
echo "Axiom WSL/JDSP listening route is ready."
echo "Pulse server: $pulse_server"
if [[ "$start_ui" != "0" && "$start_ui" != "false" && "$start_ui" != "no" && "$start_ui" != "off" ]]; then
  echo "JamesDSP UI: $(cat /tmp/jdsp-win/novnc-url.txt 2>/dev/null || printf 'http://127.0.0.1:6080/vnc.html?autoconnect=true&resize=scale&host=127.0.0.1&port=6080')"
else
  echo "JamesDSP UI: not started; use the Axiom Player Load UI button when needed."
fi
echo
echo "Play an audio file through Axiom/JDSP:"
echo "  scripts/play_wsl_jdsp_audio.sh \"C:/path/to/audio.wav\""
echo
echo "Stop the route and restore normal WSL audio:"
echo "  scripts/stop_wsl_jdsp_listening.sh"
