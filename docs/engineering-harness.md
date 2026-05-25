# Axiom Engineering Harness

The Axiom engineering harness is a project-owned Pi coding-agent environment
for controlled DSP experiments. It coordinates analysis, versioned candidate
creation, real-JDSP qualification, human listening, and release evidence while
keeping the accepted EEL baseline immutable.

It does not replace listening acceptance. It does not give an agent permission
to publish or merge without an explicit user action.

## Operating Boundary

The tracked harness is under `tools/axiom-team/`. Runtime state is deliberately
outside the repository:

| Item | Default Location |
|------|------------------|
| Local configuration | `~/.config/axiom-engineering/axiom-binaural-dsp.json` |
| Run records and reports | `~/.local/state/axiom-engineering/runs/` |
| Candidate worktrees | `~/.local/state/axiom-engineering/worktrees/` |
| Pi sessions | `~/.local/state/axiom-engineering/pi-sessions/` |
| External music manifest | `~/.local/share/axiom-test-material/cc0-opengameart/axiom-external-cc0-manifest.json` |

Captured audio, source music, manifest contents, route credentials, and
generated reports must not be committed.

## Isolation

Start the Axiom environment with:

```bash
scripts/axiom_team.sh
```

The launcher disables automatically discovered Pi extensions, skills, prompt
templates, and general-purpose built-in tools. It explicitly loads the Axiom
extension and skill. This prevents a global multi-team configuration from
granting unsupervised shell or write access inside an Axiom session.

The default coordinator and specialist model is `openai-codex/gpt-5.5`.
Override it deliberately with `AXIOM_PI_COORDINATOR_MODEL` or
`AXIOM_PI_ROLE_MODEL` when required.

The tracked policy sets a `$5.00` soft session budget warning and a `$10.00`
hard limit. At the hard limit, model-initiated consultation and mutation tools
are blocked; read-only status and locally executed validation remain available.

The coordinator receives controlled tools for repository reads, read-only
specialist consultation, candidate creation, scoped candidate edits, validation,
and qualified local commits. Publication and merge are interactive commands
with separate confirmations.

Coordinator project reads and searches are restricted to tracked repository
content. The only untracked worktree content it may read directly is the
recorded versioned candidate EEL file.

## Setup

Initialize the local configuration and inspect prerequisites:

```bash
node tools/axiom-team/bin/axiom-team.mjs init
node tools/axiom-team/bin/axiom-team.mjs doctor
```

Review `~/.config/axiom-engineering/axiom-binaural-dsp.json` if local route or
test-material locations differ. `doctor` requires the accepted `.8` SHA-256
recorded in `tools/axiom-team/policy.json`, the JDSP route helper, CLI tools,
and the configured external-material manifest.

## Commands

Inside Pi, the primary commands are:

| Command | Purpose |
|---------|---------|
| `/axiom-doctor` | Check baseline identity and local dependencies |
| `/axiom-status` | View local engineering run states |
| `/axiom-audit-baseline` | Run static/tooling gates on accepted `.8` without creating a new DSP file |
| `/axiom-investigate <observation>` | Open a measurement-backed investigation |
| `/axiom-hypothesis run-id \| hypothesis \| listening target` | Establish the reason and audible target before coding |
| `/axiom-measure-limiter run-id` | Capture accepted `.8` across controlled JDSP limiter thresholds for an investigation |
| `/axiom-create-candidate run-id \| vX.Y.Z` | Create an external worktree and new versioned candidate |
| `/axiom-qualify run-id` | Run unit/static checks and serialized real-host JDSP qualification |
| `/axiom-listening-package run-id` | Locate the local listening/evidence report |
| `/axiom-record-listening run-id \| accept/reject \| notes` | Record the user's listening decision |
| `/axiom-commit run-id \| message` | Commit only permitted, qualified candidate changes locally |
| `/axiom-publish run-id` | Confirm push and draft PR creation |
| `/axiom-merge run-id` | Separately confirm merge of the published candidate |

The Node CLI exposes the same workflow for deterministic automation and tests.

## State Machine

An audible observation creates an `investigating` run anchored to the accepted
baseline hash. A candidate cannot be created without a hypothesis and a
listening target. A candidate cannot be committed until real-host qualification
has passed or returned a documented investigation status. Static-only
validation is diagnostic and cannot enable listening acceptance.

The real-JDSP qualification runner is guarded by a filesystem lock so two
agents cannot capture through the host route simultaneously. It always uses
the tracked host policy: master limiter enabled at `-1.00 dB`, `60 ms`
release, `0 dB` postgain, and crossfeed disabled for qualification.

For an investigation that questions terminal-limiter involvement before any
candidate exists, `/axiom-measure-limiter` runs repeated same-`.8` captures of
the flagged external electronic excerpt at `0`, `-1`, and `-3 dB` limiter
thresholds. It reports repeatability plus peak, RMS, crest, and 20 ms envelope
percentile shifts. A detected threshold effect is evidence of host limiter
participation, not automatically evidence that Axiom's EEL must change.

After listening acceptance, a release branch must contain:

- the versioned candidate EEL script;
- an updated `CHANGELOG.md`;
- `docs/qualification-vX.Y.Z.md`;
- an updated `tools/axiom-team/policy.json` designating that candidate path and
  SHA-256 as the proposed accepted baseline.

Only then may `/axiom-publish` push and open a draft PR. `/axiom-merge`
requires a separate user confirmation.

Documentation-only edits may be recorded after qualification or listening
acceptance without invalidating the audio gate. Any candidate EEL or validation
tooling edit returns the run to implementation and requires qualification again.

## Specialist Roles

The coordinator can consult read-only specialists for DSP architecture, signal
research, EEL implementation, tooling, qualification, measurement, safety, and
release review. These consultations can inspect repository files but cannot
edit them or run unrestricted shell commands. All actual writes pass through
the scoped candidate tool and remain tied to a recorded run.

## Baseline Dogfood Check

The initial harness verification audits the accepted baseline only:

```bash
node tools/axiom-team/bin/axiom-team.mjs audit-baseline
```

This action records local evidence but creates no `.9` candidate and makes no
change to the accepted audio processing.
