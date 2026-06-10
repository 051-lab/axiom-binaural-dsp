#!/usr/bin/env python3
"""Build a local level-matched A/B listening package from matched WAV folders."""

from __future__ import annotations

import argparse
import json
import random
import re
import shutil
from pathlib import Path
from typing import Any

import analyze_audio_perceptual_metrics as metrics


DEFAULT_LOUDNESS_TOLERANCE_DB = 0.25
DEFAULT_TRUE_PEAK_CEILING_DBFS = -1.0


class PackageError(RuntimeError):
    pass


def db_text(value: float | None) -> str:
    return "-" if value is None else f"{value:.3f}"


def slug(value: str) -> str:
    clean = re.sub(r"[^A-Za-z0-9._-]+", "_", value.strip()).strip("._-")
    return clean or "pair"


def collect_wavs(root: Path) -> dict[str, Path]:
    if not root.is_dir():
        raise PackageError(f"WAV directory not found: {root}")
    return {
        path.relative_to(root).as_posix(): path
        for path in sorted(root.rglob("*.wav"))
        if path.is_file()
    }


def filter_names(names: list[str], include_regex: str = "", exclude_regex: str = "") -> list[str]:
    include = re.compile(include_regex) if include_regex else None
    exclude = re.compile(exclude_regex) if exclude_regex else None
    return [
        name for name in names
        if (include is None or include.search(name))
        and (exclude is None or not exclude.search(name))
    ]


def channel_clips(report: dict[str, Any]) -> int:
    return int(report["channels"]["combined"]["clipped_samples"])


def loudness(report: dict[str, Any]) -> float | None:
    return report["loudness"]["ungated_loudness_proxy_lufs"]


def true_peak(report: dict[str, Any]) -> float | None:
    return report["channels"]["combined"]["true_peak_proxy_dbfs"]


def gain_to_match(reference: dict[str, Any], candidate: dict[str, Any]) -> float | None:
    reference_loudness = loudness(reference)
    candidate_loudness = loudness(candidate)
    if reference_loudness is None or candidate_loudness is None:
        return None
    return reference_loudness - candidate_loudness


def safety_trim_db(reference: dict[str, Any], candidate: dict[str, Any], candidate_gain_db: float | None, ceiling_dbfs: float) -> float:
    reference_peak = true_peak(reference)
    candidate_peak = true_peak(candidate)
    if reference_peak is None or candidate_peak is None or candidate_gain_db is None:
        return 0.0
    loudest_after_match = max(reference_peak, candidate_peak + candidate_gain_db)
    return min(0.0, ceiling_dbfs - loudest_after_match)


def package_pair(
    name: str,
    reference_path: Path,
    candidate_path: Path,
    output_dir: Path,
    rng: random.Random,
    copy_audio: bool,
    loudness_tolerance_db: float,
    true_peak_ceiling_dbfs: float,
) -> dict[str, Any]:
    comparison = metrics.analyze_pair(
        reference_path,
        candidate_path,
        reference_label=f"{name}-reference",
        candidate_label=f"{name}-candidate",
    )
    reference = comparison["reference"]
    candidate = comparison["candidate"]
    candidate_gain = gain_to_match(reference, candidate)
    shared_trim = safety_trim_db(reference, candidate, candidate_gain, true_peak_ceiling_dbfs)
    reference_gain = shared_trim
    matched_candidate_gain = None if candidate_gain is None else candidate_gain + shared_trim
    warnings: list[str] = []
    errors: list[str] = []

    loudness_delta = comparison["candidate_minus_reference"]["loudness"]["ungated_loudness_proxy_lufs_delta"]
    if loudness_delta is None:
        errors.append("loudness proxy is not measurable")
    elif abs(loudness_delta) > loudness_tolerance_db:
        warnings.append(
            f"candidate loudness differs from reference by {loudness_delta:+.3f} dB; use recommended playback gain"
        )
    if channel_clips(reference) > 0:
        errors.append(f"reference capture has {channel_clips(reference)} clipped channel samples")
    if channel_clips(candidate) > 0:
        errors.append(f"candidate capture has {channel_clips(candidate)} clipped channel samples")
    if shared_trim < 0.0:
        warnings.append(f"apply shared safety trim {shared_trim:.3f} dB to keep true-peak proxy below {true_peak_ceiling_dbfs:.3f} dBFS")

    first_role, second_role = ("reference", "candidate") if rng.random() < 0.5 else ("candidate", "reference")
    role_paths = {"reference": reference_path, "candidate": candidate_path}
    role_gains = {"reference": reference_gain, "candidate": matched_candidate_gain}
    assignments = {
        "A": {"role": first_role, "recommended_gain_db": role_gains[first_role]},
        "B": {"role": second_role, "recommended_gain_db": role_gains[second_role]},
    }
    if copy_audio:
        pair_dir = output_dir / "audio" / slug(name)
        pair_dir.mkdir(parents=True, exist_ok=True)
        for slot, assignment in assignments.items():
            destination = pair_dir / f"{slot}.wav"
            shutil.copy2(role_paths[assignment["role"]], destination)
            assignment["package_path"] = str(destination)

    return {
        "name": name,
        "reference_path": str(reference_path),
        "candidate_path": str(candidate_path),
        "status": "fail" if errors else ("pass_with_warnings" if warnings else "pass"),
        "errors": errors,
        "warnings": warnings,
        "recommended_reference_gain_db": reference_gain,
        "recommended_candidate_gain_db": matched_candidate_gain,
        "candidate_gain_to_match_reference_db": candidate_gain,
        "shared_safety_trim_db": shared_trim,
        "true_peak_ceiling_dbfs": true_peak_ceiling_dbfs,
        "loudness_tolerance_db": loudness_tolerance_db,
        "assignments": assignments,
        "perceptual_metrics": comparison,
    }


def build_package(
    reference_dir: Path,
    candidate_dir: Path,
    output_dir: Path,
    label: str = "axiom-ab-listening",
    seed: int = 51,
    copy_audio: bool = True,
    loudness_tolerance_db: float = DEFAULT_LOUDNESS_TOLERANCE_DB,
    true_peak_ceiling_dbfs: float = DEFAULT_TRUE_PEAK_CEILING_DBFS,
    include_regex: str = "",
    exclude_regex: str = "",
) -> dict[str, Any]:
    reference_files = collect_wavs(reference_dir)
    candidate_files = collect_wavs(candidate_dir)
    all_matched = sorted(set(reference_files) & set(candidate_files))
    matched = filter_names(all_matched, include_regex, exclude_regex)
    missing_candidates = sorted(set(reference_files) - set(candidate_files))
    missing_references = sorted(set(candidate_files) - set(reference_files))
    errors = []
    warnings = []
    if not matched:
        errors.append("no matching WAV filenames found after filters")
    if missing_candidates:
        errors.append(f"missing candidate WAVs for: {', '.join(missing_candidates)}")
    if missing_references:
        errors.append(f"missing reference WAVs for: {', '.join(missing_references)}")

    output_dir.mkdir(parents=True, exist_ok=True)
    rng = random.Random(seed)
    pairs = [
        package_pair(
            name,
            reference_files[name],
            candidate_files[name],
            output_dir,
            rng,
            copy_audio,
            loudness_tolerance_db,
            true_peak_ceiling_dbfs,
        )
        for name in matched
    ]
    for pair in pairs:
        errors.extend(f"{pair['name']}: {error}" for error in pair["errors"])
        warnings.extend(f"{pair['name']}: {warning}" for warning in pair["warnings"])

    status = "fail" if errors else ("pass_with_warnings" if warnings else "pass")
    return {
        "label": label,
        "status": status,
        "reference_dir": str(reference_dir),
        "candidate_dir": str(candidate_dir),
        "output_dir": str(output_dir),
        "copy_audio": copy_audio,
        "random_seed": seed,
        "include_regex": include_regex,
        "exclude_regex": exclude_regex,
        "pair_count": len(pairs),
        "missing_candidates": missing_candidates,
        "missing_references": missing_references,
        "errors": errors,
        "warnings": warnings,
        "pairs": pairs,
    }


def markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Axiom A/B Listening Package",
        "",
        f"Label: `{report['label']}`",
        "",
        f"Status: **{report['status'].upper()}**",
        "",
        "This package is local listening evidence. It uses ungated loudness-proxy matching and true-peak-proxy safety trim; it is not certified BS.1770 loudness normalization.",
        "",
        "| Pair | A role | A gain (dB) | B role | B gain (dB) | Candidate loudness delta (dB) | Candidate match gain (dB) | Status |",
        "| --- | --- | ---: | --- | ---: | ---: | ---: | --- |",
    ]
    for pair in report["pairs"]:
        delta = pair["perceptual_metrics"]["candidate_minus_reference"]["loudness"]["ungated_loudness_proxy_lufs_delta"]
        lines.append(
            f"| {pair['name']} | {pair['assignments']['A']['role']} | "
            f"{db_text(pair['assignments']['A']['recommended_gain_db'])} | "
            f"{pair['assignments']['B']['role']} | {db_text(pair['assignments']['B']['recommended_gain_db'])} | "
            f"{db_text(delta)} | {db_text(pair['candidate_gain_to_match_reference_db'])} | "
            f"{pair['status'].upper()} |"
        )
    if report["errors"]:
        lines.extend(["", "## Errors", ""])
        lines.extend(f"- {error}" for error in report["errors"])
    if report["warnings"]:
        lines.extend(["", "## Warnings", ""])
        lines.extend(f"- {warning}" for warning in report["warnings"])
    lines.extend(
        [
            "",
            "## Listening Rules",
            "",
            "- Keep A/B slot identity hidden until notes are complete.",
            "- Apply the listed playback gain per slot before judging loudness, bass, punch, air, harshness, or fatigue.",
            "- Keep device route, host limiter, crossfeed, and Axiom slider settings fixed across both slots.",
            "- Record the result with `scripts/validate_axiom_listening_record.py`.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("reference_dir", type=Path)
    parser.add_argument("candidate_dir", type=Path)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--label", default="axiom-ab-listening")
    parser.add_argument("--seed", type=int, default=51)
    parser.add_argument("--no-copy-audio", action="store_true")
    parser.add_argument("--loudness-tolerance-db", type=float, default=DEFAULT_LOUDNESS_TOLERANCE_DB)
    parser.add_argument("--true-peak-ceiling-dbfs", type=float, default=DEFAULT_TRUE_PEAK_CEILING_DBFS)
    parser.add_argument("--include-regex", default="", help="only package matching relative WAV paths")
    parser.add_argument("--exclude-regex", default="", help="exclude matching relative WAV paths")
    args = parser.parse_args()

    try:
        report = build_package(
            args.reference_dir.resolve(),
            args.candidate_dir.resolve(),
            args.output_dir.resolve(),
            label=args.label,
            seed=args.seed,
            copy_audio=not args.no_copy_audio,
            loudness_tolerance_db=args.loudness_tolerance_db,
            true_peak_ceiling_dbfs=args.true_peak_ceiling_dbfs,
            include_regex=args.include_regex,
            exclude_regex=args.exclude_regex,
        )
    except PackageError as exc:
        print(f"error: {exc}")
        return 1

    json_path = args.output_dir.resolve() / "ab-listening-package.json"
    markdown_path = args.output_dir.resolve() / "ab-listening-package.md"
    json_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    markdown_path.write_text(markdown(report), encoding="utf-8")
    print(json_path)
    print(markdown_path)
    return 1 if report["status"] == "fail" else 0


if __name__ == "__main__":
    raise SystemExit(main())
