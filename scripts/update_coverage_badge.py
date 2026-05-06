#!/usr/bin/env python3
# Copyright 2026 KYNODE
# Licensed under the Apache License, Version 2.0.

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def color_for(percent: int) -> str:
    if percent >= 90:
        return "brightgreen"
    if percent >= 80:
        return "green"
    if percent >= 70:
        return "yellow"
    return "red"


def badge_payload(coverage_json: Path) -> dict[str, object]:
    coverage = json.loads(coverage_json.read_text(encoding="utf-8"))
    percent = round(float(coverage["totals"]["percent_covered"]))
    return {
        "schemaVersion": 1,
        "label": "coverage",
        "message": f"{percent}%",
        "color": color_for(percent),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Update or check the Shields coverage badge JSON.")
    parser.add_argument("coverage_json", type=Path)
    parser.add_argument("badge_json", type=Path)
    parser.add_argument("--check", action="store_true", help="Fail if the badge JSON is not current.")
    args = parser.parse_args()

    payload = badge_payload(args.coverage_json)
    expected = json.dumps(payload, indent=2, sort_keys=True) + "\n"

    if args.check:
        current = args.badge_json.read_text(encoding="utf-8")
        if current != expected:
            print(
                f"{args.badge_json} is out of date. Run scripts/update_coverage_badge.py.",
                file=sys.stderr,
            )
            return 1
        return 0

    args.badge_json.parent.mkdir(parents=True, exist_ok=True)
    args.badge_json.write_text(expected, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
