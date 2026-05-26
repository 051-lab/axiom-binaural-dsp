import { execFileSync, spawnSync } from "node:child_process";
import { createHash, randomUUID } from "node:crypto";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";

const moduleDir = path.dirname(fileURLToPath(import.meta.url));
export const harnessRoot = path.resolve(moduleDir, "..");
export const repositoryRoot = path.resolve(harnessRoot, "../..");
export const policyPath = path.join(harnessRoot, "policy.json");
export const localConfigPath = path.join(os.homedir(), ".config", "axiom-engineering", "axiom-binaural-dsp.json");

export const RUN_STATES = new Set([
  "investigating", "baseline_verified", "candidate_created", "implementing", "automated_validation",
  "failed", "pass_with_investigation", "ready_for_listening", "listening_rejected",
  "listening_accepted", "publication_approved", "pull_request_open",
  "merge_approved", "baseline_merged", "blocked"
]);

export function loadJson(filename) {
  return JSON.parse(fs.readFileSync(filename, "utf8"));
}

export function loadPolicy() {
  return loadJson(policyPath);
}

export function defaultLocalConfig() {
  const stateRoot = path.join(os.homedir(), ".local", "state", "axiom-engineering");
  return {
    repositoryRoot,
    stateRoot,
    worktreeRoot: path.join(stateRoot, "worktrees"),
    routeHelper: path.join(os.homedir(), ".local", "bin", "jdsp-audio-reset"),
    pulseServer: "unix:/tmp/jdsp-win/native",
    localMaterialManifest: path.join(
      os.homedir(), ".local", "share", "axiom-test-material",
      "cc0-opengameart", "axiom-external-cc0-manifest.json"
    ),
    githubRepository: "051-lab/axiom-binaural-dsp"
  };
}

export function loadLocalConfig() {
  return fs.existsSync(localConfigPath) ? loadJson(localConfigPath) : defaultLocalConfig();
}

export function saveLocalConfig(config) {
  fs.mkdirSync(path.dirname(localConfigPath), { recursive: true, mode: 0o700 });
  fs.writeFileSync(localConfigPath, JSON.stringify(config, null, 2) + "\n", { mode: 0o600 });
  return localConfigPath;
}

function shell(command, args, options = {}) {
  const result = spawnSync(command, args, {
    cwd: options.cwd,
    encoding: "utf8",
    env: { ...process.env, ...(options.env || {}) },
    timeout: options.timeout || 0
  });
  return {
    command: [command, ...args].join(" "),
    exitCode: result.status ?? 1,
    stdout: result.stdout || "",
    stderr: result.stderr || "",
    error: result.error?.message || null
  };
}

function requireSuccess(result, label) {
  if (result.exitCode !== 0) {
    throw new Error(`${label} failed: ${(result.stderr || result.stdout || result.error || "unknown error").trim()}`);
  }
  return result;
}

export function sha256(filename) {
  return createHash("sha256").update(fs.readFileSync(filename)).digest("hex");
}

export function isoNow() {
  return new Date().toISOString();
}

function slug(value) {
  return value.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "").slice(0, 44) || "experiment";
}

export function ensureLocalDirectories(config = loadLocalConfig()) {
  for (const dirname of [config.stateRoot, path.join(config.stateRoot, "runs"), config.worktreeRoot, path.join(config.stateRoot, "locks")]) {
    fs.mkdirSync(dirname, { recursive: true, mode: 0o700 });
  }
}

export function runDirectory(id, config = loadLocalConfig()) {
  return path.join(config.stateRoot, "runs", id);
}

export function runPath(id, config = loadLocalConfig()) {
  return path.join(runDirectory(id, config), "run.json");
}

export function readRun(id, config = loadLocalConfig()) {
  const filename = runPath(id, config);
  if (!fs.existsSync(filename)) throw new Error(`Unknown Axiom run: ${id}`);
  return loadJson(filename);
}

export function writeRun(run, config = loadLocalConfig()) {
  if (!RUN_STATES.has(run.status)) throw new Error(`Invalid run status: ${run.status}`);
  run.updatedAt = isoNow();
  fs.mkdirSync(runDirectory(run.id, config), { recursive: true, mode: 0o700 });
  fs.writeFileSync(runPath(run.id, config), JSON.stringify(run, null, 2) + "\n", { mode: 0o600 });
  return run;
}

export function baselineIdentity(config = loadLocalConfig(), policy = loadPolicy()) {
  const filename = path.join(config.repositoryRoot, policy.acceptedBaseline.path);
  if (!fs.existsSync(filename)) throw new Error(`Accepted baseline missing: ${filename}`);
  const digest = sha256(filename);
  return {
    version: policy.acceptedBaseline.version,
    path: policy.acceptedBaseline.path,
    sha256: digest,
    expectedSha256: policy.acceptedBaseline.sha256,
    verified: digest === policy.acceptedBaseline.sha256
  };
}

export function createInvestigation(observation, config = loadLocalConfig(), policy = loadPolicy()) {
  if (!observation || !observation.trim()) throw new Error("An investigation requires an audible observation or measurable concern.");
  ensureLocalDirectories(config);
  const id = `${new Date().toISOString().replace(/[-:]/g, "").replace(/\..*/, "")}-${slug(observation).slice(0, 24)}-${randomUUID().slice(0, 6)}`;
  const baseline = baselineIdentity(config, policy);
  if (!baseline.verified) throw new Error("Accepted baseline hash does not match tracked policy; stop before experimentation.");
  return writeRun({
    schemaVersion: 1,
    id,
    status: "investigating",
    createdAt: isoNow(),
    observation: observation.trim(),
    hypothesis: null,
    listeningTarget: null,
    baseline,
    candidate: null,
    hostBaseline: policy.hostBaseline,
    gates: [],
    approvals: {
      listening: null,
      publication: null,
      merge: null
    }
  }, config);
}

export function setHypothesis(id, hypothesis, listeningTarget, config = loadLocalConfig()) {
  const run = readRun(id, config);
  if (run.status !== "investigating") throw new Error("Hypothesis can be set only while the run is investigating.");
  if (!hypothesis?.trim() || !listeningTarget?.trim()) throw new Error("Candidate creation requires both a hypothesis and a listening target.");
  run.hypothesis = hypothesis.trim();
  run.listeningTarget = listeningTarget.trim();
  return writeRun(run, config);
}

function recordGate(run, gate) {
  run.gates.push({ timestamp: isoNow(), ...gate });
  return run;
}

function recordCommandGate(run, name, result, outputDir = null) {
  return recordGate(run, {
    name,
    status: result.exitCode === 0 ? "pass" : "fail",
    exitCode: result.exitCode,
    command: result.command,
    outputDir,
    stdout: result.stdout.slice(-4000),
    stderr: result.stderr.slice(-4000)
  });
}

export function doctor(config = loadLocalConfig(), policy = loadPolicy()) {
  const checks = [];
  const check = (name, ok, detail) => checks.push({ name, status: ok ? "pass" : "fail", detail });
  const baseline = baselineIdentity(config, policy);
  check("accepted_baseline_hash", baseline.verified, `${baseline.sha256} expected ${baseline.expectedSha256}`);
  check("repository_root", fs.existsSync(path.join(config.repositoryRoot, ".git")), config.repositoryRoot);
  check("route_helper", fs.existsSync(config.routeHelper), config.routeHelper);
  check("local_material_manifest", fs.existsSync(config.localMaterialManifest), config.localMaterialManifest);
  for (const executable of ["pi", "node", "python3", "jamesdsp", "gh", "git"]) {
    const found = shell("bash", ["-lc", `command -v ${executable}`]);
    check(`executable_${executable}`, found.exitCode === 0, found.stdout.trim() || "not found");
  }
  const git = shell("git", ["status", "--short", "--branch"], { cwd: config.repositoryRoot });
  check("git_repository_status", git.exitCode === 0, git.stdout.trim());
  return { status: checks.some((item) => item.status === "fail") ? "fail" : "pass", config, baseline, checks };
}

export function auditBaseline(config = loadLocalConfig(), policy = loadPolicy()) {
  const run = createInvestigation(`Audit accepted baseline ${policy.acceptedBaseline.version} without creating a candidate`, config, policy);
  const out = path.join(runDirectory(run.id, config), "audit");
  fs.mkdirSync(out, { recursive: true, mode: 0o700 });
  const tests = shell("python3", ["-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py"], { cwd: config.repositoryRoot });
  const staticGate = shell("scripts/validate_axiom_static.sh", [policy.acceptedBaseline.path], { cwd: config.repositoryRoot });
  recordCommandGate(run, "python_unit_suite", tests, out);
  recordCommandGate(run, "eel_static_validation", staticGate, out);
  run.status = run.gates.every((gate) => gate.status === "pass") ? "baseline_verified" : "failed";
  return writeRun(run, config);
}

export function runBaselineLimiterSweep(id, config = loadLocalConfig(), policy = loadPolicy()) {
  const run = readRun(id, config);
  if (run.status !== "investigating" || run.candidate) {
    throw new Error("Baseline limiter measurement requires an investigation with no DSP candidate.");
  }
  if (!run.hypothesis || !run.listeningTarget) {
    throw new Error("Record a falsifiable hypothesis and listening target before host measurement.");
  }
  if (!fs.existsSync(config.localMaterialManifest)) {
    throw new Error("Configured local material manifest is unavailable.");
  }
  ensureLocalDirectories(config);
  const measurementId = isoNow().replace(/[-:]/g, "").replace(/\..*/, "");
  const outputDir = path.join(runDirectory(id, config), "limiter-sweeps", measurementId);
  fs.mkdirSync(outputDir, { recursive: true, mode: 0o700 });
  const lockDir = path.join(config.stateRoot, "locks", "jdsp-host.lock");
  try {
    fs.mkdirSync(lockDir);
  } catch {
    throw new Error("Another real-host JDSP qualification is already active.");
  }
  try {
    const result = shell(
      "scripts/run_jdsp_limiter_sweep.py",
      [
        policy.acceptedBaseline.path,
        config.localMaterialManifest,
        outputDir,
        "--pulse-server", config.pulseServer,
        "--route-helper", config.routeHelper,
      ],
      { cwd: config.repositoryRoot, timeout: 60 * 60 * 1000 }
    );
    const reportPath = path.join(outputDir, "limiter_sweep.json");
    let conclusion = result.exitCode === 0 ? "measurement_completed" : "unqualified";
    if (fs.existsSync(reportPath)) conclusion = loadJson(reportPath).classification.status;
    recordGate(run, {
      name: "baseline_jdsp_limiter_threshold_sweep",
      status: conclusion === "unqualified" ? "fail" : "pass",
      conclusion,
      exitCode: result.exitCode,
      reportPath,
      command: result.command,
      stdout: result.stdout.slice(-4000),
      stderr: result.stderr.slice(-4000)
    });
    return writeRun(run, config);
  } finally {
    fs.rmSync(lockDir, { recursive: true, force: true });
  }
}

export function runAcceptedStressBaseline(id, config = loadLocalConfig(), policy = loadPolicy()) {
  const run = readRun(id, config);
  if (run.status !== "investigating" || run.candidate) {
    throw new Error("Accepted-setting stress measurement requires an investigation with no DSP candidate.");
  }
  if (!run.hypothesis || !run.listeningTarget) {
    throw new Error("Record a falsifiable hypothesis and listening target before host measurement.");
  }
  if (!fs.existsSync(config.localMaterialManifest)) {
    throw new Error("Configured local material manifest is unavailable.");
  }
  ensureLocalDirectories(config);
  const measurementId = isoNow().replace(/[-:]/g, "").replace(/\..*/, "");
  const outputDir = path.join(runDirectory(id, config), "accepted-stress", measurementId);
  fs.mkdirSync(outputDir, { recursive: true, mode: 0o700 });
  const lockDir = path.join(config.stateRoot, "locks", "jdsp-host.lock");
  try {
    fs.mkdirSync(lockDir);
  } catch {
    throw new Error("Another real-host JDSP qualification is already active.");
  }
  try {
    const result = shell(
      "scripts/run_jdsp_accepted_stress.py",
      [
        policy.acceptedBaseline.path,
        config.localMaterialManifest,
        outputDir,
        "--pulse-server", config.pulseServer,
        "--route-helper", config.routeHelper,
        "--threshold-db", String(policy.hostBaseline.masterLimiterThresholdDb),
      ],
      { cwd: config.repositoryRoot, timeout: 60 * 60 * 1000 }
    );
    const reportPath = path.join(outputDir, "accepted_stress.json");
    let conclusion = result.exitCode === 0 ? "pass" : "fail";
    if (fs.existsSync(reportPath)) conclusion = loadJson(reportPath).evaluation.status;
    recordGate(run, {
      name: "accepted_setting_dense_material_stress",
      status: conclusion,
      conclusion,
      exitCode: result.exitCode,
      reportPath,
      command: result.command,
      stdout: result.stdout.slice(-4000),
      stderr: result.stderr.slice(-4000)
    });
    return writeRun(run, config);
  } finally {
    fs.rmSync(lockDir, { recursive: true, force: true });
  }
}

export function runSubSliderMap(id, config = loadLocalConfig(), policy = loadPolicy()) {
  const run = readRun(id, config);
  if (run.status !== "investigating" || run.candidate) {
    throw new Error("Sub Harmonics stress mapping requires an investigation with no DSP candidate.");
  }
  if (!run.hypothesis || !run.listeningTarget) {
    throw new Error("Record a falsifiable hypothesis and listening target before host measurement.");
  }
  if (!fs.existsSync(config.localMaterialManifest)) {
    throw new Error("Configured local material manifest is unavailable.");
  }
  ensureLocalDirectories(config);
  const measurementId = isoNow().replace(/[-:]/g, "").replace(/\..*/, "");
  const outputDir = path.join(runDirectory(id, config), "sub-slider-maps", measurementId);
  fs.mkdirSync(outputDir, { recursive: true, mode: 0o700 });
  const lockDir = path.join(config.stateRoot, "locks", "jdsp-host.lock");
  try {
    fs.mkdirSync(lockDir);
  } catch {
    throw new Error("Another real-host JDSP qualification is already active.");
  }
  try {
    const result = shell(
      "scripts/run_jdsp_sub_slider_map.py",
      [
        policy.acceptedBaseline.path,
        config.localMaterialManifest,
        outputDir,
        "--pulse-server", config.pulseServer,
        "--route-helper", config.routeHelper,
        "--threshold-db", String(policy.hostBaseline.masterLimiterThresholdDb),
      ],
      { cwd: config.repositoryRoot, timeout: 60 * 60 * 1000 }
    );
    const reportPath = path.join(outputDir, "sub_slider_map.json");
    let conclusion = result.exitCode === 0 ? "measurement_completed" : "fail";
    if (fs.existsSync(reportPath)) conclusion = loadJson(reportPath).evaluation.status;
    recordGate(run, {
      name: "accepted_sub_harmonics_dense_material_map",
      status: conclusion === "fail" ? "fail" : "pass",
      conclusion,
      exitCode: result.exitCode,
      reportPath,
      command: result.command,
      stdout: result.stdout.slice(-4000),
      stderr: result.stderr.slice(-4000)
    });
    return writeRun(run, config);
  } finally {
    fs.rmSync(lockDir, { recursive: true, force: true });
  }
}

export function runReserveLawScreen(id, config = loadLocalConfig(), policy = loadPolicy()) {
  const run = readRun(id, config);
  if (run.status !== "investigating" || run.candidate) {
    throw new Error("Reserve-law screening requires an investigation with no DSP candidate.");
  }
  if (!run.hypothesis || !run.listeningTarget) {
    throw new Error("Record a falsifiable hypothesis and listening target before host measurement.");
  }
  if (!fs.existsSync(config.localMaterialManifest)) {
    throw new Error("Configured local material manifest is unavailable.");
  }
  ensureLocalDirectories(config);
  const measurementId = isoNow().replace(/[-:]/g, "").replace(/\..*/, "");
  const outputDir = path.join(runDirectory(id, config), "reserve-law-screens", measurementId);
  fs.mkdirSync(outputDir, { recursive: true, mode: 0o700 });
  const lockDir = path.join(config.stateRoot, "locks", "jdsp-host.lock");
  try {
    fs.mkdirSync(lockDir);
  } catch {
    throw new Error("Another real-host JDSP qualification is already active.");
  }
  try {
    const result = shell(
      "scripts/run_jdsp_reserve_law_screen.py",
      [
        policy.acceptedBaseline.path,
        config.localMaterialManifest,
        outputDir,
        "--pulse-server", config.pulseServer,
        "--route-helper", config.routeHelper,
        "--threshold-db", String(policy.hostBaseline.masterLimiterThresholdDb),
      ],
      { cwd: config.repositoryRoot, timeout: 60 * 60 * 1000 }
    );
    const reportPath = path.join(outputDir, "reserve_law_screen.json");
    let conclusion = result.exitCode === 0 ? "measurement_completed" : "fail";
    if (fs.existsSync(reportPath)) conclusion = loadJson(reportPath).evaluation.status;
    recordGate(run, {
      name: "experimental_bass_reserve_law_screen",
      status: conclusion === "fail" ? "fail" : "pass",
      conclusion,
      exitCode: result.exitCode,
      reportPath,
      command: result.command,
      stdout: result.stdout.slice(-4000),
      stderr: result.stderr.slice(-4000)
    });
    return writeRun(run, config);
  } finally {
    fs.rmSync(lockDir, { recursive: true, force: true });
  }
}

export function runReserveRangeQualification(id, config = loadLocalConfig(), policy = loadPolicy()) {
  const run = readRun(id, config);
  if (run.status !== "investigating" || run.candidate) {
    throw new Error("Reserve-range qualification requires an investigation with no DSP candidate.");
  }
  if (!run.hypothesis || !run.listeningTarget) {
    throw new Error("Record a falsifiable hypothesis and listening target before host measurement.");
  }
  if (!fs.existsSync(config.localMaterialManifest)) {
    throw new Error("Configured local material manifest is unavailable.");
  }
  ensureLocalDirectories(config);
  const measurementId = isoNow().replace(/[-:]/g, "").replace(/\..*/, "");
  const outputDir = path.join(runDirectory(id, config), "reserve-range-qualifications", measurementId);
  fs.mkdirSync(outputDir, { recursive: true, mode: 0o700 });
  const lockDir = path.join(config.stateRoot, "locks", "jdsp-host.lock");
  try {
    fs.mkdirSync(lockDir);
  } catch {
    throw new Error("Another real-host JDSP qualification is already active.");
  }
  try {
    const result = shell(
      "scripts/run_jdsp_reserve_range_qualification.py",
      [
        policy.acceptedBaseline.path,
        config.localMaterialManifest,
        outputDir,
        "--pulse-server", config.pulseServer,
        "--route-helper", config.routeHelper,
        "--threshold-db", String(policy.hostBaseline.masterLimiterThresholdDb),
      ],
      { cwd: config.repositoryRoot, timeout: 60 * 60 * 1000 }
    );
    const reportPath = path.join(outputDir, "reserve_range_qualification.json");
    let conclusion = result.exitCode === 0 ? "measurement_completed" : "fail";
    if (fs.existsSync(reportPath)) conclusion = loadJson(reportPath).evaluation.status;
    recordGate(run, {
      name: "experimental_bass_reserve_range_qualification",
      status: conclusion === "fail" ? "fail" : "pass",
      conclusion,
      exitCode: result.exitCode,
      reportPath,
      command: result.command,
      stdout: result.stdout.slice(-4000),
      stderr: result.stderr.slice(-4000)
    });
    return writeRun(run, config);
  } finally {
    fs.rmSync(lockDir, { recursive: true, force: true });
  }
}

export function runStftStageAudit(id, config = loadLocalConfig(), policy = loadPolicy()) {
  const run = readRun(id, config);
  if (run.status !== "investigating" || run.candidate) {
    throw new Error("STFT stage audit requires an investigation with no DSP candidate.");
  }
  if (!run.hypothesis || !run.listeningTarget) {
    throw new Error("Record a falsifiable hypothesis and listening target before host measurement.");
  }
  ensureLocalDirectories(config);
  const measurementId = isoNow().replace(/[-:]/g, "").replace(/\..*/, "");
  const outputDir = path.join(runDirectory(id, config), "stft-audits", measurementId);
  fs.mkdirSync(outputDir, { recursive: true, mode: 0o700 });
  const lockDir = path.join(config.stateRoot, "locks", "jdsp-host.lock");
  try {
    fs.mkdirSync(lockDir);
  } catch {
    throw new Error("Another real-host JDSP qualification is already active.");
  }
  try {
    const result = shell(
      "scripts/run_jdsp_stft_audit.py",
      [
        policy.acceptedBaseline.path,
        outputDir,
        "--pulse-server", config.pulseServer,
        "--route-helper", config.routeHelper,
        "--master-limiter-threshold-db", String(policy.hostBaseline.masterLimiterThresholdDb),
      ],
      { cwd: config.repositoryRoot, timeout: 60 * 60 * 1000 }
    );
    const reportPath = path.join(outputDir, "stft_audit.json");
    let conclusion = result.exitCode === 0 ? "measurement_complete" : "fail";
    if (fs.existsSync(reportPath)) conclusion = loadJson(reportPath).status;
    recordGate(run, {
      name: "accepted_stft_stage_audit",
      status: conclusion === "fail" ? "fail" : "pass",
      conclusion,
      exitCode: result.exitCode,
      reportPath,
      command: result.command,
      stdout: result.stdout.slice(-4000),
      stderr: result.stderr.slice(-4000)
    });
    return writeRun(run, config);
  } finally {
    fs.rmSync(lockDir, { recursive: true, force: true });
  }
}

export function runWidthMonoAudit(id, config = loadLocalConfig(), policy = loadPolicy()) {
  const run = readRun(id, config);
  if (run.status !== "investigating" || run.candidate) {
    throw new Error("Width/mono audit requires an investigation with no DSP candidate.");
  }
  if (!run.hypothesis || !run.listeningTarget) {
    throw new Error("Record a falsifiable hypothesis and listening target before host measurement.");
  }
  ensureLocalDirectories(config);
  const measurementId = isoNow().replace(/[-:]/g, "").replace(/\..*/, "");
  const outputDir = path.join(runDirectory(id, config), "width-mono-audits", measurementId);
  fs.mkdirSync(outputDir, { recursive: true, mode: 0o700 });
  const lockDir = path.join(config.stateRoot, "locks", "jdsp-host.lock");
  try {
    fs.mkdirSync(lockDir);
  } catch {
    throw new Error("Another real-host JDSP qualification is already active.");
  }
  try {
    const result = shell(
      "scripts/run_jdsp_width_mono_audit.py",
      [
        policy.acceptedBaseline.path,
        outputDir,
        "--pulse-server", config.pulseServer,
        "--route-helper", config.routeHelper,
        "--master-limiter-threshold-db", String(policy.hostBaseline.masterLimiterThresholdDb),
      ],
      { cwd: config.repositoryRoot, timeout: 60 * 60 * 1000 }
    );
    const reportPath = path.join(outputDir, "width_mono_audit.json");
    let conclusion = result.exitCode === 0 ? "measurement_complete" : "fail";
    if (fs.existsSync(reportPath)) conclusion = loadJson(reportPath).evaluation.status;
    recordGate(run, {
      name: "accepted_width_mono_audit",
      status: conclusion === "fail" ? "fail" : "pass",
      conclusion,
      exitCode: result.exitCode,
      reportPath,
      command: result.command,
      stdout: result.stdout.slice(-4000),
      stderr: result.stderr.slice(-4000)
    });
    return writeRun(run, config);
  } finally {
    fs.rmSync(lockDir, { recursive: true, force: true });
  }
}

export function runWidthMaterialScreen(id, config = loadLocalConfig(), policy = loadPolicy()) {
  const run = readRun(id, config);
  if (run.status !== "investigating" || run.candidate) {
    throw new Error("Width material screen requires an investigation with no DSP candidate.");
  }
  if (!run.hypothesis || !run.listeningTarget) {
    throw new Error("Record a falsifiable hypothesis and listening target before host measurement.");
  }
  if (!fs.existsSync(config.localMaterialManifest)) {
    throw new Error("Configured local material manifest is unavailable.");
  }
  ensureLocalDirectories(config);
  const measurementId = isoNow().replace(/[-:]/g, "").replace(/\..*/, "");
  const outputDir = path.join(runDirectory(id, config), "width-material-screens", measurementId);
  fs.mkdirSync(outputDir, { recursive: true, mode: 0o700 });
  const lockDir = path.join(config.stateRoot, "locks", "jdsp-host.lock");
  try {
    fs.mkdirSync(lockDir);
  } catch {
    throw new Error("Another real-host JDSP qualification is already active.");
  }
  try {
    const result = shell(
      "scripts/run_jdsp_width_material_screen.py",
      [
        policy.acceptedBaseline.path,
        config.localMaterialManifest,
        outputDir,
        "--pulse-server", config.pulseServer,
        "--route-helper", config.routeHelper,
        "--master-limiter-threshold-db", String(policy.hostBaseline.masterLimiterThresholdDb),
      ],
      { cwd: config.repositoryRoot, timeout: 60 * 60 * 1000 }
    );
    const reportPath = path.join(outputDir, "width_material_screen.json");
    let conclusion = result.exitCode === 0 ? "measurement_complete" : "fail";
    if (fs.existsSync(reportPath)) conclusion = loadJson(reportPath).evaluation.status;
    recordGate(run, {
      name: "accepted_width_material_screen",
      status: conclusion === "fail" ? "fail" : "pass",
      conclusion,
      exitCode: result.exitCode,
      reportPath,
      command: result.command,
      stdout: result.stdout.slice(-4000),
      stderr: result.stderr.slice(-4000)
    });
    return writeRun(run, config);
  } finally {
    fs.rmSync(lockDir, { recursive: true, force: true });
  }
}

export function runLowMidWidthScreen(id, config = loadLocalConfig(), policy = loadPolicy()) {
  const run = readRun(id, config);
  if (run.status !== "investigating" || run.candidate) {
    throw new Error("Low-mid width screen requires an investigation with no DSP candidate.");
  }
  if (!run.hypothesis || !run.listeningTarget) {
    throw new Error("Record a falsifiable hypothesis and listening target before host measurement.");
  }
  if (!fs.existsSync(config.localMaterialManifest)) {
    throw new Error("Configured local material manifest is unavailable.");
  }
  ensureLocalDirectories(config);
  const measurementId = isoNow().replace(/[-:]/g, "").replace(/\..*/, "");
  const outputDir = path.join(runDirectory(id, config), "lowmid-width-screens", measurementId);
  fs.mkdirSync(outputDir, { recursive: true, mode: 0o700 });
  const lockDir = path.join(config.stateRoot, "locks", "jdsp-host.lock");
  try {
    fs.mkdirSync(lockDir);
  } catch {
    throw new Error("Another real-host JDSP qualification is already active.");
  }
  try {
    const result = shell(
      "scripts/run_jdsp_lowmid_width_screen.py",
      [
        policy.acceptedBaseline.path,
        config.localMaterialManifest,
        outputDir,
        "--pulse-server", config.pulseServer,
        "--route-helper", config.routeHelper,
        "--master-limiter-threshold-db", String(policy.hostBaseline.masterLimiterThresholdDb),
      ],
      { cwd: config.repositoryRoot, timeout: 60 * 60 * 1000 }
    );
    const reportPath = path.join(outputDir, "lowmid_width_screen.json");
    let conclusion = result.exitCode === 0 ? "measurement_complete" : "fail";
    if (fs.existsSync(reportPath)) conclusion = loadJson(reportPath).evaluation.status;
    recordGate(run, {
      name: "experimental_lowmid_width_screen",
      status: conclusion === "fail" ? "fail" : "pass",
      conclusion,
      exitCode: result.exitCode,
      reportPath,
      command: result.command,
      stdout: result.stdout.slice(-4000),
      stderr: result.stderr.slice(-4000)
    });
    return writeRun(run, config);
  } finally {
    fs.rmSync(lockDir, { recursive: true, force: true });
  }
}

export function listRuns(config = loadLocalConfig()) {
  const root = path.join(config.stateRoot, "runs");
  if (!fs.existsSync(root)) return [];
  return fs.readdirSync(root).map((id) => {
    try { return readRun(id, config); } catch { return null; }
  }).filter(Boolean).sort((a, b) => b.updatedAt.localeCompare(a.updatedAt));
}

function validateVersion(version, policy) {
  if (!/^v\d+\.\d+\.\d+(?:\.\d+)*$/.test(version)) throw new Error("Candidate version must look like v4.1.4.9.");
  if (version === policy.acceptedBaseline.version) throw new Error("Candidate version cannot overwrite the accepted baseline.");
}

export function createCandidate(id, version, config = loadLocalConfig(), policy = loadPolicy()) {
  const run = readRun(id, config);
  if (run.status !== "investigating") throw new Error("Candidate can be created only from an investigation.");
  if (!run.hypothesis || !run.listeningTarget) throw new Error("Set a hypothesis and listening target before creating a candidate.");
  validateVersion(version, policy);
  ensureLocalDirectories(config);
  const worktree = path.join(config.worktreeRoot, id);
  const branch = `axiom/experiment/${slug(id)}`;
  if (fs.existsSync(worktree)) throw new Error(`Candidate worktree already exists: ${worktree}`);
  requireSuccess(shell("git", ["fetch", "origin", policy.project.defaultBranch], { cwd: config.repositoryRoot }), "fetch baseline branch");
  requireSuccess(shell("git", ["worktree", "add", "-b", branch, worktree, `origin/${policy.project.defaultBranch}`], { cwd: config.repositoryRoot }), "create candidate worktree");
  const relativePath = `src/axiom_binaural_dsp_${version}.eel`;
  fs.copyFileSync(path.join(worktree, policy.acceptedBaseline.path), path.join(worktree, relativePath));
  run.candidate = { version, path: relativePath, branch, worktree, sha256: sha256(path.join(worktree, relativePath)), commit: null, commits: [] };
  run.status = "candidate_created";
  return writeRun(run, config);
}

function permittedMutationPath(run, relativePath, area, policy) {
  const normalized = relativePath.replaceAll("\\", "/").replace(/^\.?\//, "");
  if (normalized === policy.acceptedBaseline.path) return false;
  if (area === "candidate-eel") return normalized === run.candidate?.path;
  if (area === "tooling") return /^(scripts|tests|tools\/axiom-team)\//.test(normalized);
  if (area === "documentation") return /^(README\.md|AGENTS\.md|CONTRIBUTING\.md|CHANGELOG\.md|docs\/|presets\/|\.gitignore$|tools\/axiom-team\/policy\.json$)/.test(normalized);
  return false;
}

export function writeScopedFile(id, relativePath, area, content, config = loadLocalConfig(), policy = loadPolicy()) {
  const run = readRun(id, config);
  const editableCodeStates = ["candidate_created", "implementing", "failed", "pass_with_investigation"];
  const editableDocumentationStates = [...editableCodeStates, "ready_for_listening", "listening_accepted"];
  const states = area === "documentation" ? editableDocumentationStates : editableCodeStates;
  if (!run.candidate?.worktree || !states.includes(run.status)) {
    throw new Error("Controlled edits require an active unpublished candidate worktree.");
  }
  if (!permittedMutationPath(run, relativePath, area, policy)) throw new Error(`Write blocked outside approved ${area} scope: ${relativePath}`);
  const absolute = path.resolve(run.candidate.worktree, relativePath);
  if (!absolute.startsWith(path.resolve(run.candidate.worktree) + path.sep)) throw new Error("Write path escapes candidate worktree.");
  fs.mkdirSync(path.dirname(absolute), { recursive: true });
  fs.writeFileSync(absolute, content, "utf8");
  if (relativePath === run.candidate.path) run.candidate.sha256 = sha256(absolute);
  if (area !== "documentation" || !["ready_for_listening", "listening_accepted"].includes(run.status)) {
    run.status = "implementing";
  }
  return writeRun(run, config);
}

export function runAutomatedValidation(id, options = {}, config = loadLocalConfig(), policy = loadPolicy()) {
  const run = readRun(id, config);
  if (!run.candidate?.worktree) throw new Error("Qualification requires a candidate worktree.");
  const root = run.candidate.worktree;
  const outputDir = path.join(runDirectory(id, config), "qualification");
  fs.mkdirSync(outputDir, { recursive: true, mode: 0o700 });
  run.status = "automated_validation";
  const tests = shell("python3", ["-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py"], { cwd: root });
  const staticGate = shell("scripts/validate_axiom_static.sh", [run.candidate.path], { cwd: root });
  recordCommandGate(run, "python_unit_suite", tests, outputDir);
  recordCommandGate(run, "candidate_eel_static_validation", staticGate, outputDir);
  if (tests.exitCode !== 0 || staticGate.exitCode !== 0) {
    run.status = "failed";
    return writeRun(run, config);
  }
  if (options.skipHost) {
    recordGate(run, { name: "managed_jdsp_qualification", status: "skipped", detail: "Host qualification explicitly skipped; candidate cannot advance to listening." });
    run.status = "automated_validation";
    return writeRun(run, config);
  }
  if (policy.requiredLocalMaterial && !fs.existsSync(config.localMaterialManifest)) {
    recordGate(run, { name: "registered_local_material", status: "fail", detail: "Configured local material manifest is unavailable." });
    run.status = "blocked";
    return writeRun(run, config);
  }
  const lockDir = path.join(config.stateRoot, "locks", "jdsp-host.lock");
  try {
    fs.mkdirSync(lockDir);
  } catch {
    throw new Error("Another real-host JDSP qualification is already active.");
  }
  try {
    const args = [
      path.join(root, policy.acceptedBaseline.path),
      path.join(root, run.candidate.path),
      outputDir,
      "--pulse-server", config.pulseServer,
      "--route-helper", config.routeHelper,
      "--master-limiter-threshold-db", String(policy.hostBaseline.masterLimiterThresholdDb),
      "--local-material-manifest", config.localMaterialManifest
    ];
    const host = shell("scripts/run_jdsp_wsl_qualification.py", args, { cwd: root, timeout: 60 * 60 * 1000 });
    let normalizedStatus = host.exitCode === 0 ? "pass" : "fail";
    const reportPath = path.join(outputDir, "qualification.json");
    if (fs.existsSync(reportPath)) normalizedStatus = loadJson(reportPath).status;
    recordGate(run, {
      name: "managed_jdsp_qualification",
      status: normalizedStatus,
      exitCode: host.exitCode,
      reportPath,
      command: host.command,
      stdout: host.stdout.slice(-4000),
      stderr: host.stderr.slice(-4000)
    });
    run.status = normalizedStatus === "fail" ? "failed" :
      normalizedStatus === "pass_with_investigation" ? "pass_with_investigation" : "ready_for_listening";
  } finally {
    fs.rmSync(lockDir, { recursive: true, force: true });
  }
  return writeRun(run, config);
}

export function runLowMidWidthCandidateQualification(id, options = {}, config = loadLocalConfig(), policy = loadPolicy()) {
  const run = readRun(id, config);
  if (!run.candidate?.worktree) throw new Error("Low-mid width candidate qualification requires a candidate worktree.");
  const root = run.candidate.worktree;
  const outputDir = path.join(runDirectory(id, config), "lowmid-candidate-qualification");
  fs.mkdirSync(outputDir, { recursive: true, mode: 0o700 });
  run.status = "automated_validation";
  const tests = shell("python3", ["-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py"], { cwd: root });
  const staticGate = shell("scripts/validate_axiom_static.sh", [run.candidate.path], { cwd: root });
  recordCommandGate(run, "python_unit_suite", tests, outputDir);
  recordCommandGate(run, "candidate_eel_static_validation", staticGate, outputDir);
  if (tests.exitCode !== 0 || staticGate.exitCode !== 0) {
    run.status = "failed";
    return writeRun(run, config);
  }
  if (options.skipHost) {
    recordGate(run, { name: "managed_lowmid_width_candidate_qualification", status: "skipped", detail: "Host qualification explicitly skipped; candidate cannot advance to listening." });
    return writeRun(run, config);
  }
  if (policy.requiredLocalMaterial && !fs.existsSync(config.localMaterialManifest)) {
    recordGate(run, { name: "registered_local_material", status: "fail", detail: "Configured local material manifest is unavailable." });
    run.status = "blocked";
    return writeRun(run, config);
  }
  const lockDir = path.join(config.stateRoot, "locks", "jdsp-host.lock");
  try {
    fs.mkdirSync(lockDir);
  } catch {
    throw new Error("Another real-host JDSP qualification is already active.");
  }
  try {
    const host = shell(
      "scripts/run_jdsp_lowmid_width_candidate_qualification.py",
      [
        path.join(root, policy.acceptedBaseline.path),
        path.join(root, run.candidate.path),
        config.localMaterialManifest,
        outputDir,
        "--pulse-server", config.pulseServer,
        "--route-helper", config.routeHelper,
        "--master-limiter-threshold-db", String(policy.hostBaseline.masterLimiterThresholdDb),
      ],
      { cwd: root, timeout: 60 * 60 * 1000 }
    );
    let normalizedStatus = host.exitCode === 0 ? "pass" : "fail";
    const reportPath = path.join(outputDir, "lowmid_candidate_qualification.json");
    if (fs.existsSync(reportPath)) normalizedStatus = loadJson(reportPath).evaluation.status;
    recordGate(run, {
      name: "managed_lowmid_width_candidate_qualification",
      status: normalizedStatus,
      exitCode: host.exitCode,
      reportPath,
      command: host.command,
      stdout: host.stdout.slice(-4000),
      stderr: host.stderr.slice(-4000)
    });
    run.status = normalizedStatus === "fail" ? "failed" :
      normalizedStatus === "pass_with_investigation" ? "pass_with_investigation" : "ready_for_listening";
  } finally {
    fs.rmSync(lockDir, { recursive: true, force: true });
  }
  return writeRun(run, config);
}

export function recordListening(id, decision, notes, config = loadLocalConfig()) {
  const run = readRun(id, config);
  if (!["ready_for_listening", "pass_with_investigation"].includes(run.status)) throw new Error("Listening can be recorded only after automated gates permit it.");
  if (!["accept", "reject"].includes(decision)) throw new Error("Listening decision must be accept or reject.");
  run.approvals.listening = { decision, notes: notes || "", timestamp: isoNow(), authority: "user" };
  run.status = decision === "accept" ? "listening_accepted" : "listening_rejected";
  return writeRun(run, config);
}

function changedPaths(worktree) {
  const output = requireSuccess(shell("git", ["status", "--porcelain"], { cwd: worktree }), "read candidate status").stdout;
  return output.split("\n").filter(Boolean).map((line) => line.slice(3).trim()).filter(Boolean);
}

export function commitCandidate(id, message, config = loadLocalConfig(), policy = loadPolicy()) {
  const run = readRun(id, config);
  if (!run.candidate?.worktree) throw new Error("No candidate worktree exists.");
  if (!["ready_for_listening", "pass_with_investigation", "listening_accepted"].includes(run.status)) {
    throw new Error("Commit requires completed real-host qualification, or accepted-listening documentation follow-up.");
  }
  const paths = changedPaths(run.candidate.worktree);
  if (!paths.length) throw new Error("Candidate worktree has no changes to commit.");
  const outside = paths.filter((filename) =>
    !permittedMutationPath(run, filename, "candidate-eel", policy) &&
    !permittedMutationPath(run, filename, "tooling", policy) &&
    !permittedMutationPath(run, filename, "documentation", policy));
  if (outside.length) throw new Error(`Commit blocked by unexpected paths: ${outside.join(", ")}`);
  requireSuccess(shell("git", ["add", "--", ...paths], { cwd: run.candidate.worktree }), "stage controlled candidate changes");
  requireSuccess(shell("git", ["commit", "-m", message || `feat(dsp): add ${run.candidate.version} candidate`], { cwd: run.candidate.worktree }), "commit candidate");
  run.candidate.commit = requireSuccess(shell("git", ["rev-parse", "HEAD"], { cwd: run.candidate.worktree }), "read candidate commit").stdout.trim();
  run.candidate.commits = [...(run.candidate.commits || []), run.candidate.commit];
  return writeRun(run, config);
}

export function approvePublication(id, config = loadLocalConfig()) {
  const run = readRun(id, config);
  if (run.status !== "listening_accepted") throw new Error("Publication requires accepted human listening evidence.");
  if (!run.candidate?.commit) throw new Error("Commit the accepted candidate branch locally before publication.");
  if (changedPaths(run.candidate.worktree).length) throw new Error("Commit release evidence before approving publication.");
  requireReleaseDocuments(run);
  run.approvals.publication = { timestamp: isoNow(), authority: "user" };
  run.status = "publication_approved";
  return writeRun(run, config);
}

function requireReleaseDocuments(run) {
  const root = run.candidate.worktree;
  const candidatePolicyPath = path.join(root, "tools", "axiom-team", "policy.json");
  const candidateChangelogPath = path.join(root, "CHANGELOG.md");
  const qualificationPath = path.join(root, "docs", `qualification-${run.candidate.version}.md`);
  if (!fs.existsSync(candidatePolicyPath) || !fs.existsSync(candidateChangelogPath) || !fs.existsSync(qualificationPath)) {
    throw new Error(`Publication requires candidate policy, CHANGELOG entry, and docs/qualification-${run.candidate.version}.md.`);
  }
  const candidatePolicy = loadJson(candidatePolicyPath);
  const digest = sha256(path.join(root, run.candidate.path));
  const accepted = candidatePolicy.acceptedBaseline || {};
  if (accepted.version !== run.candidate.version || accepted.path !== run.candidate.path || accepted.sha256 !== digest) {
    throw new Error("Publication requires policy.json to designate the qualified candidate path and hash as the proposed accepted baseline.");
  }
  if (!fs.readFileSync(candidateChangelogPath, "utf8").includes(run.candidate.version.replace(/^v/, ""))) {
    throw new Error("Publication requires a CHANGELOG entry for the candidate version.");
  }
}

export function publishPullRequest(id, config = loadLocalConfig(), policy = loadPolicy()) {
  const run = readRun(id, config);
  if (run.status !== "publication_approved") throw new Error("Publication approval has not been recorded.");
  if (changedPaths(run.candidate.worktree).length) throw new Error("Candidate worktree must be clean before publication.");
  requireReleaseDocuments(run);
  requireSuccess(shell("git", ["push", "-u", "origin", run.candidate.branch], { cwd: run.candidate.worktree }), "push candidate branch");
  const title = `[axiom] Evaluate ${run.candidate.version} candidate`;
  const body = [
    `## Hypothesis\n\n${run.hypothesis}`,
    `\n## Listening target\n\n${run.listeningTarget}`,
    `\n## Evidence\n\nAutomated gates and human listening acceptance are recorded locally for run \`${run.id}\`. Public evidence documents are included in this branch when applicable.`
  ].join("\n");
  const pr = requireSuccess(shell("gh", ["pr", "create", "--repo", policy.project.repository, "--base", policy.project.defaultBranch, "--head", run.candidate.branch, "--draft", "--title", title, "--body", body], { cwd: run.candidate.worktree }), "create draft PR");
  run.pullRequest = { url: pr.stdout.trim(), title, createdAt: isoNow() };
  run.status = "pull_request_open";
  return writeRun(run, config);
}

export function approveMerge(id, config = loadLocalConfig()) {
  const run = readRun(id, config);
  if (run.status !== "pull_request_open") throw new Error("Merge approval requires an open published PR.");
  run.approvals.merge = { timestamp: isoNow(), authority: "user" };
  run.status = "merge_approved";
  return writeRun(run, config);
}

export function mergePullRequest(id, config = loadLocalConfig(), policy = loadPolicy()) {
  const run = readRun(id, config);
  if (run.status !== "merge_approved") throw new Error("Merge approval has not been recorded.");
  requireSuccess(shell("gh", ["pr", "merge", run.pullRequest.url, "--merge"], { cwd: run.candidate.worktree }), "merge approved PR");
  requireSuccess(shell("git", ["fetch", "origin", policy.project.defaultBranch], { cwd: config.repositoryRoot }), "refresh merged main");
  run.status = "baseline_merged";
  return writeRun(run, config);
}

export function renderSummary(run) {
  const lines = [
    `Run: ${run.id}`,
    `Status: ${run.status}`,
    `Observation: ${run.observation}`,
    `Baseline: ${run.baseline.version} ${run.baseline.sha256}`,
    `Candidate: ${run.candidate ? `${run.candidate.version} (${run.candidate.branch})` : "none"}`,
    `Hypothesis: ${run.hypothesis || "not recorded"}`,
    `Listening target: ${run.listeningTarget || "not recorded"}`,
    `Gates: ${run.gates.map((gate) => `${gate.name}=${gate.status}`).join(", ") || "none"}`
  ];
  return lines.join("\n");
}
