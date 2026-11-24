#!/usr/bin/env python3
"""Produce a read-only, hash-bound reconciliation of the two project stores.

The private agent database and the Cloud Runner approval ledger have different
approval contracts. This report makes the difference explicit and never
promotes a track or changes publication state.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sqlite3
from collections import Counter
from pathlib import Path


DEFAULT_CONTRACT = {"minimum_unique_tracks": 500, "minimum_approved_seconds": 36000,
                    "min_duration_seconds": 7200, "max_duration_seconds": 10800}


def load_contract(runner_root: Path) -> dict:
    path = runner_root / "config/active_contract.json"
    if not path.is_file():
        return DEFAULT_CONTRACT
    data = json.loads(path.read_text(encoding="utf-8"))
    return {"minimum_unique_tracks": int(data["audio"]["minimum_unique_tracks"]),
            "minimum_approved_seconds": int(data["audio"]["minimum_approved_seconds"]),
            "min_duration_seconds": int(data["delivery"]["min_duration_seconds"]),
            "max_duration_seconds": int(data["delivery"]["max_duration_seconds"])}


def ledger_summary(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    requests = list(data.get("requests", {}).values())
    approved = [row for row in requests if all(row.get(key) is True for key in (
        "creative_approval", "rights_verified", "eligible_for_video_assembly"))]
    hashes = {row.get("artifact_sha256") for row in approved if row.get("artifact_sha256")}
    return {
        "request_count": len(requests),
        "statuses": dict(Counter(row.get("status", "MISSING") for row in requests)),
        "approved_request_count": len(approved),
        "approved_unique_track_count": len(hashes),
        "approved_seconds": round(sum(float(row.get("duration_seconds") or row.get("technical_duration_seconds") or 0) for row in approved), 2),
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
    }


def agent_summary(path: Path) -> dict:
    connection = sqlite3.connect(path)
    try:
        row = connection.execute(
            "select count(*), sum(case when approved=1 then 1 else 0 end), "
            "sum(case when approved=1 and rights_verified=1 then 1 else 0 end), "
            "coalesce(sum(case when approved=1 and rights_verified=1 then duration else 0 end), 0) "
            "from tracks"
        ).fetchone()
    finally:
        connection.close()
    return {
        "track_count": int(row[0] or 0),
        "approved_count": int(row[1] or 0),
        "approved_rights_verified_count": int(row[2] or 0),
        "approved_rights_verified_seconds": round(float(row[3] or 0), 2),
    }


def csv_summary(path: Path) -> dict:
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    verified = [row for row in rows if row.get("rights_verified") == "yes"]
    return {"row_count": len(rows), "rights_verified_count": len(verified)}


def delivery_summary(path: Path, contract: dict) -> dict:
    manifest = json.loads(path.read_text(encoding="utf-8"))
    videos = manifest.get("videos", [])
    hashes = [row.get("sha256") for row in videos]
    durations = [float(row.get("duration_seconds") or 0) for row in videos]
    return {
        "status": manifest.get("status"),
        "publication": manifest.get("publication"),
        "video_count": len(videos),
        "unique_video_hashes": len(set(hashes)),
        "total_video_seconds": round(sum(float(row.get("duration_seconds") or 0) for row in videos), 2),
        "pool_count": manifest.get("pool_count"),
        "pool_seconds": manifest.get("pool_seconds"),
        "contract": {
            "status_not_invalidated": manifest.get("status") != "INVALIDATED_LEGACY_DELIVERY",
            "all_videos_2_to_3_hours": bool(videos) and all(
            contract["min_duration_seconds"] <= value <= contract["max_duration_seconds"] for value in durations
            ),
            "scene_effects_validated": bool(manifest.get("scene_effects_validated")) and all(
                bool(row.get("scene_effect_validated")) for row in videos
            ),
        },
        "manifest_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
    }


def reconcile(runner_root: Path, agent_root: Path) -> dict:
    contract = load_contract(runner_root)
    ledger = ledger_summary(runner_root / "music-production/approval_ledger.json")
    agent = agent_summary(agent_root / "data/agent.db")
    library = csv_summary(agent_root / "tracks/library.csv")
    delivery = delivery_summary(agent_root / "tracks/generated/jazz-only-10-videos-2026-11-22/delivery-manifest.json", contract)
    delivery_contract = delivery["contract"]
    status = "RECONCILED_READY" if (
        ledger["approved_unique_track_count"] >= contract["minimum_unique_tracks"]
        and ledger["approved_seconds"] >= contract["minimum_approved_seconds"]
        and all(delivery_contract.values())
    ) else "RECONCILED_BLOCKED_ACTIVE_CONTRACT"
    next_action = (
        "Run final release QA; publication remains disabled."
        if status == "RECONCILED_READY"
        else "Grow the approved library to 500 unique tracks and rebuild a 2–3 hour delivery with validated scene effects before release QA."
    )
    return {
        "schema_version": 1,
        "status": status,
        "publication": "DISABLED",
        "ledger": ledger,
        "agent_database": agent,
        "library_csv": library,
        "delivery": delivery,
        "discrepancies": [
            "The Cloud Runner ledger and local agent stores are separate approval contracts and must be reconciled before release.",
            "The CSV library and SQLite database are separate stores with different row counts.",
            "The delivery repeats a 1911.620586-second pool and therefore is not unique audio capacity.",
        ],
        "next_safe_action": next_action,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runner-root", type=Path, default=Path.cwd())
    parser.add_argument("--agent-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = reconcile(args.runner_root.resolve(), args.agent_root.resolve())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
