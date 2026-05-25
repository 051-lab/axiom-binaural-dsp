import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";
import { Type } from "typebox";
import { execFileSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import {
  approveMerge,
  approvePublication,
  auditBaseline,
  commitCandidate,
  createCandidate,
  createInvestigation,
  doctor,
  listRuns,
  loadLocalConfig,
  loadPolicy,
  mergePullRequest,
  publishPullRequest,
  readRun,
  recordListening,
  renderSummary,
  repositoryRoot,
  runAutomatedValidation,
  runBaselineLimiterSweep,
  setHypothesis,
  writeScopedFile,
} from "../lib/core.mjs";

const extensionRoot = path.dirname(fileURLToPath(import.meta.url));
const harnessRoot = path.resolve(extensionRoot, "..");
const rolesRoot = path.join(harnessRoot, "roles");
const roleNames = [
  "dsp-architect",
  "signal-researcher",
  "implementation-lead",
  "eel-engineer",
  "tooling-engineer",
  "qualification-lead",
  "measurement-engineer",
  "safety-auditor",
  "release-steward",
];
const costLimits = loadPolicy().costLimits;
let sessionCostUsd = 0;
let softLimitReported = false;

function text(value: unknown) {
  return {
    content: [{ type: "text" as const, text: typeof value === "string" ? value : JSON.stringify(value, null, 2) }],
    details: value,
  };
}

function withinRepository(relativePath: string) {
  const filename = path.resolve(repositoryRoot, relativePath);
  if (!filename.startsWith(repositoryRoot + path.sep)) throw new Error("Path escapes the Axiom repository.");
  return filename;
}

function trackedRepositoryFile(relativePath: string) {
  const filename = withinRepository(relativePath);
  execFileSync("git", ["ls-files", "--error-unmatch", "--", relativePath], { cwd: repositoryRoot, encoding: "utf8", timeout: 10000 });
  return filename;
}

function statusText() {
  const runs = listRuns();
  return runs.length ? runs.slice(0, 8).map(renderSummary).join("\n\n") : "No Axiom harness runs recorded.";
}

function parsePipeArgs(args: string, expected: number) {
  const values = args.split("|").map((part) => part.trim());
  if (values.length < expected || values.slice(0, expected).some((part) => !part)) {
    throw new Error("Arguments must be non-empty fields separated by `|`.");
  }
  return values;
}

function consultRole(role: string, task: string) {
  if (!roleNames.includes(role)) throw new Error(`Unknown role: ${role}`);
  const prompt = fs.readFileSync(path.join(rolesRoot, `${role}.md`), "utf8");
  const args = [
    "--no-extensions",
    "--no-skills",
    "--no-prompt-templates",
    "--no-session",
    "--tools", "read,grep,find,ls",
    "--append-system-prompt", prompt,
    "--print",
    task,
  ];
  const model = process.env.AXIOM_PI_ROLE_MODEL;
  if (model) args.unshift("--model", model);
  return execFileSync("pi", args, { cwd: repositoryRoot, encoding: "utf8", timeout: 15 * 60 * 1000 });
}

export default function (pi: ExtensionAPI) {
  function requireBudget(action: string) {
    if (sessionCostUsd >= costLimits.hardUsd) {
      throw new Error(`Session hard cost limit of $${costLimits.hardUsd.toFixed(2)} reached; ${action} is blocked until a new reviewed session.`);
    }
  }

  pi.on("before_agent_start", async (event) => {
    return {
      systemPrompt: event.systemPrompt + "\n\nAxiom run state:\n" + statusText() +
        "\n\nSpecialist roles available through `axiom_consult_role`: " + roleNames.join(", ") + "." +
        `\nSession agent cost: $${sessionCostUsd.toFixed(4)}; soft limit $${costLimits.softUsd.toFixed(2)}, hard limit $${costLimits.hardUsd.toFixed(2)}.`,
    };
  });
  pi.on("message_end", async (event, ctx) => {
    const message: any = event.message;
    if (message.role === "assistant") {
      sessionCostUsd += Number(message.usage?.cost?.total || 0);
      ctx.ui.setStatus("axiom-budget", `Axiom cost $${sessionCostUsd.toFixed(4)} / $${costLimits.hardUsd.toFixed(2)}`);
      if (!softLimitReported && sessionCostUsd >= costLimits.softUsd) {
        softLimitReported = true;
        ctx.ui.notify(`Axiom session soft cost limit reached: $${sessionCostUsd.toFixed(4)}. Continue only for decision-grade work.`, "warning");
      }
      if (sessionCostUsd >= costLimits.hardUsd) {
        ctx.ui.notify(`Axiom session hard cost limit reached: $${sessionCostUsd.toFixed(4)}. Agent delegation and mutations are blocked.`, "error");
      }
    }
  });

  pi.registerTool({
    name: "axiom_doctor",
    label: "Axiom Doctor",
    description: "Check the local Axiom repository, accepted baseline identity, JDSP tooling, and registered external material.",
    parameters: Type.Object({}),
    async execute() { return text(doctor()); },
  });

  pi.registerTool({
    name: "axiom_status",
    label: "Axiom Status",
    description: "Show current controlled engineering runs and their gate states.",
    parameters: Type.Object({}),
    async execute() { return text(statusText()); },
  });

  pi.registerTool({
    name: "axiom_read_project_file",
    label: "Read Axiom File",
    description: "Read a tracked text file from the Axiom repository only.",
    parameters: Type.Object({ path: Type.String({ description: "Tracked repository-relative text file path" }) }),
    async execute(_id, params) {
      const filename = trackedRepositoryFile(params.path);
      return text(fs.readFileSync(filename, "utf8"));
    },
  });

  pi.registerTool({
    name: "axiom_read_candidate_file",
    label: "Read Candidate File",
    description: "Read the controlled versioned EEL candidate in a recorded external worktree.",
    parameters: Type.Object({ runId: Type.String() }),
    async execute(_id, params) {
      const run = readRun(params.runId);
      if (!run.candidate?.path || !run.candidate?.worktree) throw new Error("Run has no candidate worktree.");
      const worktree = path.resolve(run.candidate.worktree);
      const filename = path.resolve(worktree, run.candidate.path);
      if (!filename.startsWith(worktree + path.sep)) throw new Error("Candidate path escapes its worktree.");
      return text(fs.readFileSync(filename, "utf8"));
    },
  });

  pi.registerTool({
    name: "axiom_search_project",
    label: "Search Axiom",
    description: "Search tracked Axiom repository text without mutation.",
    parameters: Type.Object({ query: Type.String(), glob: Type.Optional(Type.String()) }),
    async execute(_id, params) {
      const args = ["grep", "-n"];
      args.push("-e", params.query, "--");
      if (params.glob) {
        if (params.glob.startsWith("-") || path.isAbsolute(params.glob) || params.glob.includes("..")) {
          throw new Error("Search pathspec must remain inside the tracked Axiom repository.");
        }
        args.push(params.glob);
      }
      try {
        const output = execFileSync("git", args, { cwd: repositoryRoot, encoding: "utf8", timeout: 10000 });
        return text(output.slice(0, 30000));
      } catch (error: any) {
        if (error.status === 1) return text("No matches.");
        throw error;
      }
    },
  });

  pi.registerTool({
    name: "axiom_consult_role",
    label: "Consult Specialist",
    description: "Run a read-only specialist consultation inside the Axiom repository.",
    parameters: Type.Object({ role: Type.String(), task: Type.String() }),
    async execute(_id, params) {
      requireBudget("specialist consultation");
      return text(consultRole(params.role, params.task));
    },
  });

  pi.registerTool({
    name: "axiom_investigate",
    label: "Open Investigation",
    description: "Create a local investigation record anchored to the verified accepted baseline.",
    parameters: Type.Object({ observation: Type.String() }),
    async execute(_id, params) {
      requireBudget("investigation creation");
      return text(renderSummary(createInvestigation(params.observation)));
    },
  });

  pi.registerTool({
    name: "axiom_set_hypothesis",
    label: "Set Hypothesis",
    description: "Record a falsifiable hypothesis and listening target before any candidate exists.",
    parameters: Type.Object({ runId: Type.String(), hypothesis: Type.String(), listeningTarget: Type.String() }),
    async execute(_id, params) {
      requireBudget("hypothesis mutation");
      return text(renderSummary(setHypothesis(params.runId, params.hypothesis, params.listeningTarget)));
    },
  });

  pi.registerTool({
    name: "axiom_create_candidate",
    label: "Create Candidate",
    description: "Create an external git worktree and a new versioned EEL candidate copied from the accepted baseline.",
    parameters: Type.Object({ runId: Type.String(), version: Type.String() }),
    async execute(_id, params) {
      requireBudget("candidate creation");
      return text(renderSummary(createCandidate(params.runId, params.version)));
    },
  });

  pi.registerTool({
    name: "axiom_write_scoped_file",
    label: "Write Candidate File",
    description: "Write only a controlled candidate EEL, harness/tooling, or documentation path in an active candidate worktree.",
    parameters: Type.Object({
      runId: Type.String(),
      area: Type.Union([Type.Literal("candidate-eel"), Type.Literal("tooling"), Type.Literal("documentation")]),
      path: Type.String(),
      content: Type.String(),
    }),
    async execute(_id, params) {
      requireBudget("candidate write");
      return text(renderSummary(writeScopedFile(params.runId, params.path, params.area, params.content)));
    },
  });

  pi.registerTool({
    name: "axiom_measure_baseline_limiter",
    label: "Measure Baseline Limiter",
    description: "Run the serialized real-JDSP limiter-threshold sweep on accepted .8 for a hypothesis-bearing investigation without creating a candidate.",
    parameters: Type.Object({ runId: Type.String() }),
    async execute(_id, params) { return text(renderSummary(runBaselineLimiterSweep(params.runId))); },
  });

  pi.registerTool({
    name: "axiom_qualify_candidate",
    label: "Qualify Candidate",
    description: "Run unit/static validation and serialized real-JDSP qualification for a candidate.",
    parameters: Type.Object({ runId: Type.String() }),
    async execute(_id, params) { return text(renderSummary(runAutomatedValidation(params.runId))); },
  });

  pi.registerTool({
    name: "axiom_commit_candidate",
    label: "Commit Qualified Candidate",
    description: "Commit controlled candidate changes only after real-host qualification permits review.",
    parameters: Type.Object({ runId: Type.String(), message: Type.Optional(Type.String()) }),
    async execute(_id, params) {
      requireBudget("candidate commit");
      return text(renderSummary(commitCandidate(params.runId, params.message)));
    },
  });

  pi.registerCommand("axiom-doctor", {
    description: "Check Axiom harness prerequisites and baseline identity.",
    handler: async (_args, ctx) => ctx.ui.notify(JSON.stringify(doctor(), null, 2), "info"),
  });
  pi.registerCommand("axiom-status", {
    description: "Show controlled engineering runs.",
    handler: async (_args, ctx) => ctx.ui.notify(statusText(), "info"),
  });
  pi.registerCommand("axiom-audit-baseline", {
    description: "Audit accepted .8 without creating a DSP candidate.",
    handler: async (_args, ctx) => ctx.ui.notify(renderSummary(auditBaseline()), "info"),
  });
  pi.registerCommand("axiom-measure-limiter", {
    description: "Usage: /axiom-measure-limiter run-id; capture accepted .8 across host limiter thresholds.",
    handler: async (args, ctx) => ctx.ui.notify(renderSummary(runBaselineLimiterSweep(args.trim())), "info"),
  });
  pi.registerCommand("axiom-investigate", {
    description: "Usage: /axiom-investigate <observation>",
    handler: async (args, ctx) => ctx.ui.notify(renderSummary(createInvestigation(args.trim())), "info"),
  });
  pi.registerCommand("axiom-hypothesis", {
    description: "Usage: /axiom-hypothesis run-id | hypothesis | listening target",
    handler: async (args, ctx) => {
      const [runId, hypothesis, target] = parsePipeArgs(args, 3);
      ctx.ui.notify(renderSummary(setHypothesis(runId, hypothesis, target)), "info");
    },
  });
  pi.registerCommand("axiom-create-candidate", {
    description: "Usage: /axiom-create-candidate run-id | v4.1.4.9",
    handler: async (args, ctx) => {
      const [runId, version] = parsePipeArgs(args, 2);
      ctx.ui.notify(renderSummary(createCandidate(runId, version)), "info");
    },
  });
  pi.registerCommand("axiom-qualify", {
    description: "Usage: /axiom-qualify run-id",
    handler: async (args, ctx) => ctx.ui.notify(renderSummary(runAutomatedValidation(args.trim())), "info"),
  });
  pi.registerCommand("axiom-listening-package", {
    description: "Usage: /axiom-listening-package run-id",
    handler: async (args, ctx) => {
      const run = readRun(args.trim());
      const config = loadLocalConfig();
      ctx.ui.notify(renderSummary(run) + `\nEvidence: ${path.join(config.stateRoot, "runs", run.id, "qualification")}`, "info");
    },
  });
  pi.registerCommand("axiom-record-listening", {
    description: "Usage: /axiom-record-listening run-id | accept/reject | notes",
    handler: async (args, ctx) => {
      const [runId, decision, notes = ""] = parsePipeArgs(args, 2);
      ctx.ui.notify(renderSummary(recordListening(runId, decision, notes)), "info");
    },
  });
  pi.registerCommand("axiom-commit", {
    description: "Usage: /axiom-commit run-id | commit message",
    handler: async (args, ctx) => {
      const [runId, message = ""] = parsePipeArgs(args, 1);
      ctx.ui.notify(renderSummary(commitCandidate(runId, message || undefined)), "info");
    },
  });
  pi.registerCommand("axiom-publish", {
    description: "Usage: /axiom-publish run-id; requires explicit publication confirmation.",
    handler: async (args, ctx) => {
      const runId = args.trim();
      const ok = await ctx.ui.confirm("Publish Axiom Candidate", "Push this accepted candidate branch and open a draft pull request?");
      if (!ok) return ctx.ui.notify("Publication cancelled.", "warning");
      approvePublication(runId);
      ctx.ui.notify(renderSummary(publishPullRequest(runId)), "info");
    },
  });
  pi.registerCommand("axiom-merge", {
    description: "Usage: /axiom-merge run-id; requires separate explicit merge confirmation.",
    handler: async (args, ctx) => {
      const runId = args.trim();
      const ok = await ctx.ui.confirm("Merge Axiom Candidate", "Merge the approved pull request into the accepted baseline branch?");
      if (!ok) return ctx.ui.notify("Merge cancelled.", "warning");
      approveMerge(runId);
      ctx.ui.notify(renderSummary(mergePullRequest(runId)), "info");
    },
  });
}
