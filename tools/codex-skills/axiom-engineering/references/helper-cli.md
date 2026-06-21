# Axiom Codex Helper CLI

Use the helper CLI for safe orchestration support:

```bash
python3 tools/axiom-codex/axiom_codex.py status-summary
python3 tools/axiom-codex/axiom_codex.py ready-check
python3 tools/axiom-codex/axiom_codex.py command-surface
python3 tools/axiom-codex/axiom_codex.py agentic-audit
python3 tools/axiom-codex/axiom_codex.py evidence-ingest <report.json> [<report.json> ...]
python3 tools/axiom-codex/axiom_codex.py evidence-status <bundle.json>
python3 tools/axiom-codex/axiom_codex.py evidence-catalog <directory> --set-default
python3 tools/axiom-codex/axiom_codex.py guard-check
python3 tools/axiom-codex/axiom_codex.py agent-profiles
python3 tools/axiom-codex/axiom_codex.py agent-review --topic "..."
python3 tools/axiom-codex/axiom_codex.py airwindows-index --repo ~/.local/share/axiom-knowledge/sources/airwindows/repo
python3 tools/axiom-codex/axiom_codex.py airwindows-audit --repo ~/.local/share/axiom-knowledge/sources/airwindows/repo
python3 tools/axiom-codex/axiom_codex.py knowledge-query "query text"
python3 tools/axiom-codex/axiom_codex.py knowledge-sources
python3 tools/axiom-codex/axiom_codex.py pi-handoff
python3 tools/axiom-codex/axiom_codex.py skill-eval
```

These helpers do not replace the Pi harness. They are Codex-side support for
status, review framing, guard preflights, command/profile discovery, behavior
fixture checks, and safe Knowledge search.

## Command Boundaries

- `status-summary`: read-only repository and policy summary.
- `ready-check`: documentation/static safety checks only.
- `command-surface`: list the repo-tracked command registry that future native
  aliases or plugin commands should wrap.
- `agentic-audit`: fail closed on command/runtime drift, duplicate aliases,
  unsafe JDSP approval metadata, incomplete profiles, or malformed skill-eval
  fixtures.
- `evidence-ingest`: normalize supported local qualification JSON into a
  source-hashed bundle; private paths are hidden by default and the result is
  not listening acceptance or release approval.
- `evidence-status`: validate and summarize a normalized bundle for optional
  use by `status-summary --evidence` and `next-action --evidence`.
- `next-action`: recommend the next safe work item from task-state metadata;
  initial-maintenance Agentic hardening tasks require explicit
  `--include-maintenance`.
- `evidence-catalog`: inventory local bundles, select the newest valid bundle,
  and optionally configure its directory for automatic status orientation.
- `guard-check`: fail on known unsafe changed paths or added text, including
  accepted/historical EEL scope, policy changes, private audio, captures,
  local material, manifests, credentials, and private path leaks.
- `agent-profiles`: list Codex-specific role profiles or print one profile
  source with `--role`.
- `agent-review`: validated multi-role review record from local Codex profiles
  and Pi role docs; supports JSON output for future orchestration.
- `airwindows-index`: create a local-only metadata index from an external
  Airwindows checkout for clean-room concept retrieval.
- `airwindows-audit`: validate canonical metadata, forbidden fields and paths,
  duplicate effects, and optional checkout commit drift.
- `knowledge-query`: search repo-safe notes and optional local-only source
  metadata without exposing private paths by default; auto-discovers the
  standard local Airwindows metadata index when present and supports
  `--no-airwindows-index`.
- `knowledge-sources`: audit the local-only source index, local file
  existence, and matching repo-safe notes without exposing private paths by
  default.
- `pi-handoff`: print a draft Pi handoff brief for the targeted `.11` Sub
  Harmonics follow-up without running JDSP.
- `skill-eval`: deterministic fixture check for representative
  `$axiom-engineering` prompts and helper command mappings.

## Native Alias Policy

The command registry includes proposed `/axiom-*` aliases, but this repository
does not assume an undocumented Codex slash-command runtime. Native aliases
should only wrap the tracked helper commands and must preserve the same JDSP and
approval boundaries.
