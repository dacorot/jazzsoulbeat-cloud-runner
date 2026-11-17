#!/usr/bin/env python3
"""Review-only rights evidence audit for discovery candidate CSVs.

This classifies evidence completeness and human-gated status. It never grants
rights, imports files into the approved library, or enables publication.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from urllib.parse import urlparse


def https_url(value: str) -> bool:
    parsed = urlparse(str(value or "").strip())
    return parsed.scheme == "https" and bool(parsed.hostname)


def audit(rows: list[dict]) -> dict:
    results = []
    for row in rows:
        reasons = []
        if not https_url(row.get("source_url", "")):
            reasons.append("source_evidence_missing_or_invalid")
        if not https_url(row.get("download_url", "")):
            reasons.append("direct_audio_url_missing_or_invalid")
        license_url = row.get("license_url") or row.get("license_url", "")
        if not https_url(license_url):
            reasons.append("license_evidence_missing_or_invalid")
        if str(row.get("permission", "")).casefold() != "yes":
            reasons.append("permission_not_human_verified")
        if str(row.get("rights_verified", "")).casefold() != "yes":
            reasons.append("rights_not_verified")
        status = "BLOCKED_PENDING_HUMAN_REVIEW" if reasons else "READY_FOR_HUMAN_APPROVAL"
        results.append({
            "title": row.get("title") or row.get("title_hint") or "",
            "artist": row.get("artist") or row.get("artist_hint") or "",
            "source_url": row.get("source_url", ""),
            "download_url": row.get("download_url", ""),
            "license_url": license_url,
            "status": status,
            "reasons": reasons,
            "auto_approved": False,
            "publication": "DISABLED",
        })
    return {
        "status": "REVIEW_REQUIRED" if any(item["status"].startswith("BLOCKED") for item in results) else "READY_FOR_HUMAN_APPROVAL",
        "total": len(results),
        "blocked": sum(item["status"].startswith("BLOCKED") for item in results),
        "ready_for_human": sum(item["status"] == "READY_FOR_HUMAN_APPROVAL" for item in results),
        "rights_verified": False,
        "auto_approval": False,
        "publication": "DISABLED",
        "results": results,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    with args.csv.open(newline="", encoding="utf-8-sig") as handle:
        report = audit(list(csv.DictReader(handle)))
    report["input_csv"] = str(args.csv)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: report[key] for key in (
        "status", "total", "blocked", "ready_for_human",
        "rights_verified", "auto_approval", "publication",
    )}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
