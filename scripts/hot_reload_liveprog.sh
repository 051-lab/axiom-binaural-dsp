#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
script_path="${1:-$repo_root/src/axiom_binaural_dsp_v4.1.4.1.eel}"
preset_name="${2:-Axiom-v5}"
liveprog_link="${HOME}/.config/jamesdsp/liveprog/axiom_current.eel"

if ! command -v jamesdsp >/dev/null 2>&1; then
  echo "error: jamesdsp CLI not found in PATH" >&2
  exit 127
fi

if [ ! -f "$script_path" ]; then
  echo "error: EEL script not found: $script_path" >&2
  exit 1
fi

mkdir -p "$(dirname "$liveprog_link")"
ln -sf "$script_path" "$liveprog_link"

jamesdsp --set liveprog_enable=true
jamesdsp --set liveprog_file="$script_path"
jamesdsp --save-preset "$preset_name"

echo "Liveprog hot-reloaded:"
jamesdsp --get liveprog_enable
jamesdsp --get liveprog_file
echo "Preset saved: $preset_name"
