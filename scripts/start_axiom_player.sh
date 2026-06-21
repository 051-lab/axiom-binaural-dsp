#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
library="${AXIOM_MUSIC_LIBRARY:-/mnt/c/Users/soloa/Music}"
host="${AXIOM_PLAYER_HOST:-127.0.0.1}"
port="${AXIOM_PLAYER_PORT:-8765}"
url="http://${host}:${port}/"

case "$host" in
  127.0.0.1|localhost)
    ;;
  ::1)
    url="http://[::1]:${port}/"
    ;;
  *)
    echo "error: AXIOM_PLAYER_HOST must be 127.0.0.1, ::1, or localhost" >&2
    exit 2
    ;;
esac

missing_commands=()
for command_name in python3 mpv ffmpeg pactl pacat jamesdsp; do
  command -v "$command_name" >/dev/null 2>&1 || missing_commands+=("$command_name")
done
if [ "${#missing_commands[@]}" -gt 0 ]; then
  echo "error: missing Axiom Player command dependencies: ${missing_commands[*]}" >&2
  exit 127
fi

python3 - <<'PY' || {
import flask
import mutagen
PY
  echo "error: missing Python dependencies; run:" >&2
  echo "  python3 -m pip install -r tools/axiom-player/requirements.txt" >&2
  exit 127
}

if [ ! -d "$library" ]; then
  echo "error: music library not found: $library" >&2
  exit 1
fi

export AXIOM_JDSP_PULSE_HIGH_PRIORITY="${AXIOM_JDSP_PULSE_HIGH_PRIORITY:-yes}"
export AXIOM_JDSP_OUTPUT_BACKEND="${AXIOM_JDSP_OUTPUT_BACKEND:-ffplay}"
export AXIOM_JDSP_START_UI="${AXIOM_JDSP_START_UI:-0}"
export AXIOM_JDSP_WARMUP_SECONDS="${AXIOM_JDSP_WARMUP_SECONDS:-20}"
export AXIOM_JDSP_FFPLAY_BUFFER_LATENCY_MSEC="${AXIOM_JDSP_FFPLAY_BUFFER_LATENCY_MSEC:-150}"
export AXIOM_PLAYER_MPV_AUDIO_BUFFER="${AXIOM_PLAYER_MPV_AUDIO_BUFFER:-0.2}"
export AXIOM_PLAYER_MPV_PULSE_BUFFER="${AXIOM_PLAYER_MPV_PULSE_BUFFER:-150}"
export AXIOM_PLAYER_MPV_DEMUXER_READAHEAD="${AXIOM_PLAYER_MPV_DEMUXER_READAHEAD:-16}"
export AXIOM_PLAYER_MPV_CACHE_SECS="${AXIOM_PLAYER_MPV_CACHE_SECS:-120}"
export AXIOM_PLAYER_LOCAL_AUDIO_CACHE="${AXIOM_PLAYER_LOCAL_AUDIO_CACHE:-1}"

"${repo_root}/scripts/start_wsl_jdsp_listening.sh"

cd "$repo_root"
python3 tools/axiom-player/axiom_player.py \
  --library "$library" \
  --host "$host" \
  --port "$port" &
server_pid="$!"

for _ in {1..60}; do
  if python3 - "$url" <<'PY' >/dev/null 2>&1
import sys
import urllib.request
urllib.request.urlopen(sys.argv[1], timeout=0.5).read(1)
PY
  then
    break
  fi
  sleep 0.25
done

cmd.exe /C start "" "$url" >/dev/null 2>&1 || true

echo "Axiom Player is running at $url"
echo "Server PID: $server_pid"
echo "Stop with: kill $server_pid"
wait "$server_pid"
