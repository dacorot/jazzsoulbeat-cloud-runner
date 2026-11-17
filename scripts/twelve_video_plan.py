#!/usr/bin/env python3
"""Create the bounded 12-video production queue without approving assets."""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path


def build_plan(start: dt.date, count: int = 12) -> dict:
    config = json.loads(Path("config/channel_agents.json").read_text(encoding="utf-8"))
    categories = config["editorial_categories"]
    jobs = []
    for index in range(count):
        category = categories[index % len(categories)]
        release = start + dt.timedelta(days=index * 2)
        digest = hashlib.sha256(f"{release.isoformat()}:{category['id']}:{index}".encode()).hexdigest()
        jobs.append({
            "job_id": f"jsb-video-{index + 1:02d}-{release:%Y%m%d}",
            "sequence": index + 1,
            "target_date": release.isoformat(),
            "category": category["id"],
            "title_direction": category["display_name"],
            "mission": category["mission"],
            "visual_agent": "visual_motion_agent",
            "visual_profile": "static_rain_steam_only",
            "image_status": "PLAN_READY_BASE_IMAGE_REQUIRED",
            "motion_status": "CONTRACT_READY",
            "music_status": "SEARCH_AND_APPROVAL_REQUIRED",
            "target_duration_seconds": 3600,
            "human_gates": ["music_creative_approval", "music_rights_verification", "video_creative_approval", "private_upload_approval"],
            "publication": "DISABLED",
            "deterministic_seed": digest[:16],
        })
    return {
        "schema_version": 1,
        "agent_id": "production_coordinator",
        "created_at": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat(),
        "target_videos": count,
        "parallel_music_lanes": ["primary_catalogs", "community_catalogs"],
        "no_track_repetition": True,
        "jobs": jobs,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", default="2026-11-18")
    parser.add_argument("--count", type=int, default=12)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.count != 12:
        raise SystemExit("The first production wave is fixed at exactly 12 videos.")
    plan = build_plan(dt.date.fromisoformat(args.start), args.count)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(plan, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
