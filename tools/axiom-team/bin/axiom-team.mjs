#!/usr/bin/env node
import {
  approveMerge, approvePublication, auditBaseline, commitCandidate, createCandidate,
  createInvestigation, doctor, listRuns, loadLocalConfig, mergePullRequest,
  publishPullRequest, readRun, recordListening, renderSummary, runAutomatedValidation,
  runAcceptedStressBaseline, runBaselineLimiterSweep, runReserveLawScreen, runReserveRangeQualification,
  runExciterProbeScreen, runExciterSensitivityScreen, runHighWidthScreen, runLowMidWidthCandidateQualification, runLowMidWidthScreen, runStageObservability, runStftStageAudit, runSubSliderMap, runWidthMaterialScreen, runWidthMonoAudit,
  saveLocalConfig, setHypothesis, validateMaterialManifest
} from "../lib/core.mjs";

function out(value) {
  process.stdout.write((typeof value === "string" ? value : JSON.stringify(value, null, 2)) + "\n");
}

function required(value, label) {
  if (!value) throw new Error(`Missing ${label}.`);
  return value;
}

function numeric(value, label) {
  const parsed = Number(required(value, label));
  if (!Number.isFinite(parsed)) throw new Error(`${label} must be numeric.`);
  return parsed;
}

function parseSubSliderMapArgs(args) {
  const id = required(args[0], "run id");
  const options = { sliderValuesDb: [] };
  for (let i = 1; i < args.length; i += 1) {
    const arg = args[i];
    if (arg === "--slider-db") {
      options.sliderValuesDb.push(numeric(args[++i], "--slider-db value"));
    } else if (arg === "--label-regex") {
      options.labelRegex = required(args[++i], "--label-regex value");
    } else if (arg === "--repetitions") {
      options.repetitions = numeric(args[++i], "--repetitions value");
    } else {
      throw new Error(`Unknown map-sub-gain option: ${arg}`);
    }
  }
  if (!options.sliderValuesDb.length) delete options.sliderValuesDb;
  return { id, options };
}

async function main() {
  const [command, ...args] = process.argv.slice(2);
  switch (command) {
    case "init":
      out(`Local configuration written: ${saveLocalConfig(loadLocalConfig())}`);
      return;
    case "doctor":
      {
        const result = doctor();
        out(result);
        process.exitCode = result.status === "pass" ? 0 : 1;
      }
      return;
    case "corpus-status":
      {
        const result = validateMaterialManifest(loadLocalConfig(), {
          strictMetadata: args.includes("--strict-metadata"),
          allowMissingPaths: args.includes("--allow-missing-paths"),
        });
        out(result);
        process.exitCode = result.status === "fail" ? 1 : 0;
      }
      return;
    case "status": {
      const runs = listRuns();
      out(runs.length ? runs.slice(0, 8).map(renderSummary).join("\n\n") : "No Axiom harness runs recorded.");
      return;
    }
    case "show":
      out(renderSummary(readRun(required(args[0], "run id"))));
      return;
    case "audit-baseline":
      out(renderSummary(auditBaseline()));
      return;
    case "measure-limiter":
      out(renderSummary(runBaselineLimiterSweep(required(args[0], "run id"))));
      return;
    case "stress-accepted":
      out(renderSummary(runAcceptedStressBaseline(required(args[0], "run id"))));
      return;
    case "map-sub-gain":
      {
        const { id, options } = parseSubSliderMapArgs(args);
        out(renderSummary(runSubSliderMap(id, options)));
      }
      return;
    case "stage-observability":
      out(renderSummary(runStageObservability(required(args[0], "run id"))));
      return;
    case "screen-reserve-law":
      out(renderSummary(runReserveLawScreen(required(args[0], "run id"))));
      return;
    case "qualify-reserve-range":
      out(renderSummary(runReserveRangeQualification(required(args[0], "run id"))));
      return;
    case "audit-stft":
      out(renderSummary(runStftStageAudit(required(args[0], "run id"))));
      return;
    case "audit-width-mono":
      out(renderSummary(runWidthMonoAudit(required(args[0], "run id"))));
      return;
    case "screen-width-material":
      out(renderSummary(runWidthMaterialScreen(required(args[0], "run id"))));
      return;
    case "screen-lowmid-width":
      out(renderSummary(runLowMidWidthScreen(required(args[0], "run id"))));
      return;
    case "screen-high-width":
      out(renderSummary(runHighWidthScreen(required(args[0], "run id"))));
      return;
    case "screen-exciter":
      out(renderSummary(runExciterSensitivityScreen(required(args[0], "run id"))));
      return;
    case "screen-exciter-probes":
      out(renderSummary(runExciterProbeScreen(required(args[0], "run id"))));
      return;
    case "investigate":
      out(renderSummary(createInvestigation(required(args.join(" "), "observation"))));
      return;
    case "hypothesis":
      out(renderSummary(setHypothesis(required(args[0], "run id"), required(args[1], "hypothesis"), required(args[2], "listening target"))));
      return;
    case "create-candidate":
      out(renderSummary(createCandidate(required(args[0], "run id"), required(args[1], "candidate version"))));
      return;
    case "qualify":
      out(renderSummary(runAutomatedValidation(required(args[0], "run id"), { skipHost: args.includes("--skip-host") })));
      return;
    case "qualify-lowmid-candidate":
      out(renderSummary(runLowMidWidthCandidateQualification(required(args[0], "run id"), { skipHost: args.includes("--skip-host") })));
      return;
    case "record-listening":
      out(renderSummary(recordListening(required(args[0], "run id"), required(args[1], "decision"), args.slice(2).join(" "))));
      return;
    case "commit":
      out(renderSummary(commitCandidate(required(args[0], "run id"), args.slice(1).join(" ") || undefined)));
      return;
    case "approve-publication":
      out(renderSummary(approvePublication(required(args[0], "run id"))));
      return;
    case "publish":
      out(renderSummary(publishPullRequest(required(args[0], "run id"))));
      return;
    case "approve-merge":
      out(renderSummary(approveMerge(required(args[0], "run id"))));
      return;
    case "merge":
      out(renderSummary(mergePullRequest(required(args[0], "run id"))));
      return;
    default:
      out("Usage: axiom-team.mjs <init|doctor|corpus-status|status|show|audit-baseline|measure-limiter|stress-accepted|map-sub-gain|stage-observability|screen-reserve-law|qualify-reserve-range|audit-stft|audit-width-mono|screen-width-material|screen-lowmid-width|screen-high-width|screen-exciter|screen-exciter-probes|investigate|hypothesis|create-candidate|qualify|qualify-lowmid-candidate|record-listening|commit|approve-publication|publish|approve-merge|merge> ...\nmap-sub-gain options: --slider-db <db> repeated, --label-regex <regex>, --repetitions <n>");
      process.exitCode = 2;
  }
}

main().catch((error) => {
  process.stderr.write(`error: ${error.message}\n`);
  process.exitCode = 1;
});
