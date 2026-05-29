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
test-material locations differ. `doctor` requires the accepted `.10` SHA-256
recorded in `tools/axiom-team/policy.json`, the JDSP route helper, CLI tools,
and the configured external-material manifest.

## Commands

Inside Pi, the primary commands are:

| Command | Purpose |
|---------|---------|
| `/axiom-doctor` | Check baseline identity and local dependencies |
| `/axiom-status` | View local engineering run states |
| `/axiom-audit-baseline` | Run static/tooling gates on the accepted baseline without creating a new DSP file |
| `/axiom-investigate <observation>` | Open a measurement-backed investigation |
| `/axiom-hypothesis run-id \| hypothesis \| listening target` | Establish the reason and audible target before coding |
| `/axiom-measure-limiter run-id` | Capture the accepted baseline across controlled JDSP limiter thresholds for an investigation |
| `/axiom-stress-accepted run-id` | Establish repeated dense-material behavior for the accepted baseline at `-1.00 dB` |
| `/axiom-map-sub-gain run-id` | Map dense-material behavior from `+4` through `+12 dB` Sub Harmonics Gain |
| `/axiom-stage-observability run-id` | Measure same-render `spatial_out -> bass_post` and `reserve_pre -> reserve_post` diagnostic taps |
| `/axiom-screen-reserve-law run-id` | Screen reduced elevated-bass reserve slopes in temporary fixtures |
| `/axiom-qualify-reserve-range run-id` | Range-qualify viable reduced reserve slopes before a candidate |
| `/axiom-audit-stft run-id` | Measure same-render pre-STFT versus STFT outputs at unity and accepted suppression |
| `/axiom-audit-width-mono run-id` | Measure accepted width gain and M/S leakage against temporary unity width |
| `/axiom-screen-width-material run-id` | Characterize band-specific accepted width behavior on registered material |
| `/axiom-screen-lowmid-width run-id` | Screen restrained `150 Hz-4 kHz` width settings before a candidate |
| `/axiom-screen-high-width run-id` | Screen restrained `4 kHz-18 kHz` width settings from accepted `.10` before a candidate |
| `/axiom-screen-exciter run-id` | Screen dynamic exciter sensitivity from accepted `.10` before a candidate |
| `/axiom-create-candidate run-id \| vX.Y.Z` | Create an external worktree and new versioned candidate |
| `/axiom-qualify run-id` | Run unit/static checks and serialized real-host JDSP qualification |
| `/axiom-qualify-lowmid-candidate run-id` | Qualify a restrained low-mid width candidate with its scoped spatial gate |
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
candidate exists, `/axiom-measure-limiter` runs repeated same-baseline captures of
the flagged external electronic excerpt at `-0.50`, `-1`, and `-3 dB` limiter
thresholds. It reports repeatability plus peak, RMS, crest, and 20 ms envelope
percentile shifts. Classification uses only non-clipping metrics whose
repeated-capture spread meets policy; waveform alignment remains diagnostic.
A detected threshold effect is evidence of host limiter participation, not
automatically evidence that Axiom's EEL must change.

Once participation is established, `/axiom-stress-accepted` runs all
registered dense-material excerpts through the accepted baseline repeatedly at the
tracked `-1.00 dB` limiter setting. It fails on clipping, silence, or absence
of repeatable level metrics. Stable near-ceiling output is recorded as
`PASS_WITH_INVESTIGATION`, creating the reference behavior future candidate
qualification must not silently worsen.

`/axiom-map-sub-gain` then measures the user-controlled bass path on registered
material using temporary accepted-baseline fixtures at `+4`, `+6`, `+8`, `+10`, and
`+12 dB` while holding the accepted host configuration fixed. It distinguishes
a broken default baseline from an elevated-control boundary: default clipping
or unreliable measurements fail, while elevated clipping is recorded as a
tested usable-range limit that can justify a narrowly scoped future candidate.
It separately records repeatable broadband RMS retreat relative to `+4 dB`,
because safe peak margin is not sufficient evidence that an elevated control
setting preserves practical listening level.

`/axiom-stage-observability` measures where that behavior appears inside the
accepted script before any reserve-law candidate is proposed. It creates
temporary same-render fixtures from the accepted baseline and renders generated
deterministic probes through the accepted host settings. The first mode records
`spatial_out -> bass_post` and `reserve_pre -> reserve_post` deltas, including
peak, RMS, crest, 20 ms envelope, and band-energy changes. This is diagnostic
stage evidence only; it cannot create or accept a listening candidate.

When that map exposes substantial level retreat, `/axiom-screen-reserve-law`
generates temporary `+8 dB` fixtures with reserve slopes of `1.000`, `0.875`,
`0.750`, and `0.500`. It screens the critical electronic and hip-hop excerpts
at the accepted host setting. One excluded conditioning render is performed
before each measured fixture/excerpt set so a cold host or newly loaded
fixture cannot contaminate the repeated metrics. A reduced slope advances only when every
screened excerpt recovers repeatable RMS level while remaining unclipped and
below the `-0.50 dBFS` observation boundary. The screen is pre-candidate
evidence; broader boundary qualification and user listening remain mandatory.

After a viable focused result, `/axiom-qualify-reserve-range` renders slopes
`0.750` and `0.500` against all registered excerpts at `+12`, `+10`, `+8`,
and `+6 dB`, starting with the highest-risk setting. It uses the same excluded
conditioning render and accepted host settings. Unstable scalar measurement
receives one fresh conditioned retry; a verified headroom rejection halts
further renders for that slope, because a law that fails one elevated setting
cannot qualify for a full-range candidate.

`/axiom-audit-stft` is a non-candidate stage investigation. It creates
temporary external fixtures from the accepted baseline at `0%` and accepted
suppression. With mono probes, each fixture sends its pre-STFT and processed
paths to separate output channels within one serialized real-JDSP capture, so
stage delay and residuals are not inferred from independently scheduled
captures. It repeats impulse captures by default to test transient metrics
against frame/load variation. It gates capture integrity failures only;
measured behavior must be reviewed before a production-path change is
proposed.

`/axiom-audit-width-mono` is a non-candidate spatial investigation. It creates
a temporary unity-width fixture from the accepted baseline and renders
low-level pure-mid and pure-side probes through both settings. It measures
accepted `S->S` widening by frequency and observes unexpected `M->S` or
`S->M` leakage without altering the tracked EEL baseline. Pure-side
mono cancellation is expected behavior; only unintended cross-coupling,
integrity failure, or terminal pressure can motivate deeper review.

`/axiom-screen-width-material` follows the controlled probe audit with
registered program material. It compares accepted and temporary unity-width
renders using deep-bass, upper-bass, low-mid, and high-band `S/M` energy
ratios. Since symmetric side gain does not change the mono sum, this screen
measures stereo bass-image character rather than declaring widened side
content a mono failure.

`/axiom-screen-lowmid-width` is the next spatial pre-candidate gate. It changes
only the temporary low-mid width default (`slider5`) to measure accepted
`1.890x` side gain against restrained `1.701x` and conservative `1.553x`
alternatives over registered material. Reports divide the affected range into
body, fundamentals, presence, and articulation bands. A technically safe
reduction is not automatically preferable; user listening is required before
promoting any variant into a versioned DSP candidate.

When this screen justifies the `slider5 = 126%` variant, `/axiom-qualify-lowmid-candidate`
is used after candidate creation instead of `/axiom-qualify`. Generic qualification
requires default transparency and would incorrectly fail an intentional width
change. The scoped gate admits only the description line and the two `slider5`
default-site edits, then requires unclipped real-host material renders and the
expected restrained side-to-mid reduction across each affected band before
the candidate may proceed to listening.

`/axiom-screen-high-width` is a separate post-`.10` pre-candidate stage. It
changes only temporary `slider6` defaults from accepted `110%` to `105%` and
`100%`, retaining the accepted low-mid spatial setting. Reports divide
`4-18 kHz` into presence-edge, brilliance, and air bands. This screen may
justify a focused listening candidate; it does not alter or supersede `.10`
on measurement alone.

`/axiom-screen-exciter` is the next post-width pre-candidate stage. It changes
only temporary `slider3` defaults from accepted `50%` to `35%` and `0%`,
retaining the accepted spatial, bass, STFT, and reserve settings. Reports
measure high-band RMS, side balance, and terminal integrity across registered
material. It can justify a focused listening target for reduced brightness or
air only when the measured tradeoff is stronger than simply removing the
accepted clarity.

The completed `.10` registered-material screen found no such tradeoff:
reduced and bypassed sensitivity were effectively level-neutral on the tested
high-energy excerpts. Use lower-level material for any future exciter-specific
investigation before proposing a versioned candidate.

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

This action records local evidence but creates no new candidate and makes no
change to the accepted audio processing.
