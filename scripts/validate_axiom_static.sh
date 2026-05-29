#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
script_path="${1:-$repo_root/src/axiom_binaural_dsp_v4.1.4.10.eel}"
script_name="$(basename "$script_path")"
script_family="$script_name"
if [[ "$script_name" == axiom_binaural_dsp_v4.1.4.10_*.eel ]]; then
  script_family="axiom_binaural_dsp_v4.1.4.10.eel"
fi
host_limiter_only=false
host_crossfeed_only=false
phase_preserving_bass=false
failures=0

if [ "$script_family" = "axiom_binaural_dsp_v4.1.4.4.eel" ] ||
   [ "$script_family" = "axiom_binaural_dsp_v4.1.4.5.eel" ] ||
   [ "$script_family" = "axiom_binaural_dsp_v4.1.4.6.eel" ] ||
   [ "$script_family" = "axiom_binaural_dsp_v4.1.4.7.eel" ] ||
   [ "$script_family" = "axiom_binaural_dsp_v4.1.4.8.eel" ] ||
   [ "$script_family" = "axiom_binaural_dsp_v4.1.4.9.eel" ] ||
   [ "$script_family" = "axiom_binaural_dsp_v4.1.4.10.eel" ]; then
  host_limiter_only=true
fi
if [ "$script_family" = "axiom_binaural_dsp_v4.1.4.5.eel" ] ||
   [ "$script_family" = "axiom_binaural_dsp_v4.1.4.6.eel" ] ||
   [ "$script_family" = "axiom_binaural_dsp_v4.1.4.7.eel" ] ||
   [ "$script_family" = "axiom_binaural_dsp_v4.1.4.8.eel" ] ||
   [ "$script_family" = "axiom_binaural_dsp_v4.1.4.9.eel" ] ||
   [ "$script_family" = "axiom_binaural_dsp_v4.1.4.10.eel" ]; then
  host_crossfeed_only=true
fi
if [ "$script_family" = "axiom_binaural_dsp_v4.1.4.6.eel" ] ||
   [ "$script_family" = "axiom_binaural_dsp_v4.1.4.7.eel" ] ||
   [ "$script_family" = "axiom_binaural_dsp_v4.1.4.8.eel" ] ||
   [ "$script_family" = "axiom_binaural_dsp_v4.1.4.9.eel" ] ||
   [ "$script_family" = "axiom_binaural_dsp_v4.1.4.10.eel" ]; then
  phase_preserving_bass=true
fi

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

allocation_ok=true
for expected in \
  'stftStructL = ptr; ptr += memreq;' \
  'stftStructR = ptr; ptr += memreq;' \
  'stftInL = ptr; ptr += fftSize + 4;' \
  'stftInR = ptr; ptr += fftSize + 4;' \
  'stftOutL = ptr; ptr += fftSize + 4;' \
  'stftOutR = ptr; ptr += fftSize + 4;' \
  'resBinFloor = ptr; ptr += halfLen;' \
  'resBinGain = ptr; ptr += halfLen;'; do
  grep -Fq "$expected" "$script_path" || allocation_ok=false
done
if ! "$host_crossfeed_only"; then
  for expected in \
    'buf_l = ptr; ptr += maxDelay;' \
    'buf_r = ptr; ptr += maxDelay;'; do
    grep -Fq "$expected" "$script_path" || allocation_ok=false
  done
fi
if "$allocation_ok"; then
  pass "memory blocks use sequential flat pointer allocation"
else
  fail "memory allocation topology is missing a required sequential block"
fi

stft_api_ok=true
for expected in \
  'stftCheckMemoryRequirement(stftIdxL, fftSize, kOverlap, warpFactor)' \
  'stftCheckMemoryRequirement(stftIdxR, fftSize, kOverlap, warpFactor)' \
  'stftInit(stftIdxL, stftStructL)' \
  'stftInit(stftIdxR, stftStructR)' \
  'stftForward(stftInL, stftIdxL, stftStructL, 1)' \
  'stftForward(stftInR, stftIdxR, stftStructR, 1)' \
  'stftBackward(stftInL, stftIdxL, stftStructL, 1)' \
  'stftBackward(stftInR, stftIdxR, stftStructR, 1)'; do
  grep -Fq "$expected" "$script_path" || stft_api_ok=false
done
if "$stft_api_ok"; then
  pass "STFT calls use the required API signatures"
else
  fail "required STFT API signature missing"
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

if ! grep -q 'resBinFloor = ptr; ptr += halfLen' "$script_path"; then
  fail "per-bin STFT floor memory missing"
else
  pass "per-bin STFT floor memory present"
fi

if ! grep -q 'resBinGain = ptr; ptr += halfLen' "$script_path"; then
  fail "per-bin STFT gain memory missing"
else
  pass "per-bin STFT gain memory present"
fi

if ! grep -q 'resBinFloor\[idx\] = 0.0001' "$script_path"; then
  fail "per-bin STFT floor initialization missing"
else
  pass "per-bin STFT floor initialization present"
fi

if ! grep -q 'resBinGain\[idx\] = 1.0' "$script_path"; then
  fail "per-bin STFT gain initialization missing"
else
  pass "per-bin STFT gain initialization present"
fi

if grep -Eq 'res_thresh = res_floor|rawGain = \\(bandEnergy > res_thresh\\)' "$script_path"; then
  fail "band-global STFT suppressor regression found"
else
  pass "band-global STFT suppressor regression absent"
fi

if ! grep -Fq 'loudAtkCoef = exp(-1.0 / (0.010 * srate))' "$script_path"; then
  fail "sample-rate-derived loudness attack coefficient missing"
else
  pass "sample-rate-derived loudness attack coefficient present"
fi

if "$host_limiter_only"; then
  if grep -Eq 'limAtkCoef|limRelCoef|limGainSmoothCoef|lim_env|smooth_gain|lim_gain|VCA-STYLE MASTERING LIMITER|out_[LR][[:space:]]*=[[:space:]]*min\(max\(' "$script_path"; then
    fail "host-limiter candidate contains internal limiter or hard-clamp processing"
  else
    pass "terminal limiting is delegated to the JDSP host"
  fi

  if grep -Eq '(^|[^[:alnum:]_])(res_floor|res_thresh|bandEnergy|suppression)[[:space:]]*=' "$script_path"; then
    fail "host-limiter candidate contains removed inactive state"
  else
    pass "inactive state cleanup is present"
  fi
else
  if ! grep -Fq 'limAtkCoef = exp(-1.0 / (0.0015 * srate))' "$script_path"; then
    fail "reference limiter attack coefficient missing"
  else
    pass "reference limiter attack coefficient present"
  fi

  if ! grep -Fq 'limGainSmoothCoef = exp(-1.0 / (0.005 * srate))' "$script_path"; then
    fail "reference limiter gain smoothing coefficient missing"
  else
    pass "reference limiter gain smoothing coefficient present"
  fi
fi

if "$host_crossfeed_only"; then
  if grep -Eq '^slider4:|buf_[lr]|del_idx|delaySamples|read_idx|del_[lr]|cross_[lr]|crossAmtLin|[lh]pf_cross' "$script_path"; then
    fail "device-neutral candidate contains internal crossfeed state or processing"
  else
    pass "crossfeed is absent from the EEL core"
  fi
fi

if "$phase_preserving_bass"; then
  if grep -Eq 'orig_hp_[lr]|hpf_orig_[lr]' "$script_path"; then
    fail "phase-preserving bass candidate contains the removed dry bass crossover reconstruction"
  else
    pass "bass harmonic stage leaves the dry path unsplit"
  fi

  if ! grep -Fq 'out_L += harm_l * subGainLin;' "$script_path" ||
     ! grep -Fq 'out_R += harm_r * subGainLin;' "$script_path"; then
    fail "phase-preserving bass candidate additive harmonic injection is missing"
  else
    pass "bass harmonic branch is injected additively"
  fi
fi

if [ "$script_name" = "axiom_binaural_dsp_v4.1.4.7.eel" ]; then
  if ! grep -Fq 'headroomGain = exp(-1.0 * DB_2_LOG);' "$script_path" ||
     ! grep -Fq 'out_L *= headroomGain;' "$script_path" ||
     ! grep -Fq 'out_R *= headroomGain;' "$script_path"; then
    fail "v4.1.4.7 terminal transparent headroom reserve is missing"
  else
    pass "terminal transparent headroom reserve is present"
  fi
fi

if [ "$script_name" = "axiom_binaural_dsp_v4.1.4.8.eel" ]; then
  if ! grep -Fq 'headroomGain = exp(-1.0 * DB_2_LOG);' "$script_path" ||
     ! grep -Fq 'defaultSubGainLin = exp(4.0 * DB_2_LOG);' "$script_path" ||
     ! grep -Fq 'outputGain = (slider1 > 4.0) ? (headroomGain * defaultSubGainLin / subGainLin) : headroomGain;' "$script_path" ||
     ! grep -Fq 'out_L *= outputGain;' "$script_path" ||
     ! grep -Fq 'out_R *= outputGain;' "$script_path"; then
    fail "v4.1.4.8 bass-aware terminal reserve is missing"
  else
    pass "bass-aware terminal reserve is present"
  fi
fi

if [ "$script_name" = "axiom_binaural_dsp_v4.1.4.9.eel" ] ||
   [ "$script_name" = "axiom_binaural_dsp_v4.1.4.10.eel" ]; then
  if ! grep -Fq 'headroomGain = exp(-1.0 * DB_2_LOG);' "$script_path" ||
     ! grep -Fq 'outputGain = (slider1 > 4.0) ? (headroomGain * exp(-((slider1 - 4.0) * 0.75) * DB_2_LOG)) : headroomGain;' "$script_path" ||
     ! grep -Fq 'out_L *= outputGain;' "$script_path" ||
     ! grep -Fq 'out_R *= outputGain;' "$script_path"; then
    fail "reduced bass-reserve slope is missing"
  elif grep -Fq 'defaultSubGainLin' "$script_path"; then
    fail "reduced-reserve architecture retains unused full-reserve baseline state"
  else
    pass "reduced bass-reserve slope is present without unused state"
  fi
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
