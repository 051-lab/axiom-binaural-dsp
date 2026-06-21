#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
music_root="${AXIOM_MUSIC_LIBRARY:-/mnt/c/Users/soloa/Music}"

usage() {
  cat <<'EOF'
Usage:
  scripts/axiom_music_library.sh albums
  scripts/axiom_music_library.sh tracks [FILTER]
  scripts/axiom_music_library.sh play FILTER [--volume 1..65536]

Environment:
  AXIOM_MUSIC_LIBRARY=/mnt/c/Users/soloa/Music

Examples:
  scripts/axiom_music_library.sh albums
  scripts/axiom_music_library.sh tracks emotions
  scripts/axiom_music_library.sh play "Riri"
  scripts/axiom_music_library.sh play "Electric Feel" --volume 22000
EOF
}

audio_find() {
  find "$music_root" -type f \( \
    -iname '*.wav' -o \
    -iname '*.flac' -o \
    -iname '*.mp3' -o \
    -iname '*.m4a' -o \
    -iname '*.aac' -o \
    -iname '*.ogg' -o \
    -iname '*.opus' -o \
    -iname '*.wma' \
  \)
}

require_library() {
  if [ ! -d "$music_root" ]; then
    echo "error: music library not found: $music_root" >&2
    exit 1
  fi
}

relative_path() {
  local path="$1"
  printf '%s\n' "${path#"$music_root"/}"
}

command_name="${1:-}"
[ -n "$command_name" ] || { usage >&2; exit 2; }
shift || true

require_library

case "$command_name" in
  albums)
    find "$music_root" -mindepth 1 -maxdepth 1 -type d -printf '%f\n' | sort
    ;;
  tracks)
    filter="${1:-}"
    if [ -n "$filter" ]; then
      audio_find | grep -i -- "$filter" | sort | while IFS= read -r path; do
        relative_path "$path"
      done
    else
      audio_find | sort | while IFS= read -r path; do
        relative_path "$path"
      done
    fi
    ;;
  play)
    [ "$#" -ge 1 ] || { usage >&2; exit 2; }
    filter="$1"
    shift
    volume_args=()
    if [ "$#" -gt 0 ]; then
      case "$1" in
        --volume)
          [ "$#" -eq 2 ] || { usage >&2; exit 2; }
          volume_args=(--volume "$2")
          ;;
        *)
          echo "error: unknown option: $1" >&2
          usage >&2
          exit 2
          ;;
      esac
    fi
    mapfile -t matches < <(audio_find | grep -i -- "$filter" | sort)
    if [ "${#matches[@]}" -eq 0 ]; then
      echo "error: no tracks matched: $filter" >&2
      exit 1
    fi
    if [ "${#matches[@]}" -gt 1 ]; then
      echo "error: multiple tracks matched: $filter" >&2
      printf '\nMatches:\n' >&2
      for path in "${matches[@]}"; do
        printf '  %s\n' "$(relative_path "$path")" >&2
      done
      echo >&2
      echo "Use a more specific filter." >&2
      exit 1
    fi
    exec "${repo_root}/scripts/play_wsl_jdsp_audio.sh" "${volume_args[@]}" "${matches[0]}"
    ;;
  -h|--help)
    usage
    ;;
  *)
    echo "error: unknown command: $command_name" >&2
    usage >&2
    exit 2
    ;;
esac
