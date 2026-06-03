# Axiom Pi Runbooks

These runbooks define repeatable terminal missions for Codex/Pi sessions. Use
them when opening a new tmux window, assigning a Pi team task, or deciding
which command sequence belongs to the current work.

The runbooks complement `engineering-harness.md`. The harness document lists
commands and state-machine behavior; this document packages those commands into
missions with inputs, outputs, and stop conditions.

## Global Rules

Apply these rules to every runbook:

- Read `system-status.md` before choosing work.
- Confirm `v4.1.4.11` remains the accepted baseline unless policy has changed.
- Do not edit accepted or historical EEL files in place.
- Do not run two real-host JDSP measurements at the same time.
- Do not commit captures, source music, local manifests, credentials, route
  logs, private listening records, or generated run folders.
- Keep external LLM feedback advisory until converted into a testable issue,
  note, fixture, or rejection.
- Publication and merge each require explicit user approval.

## Runbook 1: Baseline Audit

Use when:

- starting a new session;
- checking repo and harness health;
- confirming the accepted baseline hash;
- preparing for candidate readiness or publication.

Inputs:

- repository checkout;
- accepted baseline policy in `tools/axiom-team/policy.json`;
- local harness configuration.

Steps:

```bash
git status -sb
node tools/axiom-team/bin/axiom-team.mjs doctor
node tools/axiom-team/bin/axiom-team.mjs corpus-status --strict-metadata
node tools/axiom-team/bin/axiom-team.mjs audit-baseline
```

Outputs:

- baseline hash confirmation;
- local dependency status;
- corpus metadata status;
- static/tooling audit run.

Stop conditions:

- accepted baseline hash mismatch;
- missing local manifest when the task requires corpus evidence;
- dirty worktree changes unrelated to the current task;
- failed static validation.

Decision:

- If all checks pass, continue with the planned work.
- If any check fails, fix the environment or documentation before creating a
  candidate.

## Runbook 2: Candidate Readiness

Use when:

- considering any sound-changing `.12`, v5, or profile candidate;
- deciding whether measurement foundations are strong enough for DSP work.

Inputs:

- accepted baseline hash;
- strict local material manifest;
- strict device matrix;
- no existing active candidate.

Steps:

```bash
scripts/evaluate_axiom_candidate_readiness.py \
  --json /tmp/axiom-candidate-readiness.json \
  --markdown /tmp/axiom-candidate-readiness.md
```

Outputs:

- readiness JSON and Markdown reports under `/tmp`;
- decision: `READY` or blocked.

Stop conditions:

- baseline hash mismatch;
- corpus metadata missing or incomplete;
- device route/setup coverage incomplete;
- warning or failure in strict mode.

Decision:

- If ready, a scoped investigation may continue.
- If blocked, fix the evidence foundation before proposing a candidate.

## Runbook 3: Investigation Without Candidate

Use when:

- the accepted baseline has a question that needs measurement;
- a listening concern needs evidence before DSP changes;
- a post-acceptance audit is needed.

Inputs:

- clear observation;
- falsifiable hypothesis;
- listening target;
- no candidate branch required yet.

Steps:

```bash
node tools/axiom-team/bin/axiom-team.mjs investigate "<observation>"
node tools/axiom-team/bin/axiom-team.mjs hypothesis <run-id> "<hypothesis>" "<listening target>"
```

Then choose the narrow measurement:

```bash
node tools/axiom-team/bin/axiom-team.mjs stress-accepted <run-id>
node tools/axiom-team/bin/axiom-team.mjs map-sub-gain <run-id> --slider-db 10 --slider-db 12 --label-regex 'electronic|hip hop|bass|flawed'
node tools/axiom-team/bin/axiom-team.mjs stage-observability <run-id>
node tools/axiom-team/bin/axiom-team.mjs audit-stft <run-id>
node tools/axiom-team/bin/axiom-team.mjs audit-width-mono <run-id>
node tools/axiom-team/bin/axiom-team.mjs screen-exciter-probes <run-id>
```

Outputs:

- local run record under `~/.local/state/axiom-engineering/runs/`;
- gate status;
- public summary only if sanitized and useful.

Stop conditions:

- measurement route unavailable;
- another real-host run is active;
- hypothesis is broad or not falsifiable;
- result does not justify a candidate.

Decision:

- Stop with "no candidate" when evidence does not justify a sound change.
- Move to Labs or candidate creation only when evidence identifies a scoped
  change worth testing.

## Runbook 4: Labs Experiment

Use when:

- an idea needs exploration but is not ready for Core;
- a profile concept needs a fixture;
- external feedback suggests a possible DSP direction.

Inputs:

- Labs issue or `templates/labs-experiment.md` note;
- hypothesis;
- changed variables;
- forbidden scope.

Steps:

```bash
git switch -c labs/<topic>
```

Create or update the Labs note, then run only the minimum tests needed for the
hypothesis. Typical examples:

```bash
scripts/validate_axiom_static.sh <temporary-fixture.eel>
scripts/analyze_audio_perceptual_metrics.py <capture.wav> --json /tmp/metrics.json --markdown /tmp/metrics.md
node tools/axiom-team/bin/axiom-team.mjs screen-width-material <run-id>
```

Outputs:

- Labs note;
- local reports under `/tmp` or harness state;
- decision: stop, continue Labs, create diagnostic, create candidate, or no
  action.

Stop conditions:

- accepted baseline or historical EEL file is edited in place;
- too many variables change to interpret the result;
- required evidence would need private/copyrighted material in git;
- measurement cannot support or reject the hypothesis.

Decision:

- Keep successful research in Labs until candidate gates are met.
- Do not merge Labs into Core directly.

## Runbook 5: Candidate Creation And Qualification

Use when:

- candidate readiness passes;
- an investigation or Labs result supports one narrow sound-changing edit;
- user agrees the candidate is worth listening to.

Inputs:

- run ID with hypothesis and listening target;
- candidate version;
- scoped edit boundary;
- required qualification plan.

Steps:

```bash
node tools/axiom-team/bin/axiom-team.mjs create-candidate <run-id> vX.Y.Z
```

After scoped implementation in the candidate worktree:

```bash
node tools/axiom-team/bin/axiom-team.mjs qualify <run-id>
```

Use a scoped qualification command instead when the candidate intentionally
changes behavior that generic transparency checks would reject, for example:

```bash
node tools/axiom-team/bin/axiom-team.mjs qualify-lowmid-candidate <run-id>
```

Outputs:

- versioned EEL candidate;
- qualification gates;
- local listening package or evidence path.

Stop conditions:

- unscoped file differences;
- static validation failure;
- normal-material clipping;
- silent or unreliable host capture;
- missing listening target;
- user rejects listening.

Decision:

- Proceed to listening only when qualification says the candidate is safe
  enough to evaluate.
- Do not promote on measurement alone.

## Runbook 6: Listening Acceptance

Use when:

- a qualified candidate is ready for user listening;
- a structured accept/reject decision is needed.

Inputs:

- candidate version;
- comparison version;
- host settings;
- material classes;
- device/route.

Steps:

```bash
scripts/build_android_validation_package.py \
  src/axiom_binaural_dsp_vX.Y.Z.eel \
  /tmp/axiom-android-vX.Y.Z

scripts/build_axiom_ab_listening_package.py \
  /tmp/axiom-captures/accepted \
  /tmp/axiom-captures/candidate \
  /tmp/axiom-ab-listening-vX.Y.Z
```

After the user records a structured local listening record:

```bash
scripts/validate_axiom_listening_record.py \
  ~/.local/state/axiom-engineering/listening-records/vX.Y.Z.json \
  --json /tmp/axiom-listening-validation.json \
  --markdown /tmp/axiom-listening-validation.md
```

Outputs:

- validated local listening record;
- sanitized summary for the qualification document if accepted.

Stop conditions:

- route/settings mismatch;
- user reports `needs_retest`, `no_decision`, or `reject`;
- private material cannot be summarized safely;
- candidate differs mainly by uncontrolled loudness.

Decision:

- `accept` can move to release preparation.
- any other decision blocks promotion.

## Runbook 7: Advisory Review Triage

Use when:

- ChatGPT, Claude, Qwen, Gemini, or another reviewer provides critique;
- a user brings in an external repo review;
- a research idea needs normalization.

Inputs:

- review summary;
- affected files or concept;
- source/reviewer identity if safe to record.

Steps:

1. Fill `templates/external-review-triage.md` or open an external review issue.
2. Separate claims worth testing from unsupported claims.
3. Assign each useful claim to Core, Labs, Knowledge, Qualification, docs, or
   reject.
4. Create a Labs experiment, Knowledge note, issue, or documentation update.

Outputs:

- triage note or issue;
- rejected claims list;
- testable follow-up tasks.

Stop conditions:

- review asks for unsupported claims;
- review requires copyrighted or private content in git;
- suggested change bypasses qualification;
- no falsifiable action exists.

Decision:

- Advice becomes work only after it is scoped and testable.

## Runbook 8: Repository Housekeeping

Use when:

- docs may be stale;
- a branch is ready to publish;
- generated files may have leaked into git status;
- the system status dashboard needs refresh.

Inputs:

- clean understanding of intended scope;
- current branch and remote state.

Steps:

```bash
git status -sb
git diff --check
rg -n 'accepted source is .*v4\.1\.4\.10|Current accepted baseline.*4\.1\.4\.10|Maintained by 051-lab.*4\.1\.4\.10|accepted baseline \| `v4\.1\.4\.10`' README.md AGENTS.md CONTRIBUTING.md docs tools .github || true
```

For documentation branches:

```bash
ruby -e 'require "yaml"; ARGV.each { |f| YAML.load_file(f); puts "ok #{f}" }' .github/ISSUE_TEMPLATE/*.yml
python3 tools/generate_session_work_log_pdf.py
```

Outputs:

- clean status report;
- regenerated work-log PDF when relevant;
- list of files intended for commit.

Stop conditions:

- unrelated dirty files;
- generated captures or local manifests in git status;
- stale accepted-baseline references;
- failing validation.

Decision:

- Commit only the scoped files.
- Publish only after user approval.

## Runbook 9: Publication And Merge

Use when:

- the user explicitly approves publishing;
- scope and validation are complete.

Inputs:

- intended branch;
- commit message;
- validation summary;
- PR target.

Steps:

```bash
git status -sb
git diff --stat
git add <scoped files>
git commit -m "<message>"
git push -u origin <branch>
```

Open a PR with:

- summary;
- why it matters;
- validation;
- risks or tests not run.

Merge only after separate user approval.

Outputs:

- commit hash;
- PR URL;
- merge commit when approved.

Stop conditions:

- user has not approved publication;
- branch contains unrelated files;
- validation is stale or failed;
- PR contains private artifacts;
- merge approval has not been explicitly given.
