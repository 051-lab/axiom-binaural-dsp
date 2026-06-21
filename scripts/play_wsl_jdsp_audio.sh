#!/usr/bin/env bash
set -euo pipefail

pulse_server="${AXIOM_JDSP_PULSE_SERVER:-unix:/tmp/jdsp-win/native}"
volume=32768
latency_msec=80

usage() {
  cat <<'EOF'
Usage: scripts/play_wsl_jdsp_audio.sh [--volume 1..65536] [--latency-msec N] AUDIO_FILE

Decodes AUDIO_FILE with ffmpeg and plays it through the managed WSL JamesDSP
sink. Start the route first with scripts/start_wsl_jdsp_listening.sh.
EOF
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --volume)
      [ "$#" -ge 2 ] || { echo "error: --volume needs a value" >&2; exit 2; }
      volume="$2"
      shift 2
      ;;
    --latency-msec)
      [ "$#" -ge 2 ] || { echo "error: --latency-msec needs a value" >&2; exit 2; }
      latency_msec="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    --)
      shift
      break
      ;;
    -*)
      echo "error: unknown option: $1" >&2
      usage >&2
      exit 2
      ;;
    *)
      break
      ;;
  esac
done

[ "$#" -eq 1 ] || { usage >&2; exit 2; }
audio_file="$1"

if [[ "$audio_file" =~ ^[A-Za-z]:[/\\] ]]; then
  drive="${audio_file:0:1}"
  rest="${audio_file:2}"
  rest="${rest//\\//}"
  drive="$(printf '%s' "$drive" | tr '[:upper:]' '[:lower:]')"
  audio_file="/mnt/${drive}${rest}"
fi

if ! [[ "$volume" =~ ^[0-9]+$ ]] || [ "$volume" -lt 1 ] || [ "$volume" -gt 65536 ]; then
  echo "error: --volume must be an integer in [1, 65536]" >&2
  exit 2
fi

if ! [[ "$latency_msec" =~ ^[0-9]+$ ]] || [ "$latency_msec" -lt 10 ]; then
  echo "error: --latency-msec must be an integer >= 10" >&2
  exit 2
fi

if [ ! -f "$audio_file" ]; then
  echo "error: audio file not found: $audio_file" >&2
  exit 1
fi

for command_name in ffmpeg pacat pactl jamesdsp; do
  command -v "$command_name" >/dev/null 2>&1 || {
    echo "error: required command not found: $command_name" >&2
    exit 127
  }
done

PULSE_SERVER="$pulse_server" pactl list short sinks | grep -q '[[:space:]]JamesDSP[[:space:]]' || {
  echo "error: JamesDSP sink is not available. Run scripts/start_wsl_jdsp_listening.sh first." >&2
  exit 1
}

PULSE_SERVER="$pulse_server" jamesdsp --is-connected >/dev/null || {
  echo "error: JamesDSP service is not connected. Run scripts/start_wsl_jdsp_listening.sh first." >&2
  exit 1
}

echo "Playing through Axiom/JDSP: $audio_file"
echo "Volume: $volume / 65536"

ffmpeg \
  -hide_banner \
  -nostdin \
  -v warning \
  -i "$audio_file" \
  -vn \
  -sn \
  -dn \
  -f s16le \
  -acodec pcm_s16le \
  -ar 44100 \
  -ac 2 \
  - | PULSE_SERVER="$pulse_server" pacat \
    --playback \
    --raw \
    --device=JamesDSP \
    --format=s16le \
    --rate=44100 \
    --channels=2 \
    --volume="$volume" \
    --latency-msec="$latency_msec" \
    --client-name=AxiomWSLListening \
    --stream-name="$(basename "$audio_file")"
