#!/usr/bin/env bash
set -euo pipefail

runtime_dir="/tmp/jdsp-win"
fifo_path="${runtime_dir}/out.raw"

pkill -x jamesdsp 2>/dev/null || true
pkill -x pulseaudio 2>/dev/null || true
pkill -f "$fifo_path" 2>/dev/null || true
pkill -f "Xvfb :121" 2>/dev/null || true
pkill -f "x11vnc .*:121" 2>/dev/null || true
pkill -f "websockify .*6080" 2>/dev/null || true
pkill -x openbox 2>/dev/null || true
pkill -x xcursor-follow 2>/dev/null || true
powershell.exe -NoProfile -Command \
  "Get-Process ffplay -ErrorAction SilentlyContinue | Stop-Process -Force" >/dev/null 2>&1 || true

rm -rf "$runtime_dir"
systemctl --user start pipewire-pulse >/dev/null 2>&1 || true

echo "Stopped Axiom WSL/JDSP listening route."
echo "Normal WSLg audio should be available again at unix:/mnt/wslg/PulseServer."
