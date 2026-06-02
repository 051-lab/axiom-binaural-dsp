#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
script_path="${1:-$repo_root/src/axiom_binaural_dsp_v4.1.4.11.eel}"
liveprog_link="${HOME}/.config/jamesdsp/liveprog/axiom_current.eel"

case "$(basename "$script_path")" in
  axiom_binaural_dsp_v4.1.4.3.eel)
    default_preset_name="Axiom-v4.1.4.3-internal-limiter"
    ;;
  axiom_binaural_dsp_v4.1.4.4.eel)
    default_preset_name="Axiom-v4.1.4.4-host-limiter"
    ;;
  axiom_binaural_dsp_v4.1.4.5.eel)
    default_preset_name="Axiom-v4.1.4.5-core"
    ;;
  axiom_binaural_dsp_v4.1.4.6.eel)
    default_preset_name="Axiom-v4.1.4.6-phase-preserving-bass"
    ;;
  axiom_binaural_dsp_v4.1.4.7.eel)
    default_preset_name="Axiom-v4.1.4.7-transparent-headroom"
    ;;
  axiom_binaural_dsp_v4.1.4.8.eel)
    default_preset_name="Axiom-v4.1.4.8-previous-baseline"
    ;;
  axiom_binaural_dsp_v4.1.4.9.eel)
    default_preset_name="Axiom-v4.1.4.9-previous-baseline"
    ;;
  axiom_binaural_dsp_v4.1.4.10.eel)
    default_preset_name="Axiom-v4.1.4.10-previous-baseline"
    ;;
  axiom_binaural_dsp_v4.1.4.11.eel)
    default_preset_name="Axiom-v4.1.4.11-accepted"
    ;;
  *)
    default_preset_name="Axiom-custom"
    ;;
esac
preset_name="${2:-$default_preset_name}"
qualified_master_limthreshold="-1.0"

if ! command -v jamesdsp >/dev/null 2>&1; then
  echo "error: jamesdsp CLI not found in PATH" >&2
  exit 127
fi

if [ ! -f "$script_path" ]; then
  echo "error: EEL script not found: $script_path" >&2
  exit 1
fi

script_path="$(realpath "$script_path")"

set_config() {
  local key="$1"
  local value="$2"
  local current
  local applied

  current="$(jamesdsp --get "$key")" || {
    echo "error: unable to read JDSP key: $key" >&2
    exit 1
  }
  if [ "$current" != "$value" ]; then
    jamesdsp --set "$key=$value" >/dev/null 2>&1 || true
    applied="$(jamesdsp --get "$key")" || {
      echo "error: unable to verify JDSP key after update: $key" >&2
      exit 1
    }
    if [ "$applied" != "$value" ]; then
      echo "error: JDSP did not apply $key=$value" >&2
      exit 1
    fi
  fi
}

force_config() {
  local key="$1"
  local value="$2"
  local applied

  jamesdsp --set "$key=$value" >/dev/null 2>&1 || true
  applied="$(jamesdsp --get "$key")" || {
    echo "error: unable to verify JDSP key after reload: $key" >&2
    exit 1
  }
  if [ "$applied" != "$value" ]; then
    echo "error: JDSP did not apply $key=$value" >&2
    exit 1
  fi
}

mkdir -p "$(dirname "$liveprog_link")"
ln -sf "$script_path" "$liveprog_link"

for setting in \
  'master_enable true' \
  'tube_enable false' \
  'compander_enable false' \
  'bass_enable false' \
  'graphiceq_enable false' \
  'tone_enable false' \
  'convolver_enable false' \
  'ddc_enable false' \
  'stereowide_enable false' \
  'reverb_enable false' \
  "master_limthreshold ${qualified_master_limthreshold}" \
  'master_limrelease 60' \
  'master_postgain 0'; do
  set_config "${setting%% *}" "${setting#* }"
done

# Keep the measured comparison baseline device-neutral; enable host crossfeed manually when desired.
set_config crossfeed_enable false

set_config liveprog_enable false
force_config liveprog_file "$script_path"
set_config liveprog_enable true
jamesdsp --save-preset "$preset_name" >/dev/null 2>&1 || true
if ! jamesdsp --list-presets | grep -Fxq "$preset_name"; then
  echo "error: JDSP did not save preset: $preset_name" >&2
  exit 1
fi

# JDSP4Linux currently rewrites master_limthreshold to 0 during --save-preset.
# Restore the live value and correct the saved preset so reloads keep policy.
preset_path="${HOME}/.config/jamesdsp/presets/${preset_name}.conf"
if [ -f "$preset_path" ]; then
  if grep -q '^master_limthreshold=' "$preset_path"; then
    sed -i "s/^master_limthreshold=.*/master_limthreshold=${qualified_master_limthreshold}/" "$preset_path"
  else
    printf 'master_limthreshold=%s\n' "$qualified_master_limthreshold" >> "$preset_path"
  fi
fi
force_config master_limthreshold "$qualified_master_limthreshold"

echo "Liveprog hot-reloaded with isolated JDSP baseline:"
for key in \
  liveprog_enable liveprog_file master_limthreshold master_limrelease master_postgain \
  crossfeed_enable crossfeed_mode crossfeed_bs2b_fcut crossfeed_bs2b_feed \
  stereowide_enable reverb_enable compander_enable graphiceq_enable; do
  printf '%s=' "$key"
  jamesdsp --get "$key"
done
echo "Preset saved: $preset_name"
