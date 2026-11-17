#!/usr/bin/env python3
"""Route approved music into seasonal and playlist-safe folders.

This is an editorial routing agent. It does not approve rights or publish.
Unknown titles fail closed instead of being silently mixed into a playlist.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def _key(value: str) -> str:
    return " ".join((value or "").casefold().split())


def load_policy(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def route_rows(rows: list[dict], policy: dict, approved_titles: set[str] | None = None) -> dict:
    groups = policy["seasonal_groups"]
    title_to_group = {
        _key(title): group
        for group, titles in groups.items()
        for title in titles
    }
    routed: list[dict] = []
    excluded: list[dict] = []
    unknown: list[dict] = []
    for row in rows:
        title = (row.get("title") or "").strip()
        if approved_titles is not None and _key(title) not in approved_titles:
            excluded.append({"title": title, "reason": "not_in_approved_title_set"})
            continue
        group = title_to_group.get(_key(title))
        if not group:
            unknown.append({"title": title, "reason": "missing_editorial_category"})
            continue
        routed.append({
            "title": title,
            "artist": (row.get("artist") or row.get("creator") or "").strip(),
            "group": group,
            "folder": f"tracks/seasonal/{'christmas' if group == 'christmas' else 'general_jazz_soul'}",
            "playlist_allowlist": [
                name for name, allowed in policy.get("playlist_rules", {}).items()
                if group in allowed
            ],
            "status": "ROUTED_REVIEW_ONLY",
        })
    status = "ROUTED" if not unknown else "BLOCKED_UNCATEGORIZED"
    return {
        "status": status,
        "routed_count": len(routed),
        "excluded_count": len(excluded),
        "unknown_count": len(unknown),
        "routed": routed,
        "excluded": excluded,
        "unknown": unknown,
        "rights_verified": False,
        "publication": "DISABLED",
    }


def audit_folder_boundaries(report: dict) -> dict:
    christmas = [
        item for item in report.get("routed", [])
        if item["group"] == "christmas"
    ]
    general = [
        item for item in report.get("routed", [])
        if item["group"] == "general_jazz_soul"
    ]
    violations = [
        item["title"] for item in christmas
        if "christmas" not in item["folder"]
    ]
    return {
        "christmas_count": len(christmas),
        "general_count": len(general),
        "boundary_violations": violations,
        "status": "PASS" if not violations else "BLOCKED",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", required=True, type=Path)
    parser.add_argument("--policy", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--approved-titles-file", type=Path)
    args = parser.parse_args()

    approved = None
    if args.approved_titles_file:
        approved = {
            _key(line)
            for line in args.approved_titles_file.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.lstrip().startswith("#")
        }
    with args.csv.open(newline="", encoding="utf-8-sig") as handle:
        report = route_rows(list(csv.DictReader(handle)), load_policy(args.policy), approved)
    report["folder_boundary_audit"] = audit_folder_boundaries(report)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": report["status"],
        "routed_count": report["routed_count"],
        "excluded_count": report["excluded_count"],
        "unknown_count": report["unknown_count"],
        "folder_boundary": report["folder_boundary_audit"]["status"],
    }, ensure_ascii=False))
    return 0 if report["status"] == "ROUTED" and report["folder_boundary_audit"]["status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
