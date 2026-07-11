#!/usr/bin/env python3
"""Validate the complete approved R011-to-R012 candidate change boundary."""

from __future__ import annotations

import argparse
import difflib
import pathlib
import re
import sys


REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
DEFAULT_BASELINE = REPO_ROOT / "src" / "axiom_binaural_dsp_v4.1.4.11.eel"
DEFAULT_CANDIDATE = REPO_ROOT / "src" / "axiom_clean_r012.eel"

BASELINE_STATE = "sub_l = 0.0; sub_r = 0.0; drive = 3.5; sat_l = 0.0; sat_r = 0.0;"
INTERPOLATION_STATE = "\n".join(
    [
        BASELINE_STATE,
        "prev_sub_l = 0.0; prev_sub_r = 0.0; sub_l_mid = 0.0; sub_r_mid = 0.0;",
        "sat_l_mid = 0.0; sat_r_mid = 0.0; sat_l_now = 0.0; sat_r_now = 0.0;",
    ]
)
BASELINE_SATURATION = "\n".join(
    [
        "sat_l = (sub_l * drive) / (1.0 + abs(sub_l * drive));",
        "sat_r = (sub_r * drive) / (1.0 + abs(sub_r * drive));",
    ]
)
R012_SATURATION = "\n".join(
    [
        "sub_l_mid = (prev_sub_l + sub_l) * 0.5;",
        "sat_l_mid = (sub_l_mid * drive) / (1.0 + abs(sub_l_mid * drive));",
        "sat_l_now = (sub_l * drive) / (1.0 + abs(sub_l * drive));",
        "sat_l = (sat_l_mid + sat_l_now) * 0.5;",
        "prev_sub_l = sub_l;",
        "",
        "sub_r_mid = (prev_sub_r + sub_r) * 0.5;",
        "sat_r_mid = (sub_r_mid * drive) / (1.0 + abs(sub_r_mid * drive));",
        "sat_r_now = (sub_r * drive) / (1.0 + abs(sub_r * drive));",
        "sat_r = (sat_r_mid + sat_r_now) * 0.5;",
        "prev_sub_r = sub_r;",
    ]
)


def replace_once(text: str, old: str, new: str, name: str) -> str:
    count = text.count(old)
    if count != 1:
        raise ValueError(f"{name}: expected one baseline match, found {count}")
    return text.replace(old, new, 1)


def approved_r012_text(baseline: str, candidate_description: str) -> str:
    first_line, separator, remainder = baseline.partition("\n")
    if not separator or not first_line.startswith("desc:"):
        raise ValueError("baseline description line is missing")
    if not candidate_description.startswith("desc:"):
        raise ValueError("candidate description line is missing")
    expected = candidate_description + "\n" + remainder
    expected = replace_once(
        expected,
        "slider2:135<0,200,5>Global Side Width (%)",
        "slider2:100<0,200,5>Global Side Width (%)",
        "slider2 declaration",
    )
    expected = replace_once(
        expected,
        "slider1 = 4; slider2 = 135; slider3 = 50;",
        "slider1 = 4; slider2 = 100; slider3 = 50;",
        "slider2 initialization",
    )
    expected = replace_once(expected, BASELINE_STATE, INTERPOLATION_STATE, "interpolation state")
    expected = replace_once(expected, BASELINE_SATURATION, R012_SATURATION, "saturation block")
    return expected


def validate(baseline_path: pathlib.Path, candidate_path: pathlib.Path) -> list[str]:
    failures: list[str] = []
    baseline = baseline_path.read_text(encoding="utf-8")
    candidate = candidate_path.read_text(encoding="utf-8")
    candidate_description = candidate.partition("\n")[0]
    try:
        expected = approved_r012_text(baseline, candidate_description)
    except ValueError as error:
        return [str(error)]

    if candidate != expected:
        diff = "\n".join(
            difflib.unified_diff(
                expected.splitlines(),
                candidate.splitlines(),
                fromfile="approved-r012",
                tofile=str(candidate_path),
                n=2,
            )
        )
        failures.append("candidate contains changes outside the approved R012 boundary\n" + diff)

    required = {
        "slider2 declaration default 100": "slider2:100<0,200,5>Global Side Width (%)",
        "slider2 initialization default 100": "slider1 = 4; slider2 = 100; slider3 = 50;",
        "slider5 default 126": "slider5:126<0,200,5>",
        "slider6 default 110": "slider6:110<0,150,5>",
        "interpolation previous-sample state": "prev_sub_l = 0.0; prev_sub_r = 0.0;",
        "left midpoint": "sub_l_mid = (prev_sub_l + sub_l) * 0.5;",
        "right midpoint": "sub_r_mid = (prev_sub_r + sub_r) * 0.5;",
        "left midpoint saturator": "sat_l_mid = (sub_l_mid * drive) / (1.0 + abs(sub_l_mid * drive));",
        "right midpoint saturator": "sat_r_mid = (sub_r_mid * drive) / (1.0 + abs(sub_r_mid * drive));",
        "left current saturator": "sat_l_now = (sub_l * drive) / (1.0 + abs(sub_l * drive));",
        "right current saturator": "sat_r_now = (sub_r * drive) / (1.0 + abs(sub_r * drive));",
        "left saturation average": "sat_l = (sat_l_mid + sat_l_now) * 0.5;",
        "right saturation average": "sat_r = (sat_r_mid + sat_r_now) * 0.5;",
        "left previous-sample update": "prev_sub_l = sub_l;",
        "right previous-sample update": "prev_sub_r = sub_r;",
    }
    for name, fragment in required.items():
        if candidate.count(fragment) != 1:
            failures.append(f"{name}: expected exactly one match")

    prohibited = re.compile(r"\b(lfo|modulation|oscillator|entrainment|dopamine|reward)\b", re.IGNORECASE)
    executable = "\n".join(line.split("//", 1)[0] for line in candidate.splitlines())
    if prohibited.search(executable):
        failures.append("unapproved modulation, LFO, or unrelated experimental processing found")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("candidate", nargs="?", type=pathlib.Path, default=DEFAULT_CANDIDATE)
    parser.add_argument("--baseline", type=pathlib.Path, default=DEFAULT_BASELINE)
    args = parser.parse_args()
    failures = validate(args.baseline, args.candidate)
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1
    print("PASS: R012 defaults and interpolation arithmetic match the approved change boundary")
    print("PASS: crossover, bass-filter, additive-injection, exciter, STFT, and reserve code match R011")
    print("PASS: internal limiting, crossfeed, modulation, LFO, and unrelated processing are absent")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
