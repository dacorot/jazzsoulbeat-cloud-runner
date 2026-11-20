#!/usr/bin/env python3
"""Cross-check the project contract before any production run.

This is a read-only Deming CHECK: it verifies that editorial, seasonal,
visual, queue, audio and publication constraints agree with one another.
It never approves creative work, rights or publication.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def audit(root: Path) -> dict:
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    channel = json.loads((root / "config/channel_agents.json").read_text(encoding="utf-8"))
    seasonal = json.loads((root / "config/seasonal_visual_matrix.json").read_text(encoding="utf-8"))
    policy = json.loads((root / "config/music_search_policy.json").read_text(encoding="utf-8"))
    visual = json.loads((root / "config/visual_motion_agent.json").read_text(encoding="utf-8"))
    from scripts.scene_library_agent import inspect
    from scripts.longform_library_agent import plan as library_plan
    from scripts.twelve_video_plan import build_plan
    import datetime as dt

    categories = channel.get("editorial_categories", [])
    target_seconds = 7200
    ledger_path = root / "music-production/approval_ledger.json"
    seasons = set(seasonal.get("seasons", {}))
    mapping = seasonal.get("playlist_mapping", {})
    queue = build_plan(dt.date(2026, 11, 18))
    scene_folder = root / "music-production/visual-review"
    scene = inspect(scene_folder) if scene_folder.exists() else {
        "status": "PRIVATE_SCENE_LIBRARY_NOT_PRESENT", "image_count": 0,
        "minimum_required": 8, "creative_approval": False, "generated_replacement": False,
    }
    if scene["image_count"] == 0:
        scene["status"] = "PRIVATE_SCENE_LIBRARY_NOT_PRESENT"
    capacity_path = root / "output/library-promotion/production-capacity.json"
    capacity = json.loads(capacity_path.read_text(encoding="utf-8")) if capacity_path.is_file() else None
    library = library_plan(json.loads(ledger_path.read_text(encoding="utf-8"))) if ledger_path.exists() else {
        "status": "PRIVATE_LEDGER_NOT_PRESENT", "approved_seconds": 0.0, "missing_seconds": target_seconds,
    }
    approved_seconds = float(capacity["approved_seconds"]) if capacity else library["approved_seconds"]
    missing_seconds = max(0.0, target_seconds - approved_seconds)
    checks = {
        "editorial_categories": len(categories) == 5,
        "seasonal_matrix": seasons == {"spring", "summer", "autumn", "winter"} and len(mapping) == 5,
        "scene_diversity_policy": seasonal.get("scene_diversity", {}).get("same_focal_instrument_in_every_scene_allowed") is False,
        "scene_library": scene["status"] in {"READY", "PRIVATE_SCENE_LIBRARY_NOT_PRESENT"},
        "queue": len(queue.get("jobs", [])) == 12 and len(queue.get("parallel_music_lanes", [])) == 3,
        "visual_contract": visual.get("allowed_profile") == "single_approved_plate_integrated_motion" and visual.get("motion_contract", {}).get("camera") == "locked",
        "music_policy": policy.get("dedup_required_before_download") is True and policy.get("never_auto_approve") is True,
        "audio_capacity": approved_seconds >= target_seconds,
        "publication_disabled": all(job.get("publication") == "DISABLED" for job in queue.get("jobs", [])),
    }
    return {
        "audit": "project_compliance",
        "status": "PASS" if all(checks.values()) else "BLOCKED",
        "checks": checks,
        "scene_library": scene,
        "audio": {"approved_seconds": approved_seconds, "target_seconds": target_seconds,
                   "missing_seconds": missing_seconds,
                   "status": capacity.get("status") if capacity else library["status"],
                   "source": capacity.get("source") if capacity else "music-production/approval_ledger.json"},
        "queue": {"videos": len(queue.get("jobs", [])),
                  "parallel_music_lanes": queue.get("parallel_music_lanes")},
        "publication": "DISABLED",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = audit(args.root.resolve())
    text = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0 if result["status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())

