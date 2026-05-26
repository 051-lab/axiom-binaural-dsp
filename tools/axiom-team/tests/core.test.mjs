import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import test from "node:test";
import {
  auditBaseline,
  baselineIdentity,
  commitCandidate,
  createInvestigation,
  readRun,
  recordListening,
  runAcceptedStressBaseline,
  runAutomatedValidation,
  runBaselineLimiterSweep,
  writeRun,
  writeScopedFile,
} from "../lib/core.mjs";

function sha256(filename) {
  return createHash("sha256").update(fs.readFileSync(filename)).digest("hex");
}

function fixture() {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "axiom-team-"));
  const repo = path.join(root, "repo");
  const stateRoot = path.join(root, "state");
  const worktreeRoot = path.join(stateRoot, "worktrees");
  fs.mkdirSync(path.join(repo, "src"), { recursive: true });
  fs.mkdirSync(path.join(repo, "scripts"), { recursive: true });
  fs.mkdirSync(path.join(repo, "tests"), { recursive: true });
  fs.mkdirSync(path.join(repo, ".git"), { recursive: true });
  const accepted = "src/axiom_binaural_dsp_v4.1.4.8.eel";
  fs.writeFileSync(path.join(repo, accepted), "accepted baseline\n", "ascii");
  fs.writeFileSync(path.join(repo, "tests", "test_fixture.py"), "import unittest\n\nclass FixtureTest(unittest.TestCase):\n    def test_fixture(self):\n        self.assertTrue(True)\n", "ascii");
  const validator = path.join(repo, "scripts", "validate_axiom_static.sh");
  fs.writeFileSync(validator, "#!/usr/bin/env bash\nexit 0\n", "ascii");
  fs.chmodSync(validator, 0o755);
  const manifest = path.join(root, "material.json");
  fs.writeFileSync(manifest, "{\"tracks\":[]}\n", "ascii");
  const config = {
    repositoryRoot: repo,
    stateRoot,
    worktreeRoot,
    routeHelper: path.join(root, "route-helper"),
    pulseServer: "unix:/tmp/fake",
    localMaterialManifest: manifest,
  };
  const policy = {
    project: { defaultBranch: "main" },
    acceptedBaseline: {
      version: "v4.1.4.8",
      path: accepted,
      sha256: sha256(path.join(repo, accepted)),
    },
    hostBaseline: { masterLimiterThresholdDb: -1.0 },
    requiredLocalMaterial: true,
  };
  return { root, repo, config, policy, accepted };
}

function candidateRun(fx) {
  const run = createInvestigation("Evaluate an isolated safety improvement", fx.config, fx.policy);
  const worktree = path.join(fx.config.worktreeRoot, run.id);
  const candidate = "src/axiom_binaural_dsp_v4.1.4.9.eel";
  fs.mkdirSync(path.join(worktree, "src"), { recursive: true });
  fs.mkdirSync(path.join(worktree, "scripts"), { recursive: true });
  fs.mkdirSync(path.join(worktree, "tests"), { recursive: true });
  fs.copyFileSync(path.join(fx.repo, fx.accepted), path.join(worktree, fx.accepted));
  fs.copyFileSync(path.join(fx.repo, fx.accepted), path.join(worktree, candidate));
  fs.copyFileSync(path.join(fx.repo, "scripts", "validate_axiom_static.sh"), path.join(worktree, "scripts", "validate_axiom_static.sh"));
  fs.copyFileSync(path.join(fx.repo, "tests", "test_fixture.py"), path.join(worktree, "tests", "test_fixture.py"));
  fs.chmodSync(path.join(worktree, "scripts", "validate_axiom_static.sh"), 0o755);
  run.candidate = { version: "v4.1.4.9", path: candidate, branch: "axiom/experiment/test", worktree, sha256: sha256(path.join(worktree, candidate)), commit: null, commits: [] };
  run.status = "candidate_created";
  writeRun(run, fx.config);
  return run;
}

test("accepted baseline identity is hash anchored", () => {
  const fx = fixture();
  assert.equal(baselineIdentity(fx.config, fx.policy).verified, true);
  fs.appendFileSync(path.join(fx.repo, fx.accepted), "changed\n");
  assert.equal(baselineIdentity(fx.config, fx.policy).verified, false);
  assert.throws(() => createInvestigation("Do not proceed", fx.config, fx.policy), /hash does not match/);
});

test("baseline audit is verified evidence and never a listening-ready candidate", () => {
  const fx = fixture();
  const run = auditBaseline(fx.config, fx.policy);
  assert.equal(run.status, "baseline_verified");
  assert.equal(run.candidate, null);
  assert.throws(() => recordListening(run.id, "accept", "", fx.config), /after automated gates/);
});

test("controlled writes cannot overwrite the accepted baseline", () => {
  const fx = fixture();
  const run = candidateRun(fx);
  assert.throws(() => writeScopedFile(run.id, fx.accepted, "candidate-eel", "bad\n", fx.config, fx.policy), /blocked/);
  const updated = writeScopedFile(run.id, run.candidate.path, "candidate-eel", "candidate change\n", fx.config, fx.policy);
  assert.equal(updated.status, "implementing");
  assert.equal(fs.readFileSync(path.join(run.candidate.worktree, run.candidate.path), "utf8"), "candidate change\n");
});

test("static-only validation records a skipped host gate and cannot advance to listening", () => {
  const fx = fixture();
  const run = candidateRun(fx);
  const result = runAutomatedValidation(run.id, { skipHost: true }, fx.config, fx.policy);
  assert.equal(result.status, "automated_validation");
  assert.equal(result.gates.at(-1).status, "skipped");
  assert.throws(() => recordListening(run.id, "accept", "not qualified", fx.config), /after automated gates/);
  assert.equal(readRun(run.id, fx.config).status, "automated_validation");
});

test("an unqualified candidate cannot be locally committed", () => {
  const fx = fixture();
  const run = candidateRun(fx);
  assert.throws(() => commitCandidate(run.id, "feat(dsp): unsafe", fx.config, fx.policy), /real-host qualification/);
});

test("post-listening evidence edits preserve acceptance while DSP edits remain blocked", () => {
  const fx = fixture();
  const run = candidateRun(fx);
  run.status = "listening_accepted";
  writeRun(run, fx.config);
  const updated = writeScopedFile(run.id, "docs/qualification-v4.1.4.9.md", "documentation", "accepted evidence\n", fx.config, fx.policy);
  assert.equal(updated.status, "listening_accepted");
  assert.throws(() => writeScopedFile(run.id, run.candidate.path, "candidate-eel", "changed after acceptance\n", fx.config, fx.policy), /active unpublished candidate/);
});

test("baseline limiter measurement is blocked until hypothesis exists and after candidate creation", () => {
  const fx = fixture();
  const investigation = createInvestigation("Measure default limiter behavior", fx.config, fx.policy);
  assert.throws(() => runBaselineLimiterSweep(investigation.id, fx.config, fx.policy), /hypothesis/);
  const candidate = candidateRun(fx);
  assert.throws(() => runBaselineLimiterSweep(candidate.id, fx.config, fx.policy), /no DSP candidate/);
});

test("accepted-setting stress measurement is blocked until hypothesis exists and after candidate creation", () => {
  const fx = fixture();
  const investigation = createInvestigation("Stress accepted dense-material behavior", fx.config, fx.policy);
  assert.throws(() => runAcceptedStressBaseline(investigation.id, fx.config, fx.policy), /hypothesis/);
  const candidate = candidateRun(fx);
  assert.throws(() => runAcceptedStressBaseline(candidate.id, fx.config, fx.policy), /no DSP candidate/);
});
