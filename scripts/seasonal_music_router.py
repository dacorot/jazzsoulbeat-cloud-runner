#!/usr/bin/env python3
"""Route approved music into seasonal and playlist-safe folders."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def _key(value: str) -> str:
    return " ".join((value or "").casefold().split())


def load_policy(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _metadata(row: dict) -> str:
    return " ".join(
        (row.get(field) or "")
        for field in ("title", "genre", "instruments", "feel")
    ).casefold()


def _primary_season(row: dict, policy: dict) -> tuple[str, dict[str, int]]:
    routing = policy.get("seasonal_routing", {})
    text = _metadata(row)
    scores = {
        season: sum(text.count(_key(keyword)) for keyword in keywords)
        for season, keywords in routing.get("keyword_weights", {}).items()
    }
    order = routing.get("tie_break_order", ["autumn", "spring", "summer", "winter"])
    primary = max(order, key=lambda season: (scores.get(season, 0), -order.index(season)))
    if not scores.get(primary, 0):
        primary = routing.get("fallback_season", "autumn")
    return primary, scores


def route_rows(rows: list[dict], policy: dict, approved_titles: set[str] | None = None) -> dict:
    groups = policy["seasonal_groups"]
    title_to_group = {
        _key(title): group
        for group, titles in groups.items()
        for title in titles
    }
    routed, excluded, unknown = [], [], []
    for row in rows:
        title = (row.get("title") or "").strip()
        if approved_titles is not None and _key(title) not in approved_titles:
            excluded.append({"title": title, "reason": "not_in_approved_title_set"})
            continue
        group = title_to_group.get(_key(title))
        if not group:
            unknown.append({"title": title, "reason": "missing_editorial_category"})
            continue
        if group == "christmas":
            season, scores = "christmas", {"christmas": 1}
        else:
            season, scores = _primary_season(row, policy)
        playlists = [
            name for name, allowed in policy.get("playlist_rules", {}).items()
            if group in allowed and (
                group != "christmas" or name in {"christmas_holiday", "winter_holiday"}
            )
        ]
        routed.append({
            "title": title,
            "artist": (row.get("artist") or row.get("creator") or "").strip(),
            "group": group,
            "primary_season": season,
            "season_scores": scores,
            "season_folder": f"tracks/seasonal/{season}",
            "playlist_folders": ([f"tracks/playlists/{season}/{name}" for name in playlists] if group != "christmas" else [f"tracks/playlists/{name}" for name in playlists]),
            "playlist_allowlist": playlists,
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
    violations = []
    for item in report.get("routed", []):
        if item["group"] == "christmas" and item["primary_season"] != "christmas":
            violations.append(item["title"])
        if item["group"] != "christmas" and item["primary_season"] == "christmas":
            violations.append(item["title"])
        if item["group"] == "christmas" and any(
            name not in {"christmas_holiday", "winter_holiday"}
            for name in item["playlist_allowlist"]
        ):
            violations.append(item["title"])
    return {
        "christmas_count": sum(item["group"] == "christmas" for item in report.get("routed", [])),
        "general_count": sum(item["group"] == "general_jazz_soul" for item in report.get("routed", [])),
        "season_counts": {
            season: sum(item["primary_season"] == season for item in report.get("routed", []))
            for season in ("spring", "summer", "autumn", "winter", "christmas")
        },
        "boundary_violations": sorted(set(violations)),
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
            _key(line) for line in args.approved_titles_file.read_text(encoding="utf-8").splitlines()
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
        "season_counts": report["folder_boundary_audit"]["season_counts"],
        "folder_boundary": report["folder_boundary_audit"]["status"],
    }, ensure_ascii=False))
    return 0 if report["status"] == "ROUTED" and report["folder_boundary_audit"]["status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
