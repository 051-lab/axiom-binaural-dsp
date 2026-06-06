# Axiom Codex Helper CLI

Use the helper CLI for safe orchestration support:

```bash
python3 tools/axiom-codex/axiom_codex.py status-summary
python3 tools/axiom-codex/axiom_codex.py ready-check
python3 tools/axiom-codex/axiom_codex.py agent-review --topic "..."
python3 tools/axiom-codex/axiom_codex.py knowledge-query "query text"
```

These helpers do not replace the Pi harness. They are Codex-side support for
status, review framing, and safe Knowledge search.

## Command Boundaries

- `status-summary`: read-only repository and policy summary.
- `ready-check`: documentation/static safety checks only.
- `agent-review`: structured multi-role review scaffold from local role docs.
- `knowledge-query`: search repo-safe notes and optional local-only source
  metadata without exposing private paths by default.
