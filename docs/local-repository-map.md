# Axiom Local Repository Map

This document explains the local Axiom directories around the main
`axiom-binaural-dsp` repository. It is a repo-safe map, not a complete dump of
private local paths.

## Main Repository

`axiom-binaural-dsp` is the source of truth for:

- accepted and historical EEL files under `src/`;
- docs, qualification records, roadmap, and release gates;
- helper CLI, tests, Codex skills, and Pi harness source;
- repo-safe Knowledge notes under `docs/knowledge/`;
- ignored local Knowledge source index and PDF shelf under `docs/knowledge/`.

Current policy: keep PDFs and `source-index.local.json` local-only and ignored
by git. Track summaries, concept notes, and source-index examples only.

## External Knowledge Scaffold

`../axiom-knowledge-base` is an older external technical-library scaffold. It
contains taxonomy, guardrail, workflow, catalog-template, claim-template, and
starter-source documents. It is small and does not appear to contain the active
PDF library.

Recommended status: **reference or retire after review**.

Use it only as historical design input for Knowledge workflow ideas. The active
Axiom Knowledge layout should remain inside `docs/knowledge/` so the local
repo has one obvious Knowledge entry point.

Do not move its whole structure into the repo. The current repo Knowledge model
is simpler and already integrated with `knowledge-query`, `knowledge-sources`,
guardrails, and git ignore rules.

Potential follow-up:

- review its catalog and claim templates for ideas worth adapting;
- if useful, convert only the durable workflow concepts into repo docs;
- then mark the external scaffold as archived in local notes.

## External Worktrees

`../axiom-worktrees` contains registered Git worktrees for older Codex
branches. These are not the active repo and should not be treated as Knowledge
or general project storage.

Observed worktrees:

| Worktree | Branch | Current Meaning |
| --- | --- | --- |
| `analysis` | `codex/testbench-analysis` | Historical testbench branch; branch tip is not contained in `main`. |
| `transfer-analysis` | `codex/testbench-transfer` | Historical transfer-analysis branch; branch tip is not contained in `main`. |
| `repeatability` | `codex/testbench-repeatability` | Historical repeatability branch; branch tip is not contained in `main`. |
| `host-render` | `codex/testbench-host-render` | Historical host-render branch; branch tip is contained in `main`, but the worktree has an untracked render script. |
| `testbench-expansion` | `codex/testbench-expansion` | Historical branch; branch tip is contained in `main`. |
| `v4148` | `codex/v4.1.4.8-bass-aware-headroom` | Historical candidate/qualification branch; branch tip is contained in `main`. |

Recommended status: **preserve until branch-level audit is done**.

Do not delete or prune these worktrees casually. Some branch tips are not
contained in `main`, and one worktree has an untracked file. If cleanup is
wanted later, audit each branch diff against `main`, decide whether any
remaining code or tests should be ported, and only then remove the worktree
through normal Git worktree commands.

## Practical Rule

Use these locations this way:

- `axiom-binaural-dsp`: active source, docs, tests, helper tooling, and
  repo-contained local Knowledge structure.
- `docs/knowledge/pdfs/`: ignored local PDF shelf for Axiom Knowledge.
- `docs/knowledge/source-index.local.json`: ignored local metadata index for
  user-provided source files.
- `../axiom-knowledge-base`: historical external Knowledge scaffold; reference
  only until archived or selectively adapted.
- `../axiom-worktrees`: historical Git worktrees; preserve until branch audit
  and explicit cleanup.

## Next Cleanup Step

The safe next cleanup is a branch audit, not deletion:

1. For each external worktree branch, compare it against `main`.
2. Identify any unique tests, scripts, docs, or untracked files.
3. Decide whether to port, archive, or discard each item.
4. Remove only worktrees whose unique content is intentionally handled.
