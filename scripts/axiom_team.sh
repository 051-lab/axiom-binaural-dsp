#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
harness_root="${repo_root}/tools/axiom-team"
coordinator_model="${AXIOM_PI_COORDINATOR_MODEL:-openai-codex/gpt-5.5}"
export AXIOM_PI_ROLE_MODEL="${AXIOM_PI_ROLE_MODEL:-openai-codex/gpt-5.5}"

cd "${repo_root}"
exec pi \
  --model "${coordinator_model}" \
  --no-extensions \
  --no-skills \
  --no-prompt-templates \
  --no-builtin-tools \
  --extension "${harness_root}/extensions/index.ts" \
  --skill "${harness_root}/skills/axiom-engineering" \
  --append-system-prompt "${harness_root}/prompts/SYSTEM.md" \
  --session-dir "${HOME}/.local/state/axiom-engineering/pi-sessions" \
  "$@"
