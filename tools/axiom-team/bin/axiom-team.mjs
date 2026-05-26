#!/usr/bin/env node
import {
  approveMerge, approvePublication, auditBaseline, commitCandidate, createCandidate,
  createInvestigation, doctor, listRuns, loadLocalConfig, mergePullRequest,
  publishPullRequest, readRun, recordListening, renderSummary, runAutomatedValidation,
  runAcceptedStressBaseline, runBaselineLimiterSweep, runReserveLawScreen, runReserveRangeQualification,
  runLowMidWidthCandidateQualification, runLowMidWidthScreen, runStftStageAudit, runSubSliderMap, runWidthMaterialScreen, runWidthMonoAudit,
  saveLocalConfig, setHypothesis
} from "../lib/core.mjs";

function out(value) {
  process.stdout.write((typeof value === "string" ? value : JSON.stringify(value, null, 2)) + "\n");
}

function required(value, label) {
  if (!value) throw new Error(`Missing ${label}.`);
  return value;
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
      out(renderSummary(runSubSliderMap(required(args[0], "run id"))));
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
      out("Usage: axiom-team.mjs <init|doctor|status|show|audit-baseline|measure-limiter|stress-accepted|map-sub-gain|screen-reserve-law|qualify-reserve-range|audit-stft|audit-width-mono|screen-width-material|screen-lowmid-width|investigate|hypothesis|create-candidate|qualify|qualify-lowmid-candidate|record-listening|commit|approve-publication|publish|approve-merge|merge> ...");
      process.exitCode = 2;
  }
}

main().catch((error) => {
  process.stderr.write(`error: ${error.message}\n`);
  process.exitCode = 1;
});
