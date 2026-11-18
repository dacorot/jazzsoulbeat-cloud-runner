#!/usr/bin/env python3
"""Build a fail-closed active-catalog view from the copyright watch report."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

BLOCKING_DECISIONS = {
    "REMOVE_FROM_ACTIVE_CATALOG_PENDING_CONFIRMATION",
    "REVIEW_REQUIRED",
}


def build_views(report: dict[str, Any]) -> dict[str, Any]:
    records = report.get("records")
    if not isinstance(records, list):
        raise ValueError("copyright_watch_report_records_required")
    quarantined: list[dict[str, Any]] = []
    active: list[dict[str, Any]] = []
    for record in records:
        if not isinstance(record, dict):
            continue
        decision = record.get("decision")
        if decision in BLOCKING_DECISIONS:
            quarantined.append(record)
        else:
            active.append(record)
    return {
        "schema_version": 1,
        "source_report_checked_at": report.get("checked_at"),
        "mode": "FAIL_CLOSED_DERIVED_VIEW",
        "automatic_deletion": False,
        "automatic_rights_approval": False,
        "quarantined": quarantined,
        "active_pending_review": active,
        "counts": {"quarantined": len(quarantined), "active_pending_review": len(active)},
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = json.loads(args.report.read_text(encoding="utf-8"))
    views = build_views(report)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(views, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(views["counts"], ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
