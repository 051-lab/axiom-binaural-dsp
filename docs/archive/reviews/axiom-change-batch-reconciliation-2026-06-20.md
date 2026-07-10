# Axiom Change-Batch Reconciliation

Date: 2026-06-20

Scope: review the current uncommitted Axiom repository work, classify it into
coherent batches, identify blockers, and define a safe path to a clean
checkpoint. This review does not commit, publish, merge, change DSP behavior,
or approve a candidate.

## Decision

The current change batch was committed locally after explicit user approval.
Publication and pushing remain separate approval-gated actions.

Most automated validation passes. The two Player blockers identified below
were resolved during follow-up implementation. The historical `.10`
formatting-only change was restored to the committed evidence anchor after
explicit user approval.

The Player batch also contains a generated `tools/axiom-player/__pycache__/`
directory on disk. It is ignored by git and must stay outside commit scope.

## Findings

### High: Player Track IDs Can Escape The Music Library

`AxiomPlayer.play_track()` decodes a caller-controlled absolute path, checks
only that the file exists and has a supported extension, and then copies or
plays it. It does not require the resolved path to be under
`self.library_root`.

Resolved: track paths and symlinks are now resolved and required to remain
under the configured library root. Forged IDs, sibling paths, and escaping
symlinks are rejected. Direct and Flask endpoint tests cover the boundary, and
both the launcher and Python CLI reject non-loopback hosts.

### Medium: Player Runtime Dependencies Are Undeclared

The Player imports Flask and Mutagen and launches mpv. These are installed on
the current machine, but there is no tracked requirements file, package
metadata, bootstrap check, or prerequisite section that makes a fresh setup
repeatable.

Resolved: `tools/axiom-player/requirements.txt` declares Flask and Mutagen.
The Player documentation lists command prerequisites, and the launcher fails
before route startup when commands, Python packages, or the library are
missing.

### Medium: Historical `.10` EEL Is Modified

The only diff is:

```text
slider1 = 4;
```

to:

```text
slider1 = 4.00;
```

Static EEL validation passes, and the numeric value is equivalent. The file
hash still changes, so the modification violates historical evidence
immutability. Do not include this file in any commit. Reconcile it separately
with the user-owned working tree before publication preparation.

Resolved: the file was restored to the exact committed content. Its SHA-256
again matches the repository version, and `.10` is absent from the change set.

### Low: Dashboard Guidance Was Stale

`docs/system-status.md` still described PR #12 as open and recommended merging
it, while `AX-TASK-025` records that PR #12 is complete. This review updates the
dashboard to remove that stale action.

## Proposed Commit Groups

### Group 1: Naming And Continuity Policy

Primary scope:

- `AGENTS.md`
- `docs/versioning-and-naming.md`
- `docs/current-state.md`
- naming references in roadmap, release-gate, runbook, README, and status docs
- `docs/axiom-layer-progression-2026-06-10.md`

Boundary: documentation and naming policy only. Exclude all `.eel` files.

### Group 2: Agentic And Knowledge Tooling

Primary scope:

- `tools/axiom-codex/`
- `tests/test_axiom_codex_helper.py`
- Axiom Codex skill references
- Airwindows Knowledge notes and taxonomy
- Agentic evidence ingestion, status, and catalog support
- task ledger, blueprint, and related docs

Boundary: local orchestration and metadata only. No real-JDSP execution,
candidate creation, private evidence, or external source code.

### Group 3: WSL Listening Route And Axiom Player

Primary scope:

- `tools/axiom-player/`
- `tests/test_axiom_player.py`
- WSL listening and player scripts
- `docs/axiom-player.md`
- `docs/wsl-jdsp-listening.md`
- related tool-inventory and README entries

Status: blockers resolved and committed locally.

Boundary: local listening tooling only. No qualification claim and no private
music, cache, bookmarks, or runtime state.

### Group 4: Reconciliation And Status Refresh

Primary scope:

- this report;
- corrected current-status guidance;
- task-ledger entry for reconciliation follow-up.

Boundary: review metadata only.

Some shared documentation files span multiple groups. Use hunk-level staging
or combine Groups 1, 2, and 4 into one orchestration/documentation commit if a
clean split would obscure the actual dependency between them.

## Validation Results

Passed:

- `git diff --check`;
- Python unit tests: 201 passed, including forged-path, escaping-symlink,
  endpoint, invalid-ID, and loopback-host Player checks;
- Node harness tests: 23 passed;
- shell syntax checks for all five new listening/player scripts;
- static validation for accepted `.11`;
- static validation for historical `.10`;
- Codex ready-check;
- task-state validation: 32 tasks before this report;
- Airwindows metadata audit: 541 canonical effects;
- skill behavior eval: 7 fixtures;
- qualification evidence bundle validation: 2 records, zero critical failures.

Guard result:

- guard-check passes after restoring historical `.10`.

Not run as part of this reconciliation:

- a new real-JDSP capture;
- another long-duration soak;
- browser visual regression testing;
- publication, commit, merge, or accepted-baseline promotion.

## Next Sequence

1. Review the local commit series and publish or push only after explicit
   approval.
2. Return to focused `.11` Sub Harmonics listening after the repository
   checkpoint is clean.
