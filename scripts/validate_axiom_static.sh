#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
script_path="${1:-$repo_root/src/axiom_binaural_dsp_v4.1.4.2.eel}"
failures=0

fail() {
  echo "FAIL: $*"
  failures=$((failures + 1))
}

pass() {
  echo "PASS: $*"
}

if [ ! -f "$script_path" ]; then
  echo "error: EEL script not found: $script_path" >&2
  exit 1
fi

if grep -Eq '\$(pi|PI|e|E|eps|EPS)[[:space:]]*=' "$script_path"; then
  fail "reserved EEL constants are assigned"
else
  pass "reserved constants are read-only"
fi

if grep -Eq 'FractionalDelayLineInit|pfb_init|InitPolyphaseFilterbank' "$script_path"; then
  fail "forbidden JDSP crash-prone API found"
else
  pass "forbidden JDSP APIs absent"
fi

if sed 's://.*$::' "$script_path" | grep -Ev '^[[:space:]]*slider[0-9]+:' | grep -Eq '%'; then
  fail "possible modulo operator found outside slider declarations"
else
  pass "no executable modulo operator found"
fi

if ! grep -q '^@init' "$script_path"; then
  fail "@init block missing"
else
  pass "@init block present"
fi

if ! grep -q '^@sample' "$script_path"; then
  fail "@sample block missing"
else
  pass "@sample block present"
fi

last_two="$(grep -Ev '^[[:space:]]*(//|$)' "$script_path" | tail -n 2)"
if [ "$last_two" = $'spl0 = out_L;\nspl1 = out_R;' ]; then
  pass "final @sample write-back lines are correct"
else
  fail "final executable lines are not spl0/spl1 write-back"
fi

if grep -q 'loop((binEnd - binStart) \\* 2' "$script_path"; then
  fail "STFT bin loop double-count regression found"
else
  pass "STFT bin loop bounds are not double-counted"
fi

if grep -q 'bandEnergy += (stftInL\\[i\\]\\*stftInL\\[i\\] + stftInL\\[i+1\\]\\*stftInL\\[i+1\\])' "$script_path"; then
  fail "left-only STFT band energy regression found"
else
  pass "STFT band energy is not left-only legacy form"
fi

if ! grep -q 'dc_block_l.HighPassFilter_Set' "$script_path"; then
  fail "input DC blocker init missing"
else
  pass "input DC blocker init present"
fi

if ! grep -q 'stftOutL\[stftBufPos\] = 0.0' "$script_path"; then
  fail "STFT output clear-after-read missing"
else
  pass "STFT output clear-after-read present"
fi

if grep -Eq 'Perfect|perfect|Mathematically perfect' "$script_path"; then
  fail "unverified perfection claim remains in comments"
else
  pass "unverified perfection claims absent"
fi

if [ "$failures" -gt 0 ]; then
  echo "Static validation failed with $failures issue(s): $script_path"
  exit 1
fi

echo "Static validation passed: $script_path"
