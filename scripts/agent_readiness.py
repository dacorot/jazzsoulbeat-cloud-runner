#!/usr/bin/env python3
"""Run a bounded readiness audit for every local Jazz Soul Beat agent."""
# Regression trigger: rerun after dependency-manifest and workflow-YAML fixes.
from __future__ import annotations

import argparse
import importlib
import json
import subprocess
import sys
from pathlib import Path


def check(name, fn):
    try:
        result = fn()
        return {"name": name, "status": "PASS", "details": result or {}}
    except Exception as exc:  # noqa: BLE001 - audit must report every lane
        return {"name": name, "status": "FAIL", "details": {"error": str(exc)}}


def audit(root: Path) -> dict:
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    image = root / "music-production/visual-review/cafe-library-clean-window-v2-candidate.png"
    ledger = root / "music-production/approval_ledger.json"
    checks = [
        check("visual_motion_agent_contract", lambda: _visual(root, image)),
        check("music_search_policy", lambda: _search(root)),
        check("longform_library_gate", lambda: _library(root, ledger)),
        check("editorial_agent_profiles", lambda: _editorial(root)),
        check("weekly_planner_contract", lambda: _planner()),
        check("twelve_video_production_queue", lambda: _twelve_video_queue()),
        check("pdca_workflow_contract", lambda: _pdca(root)),
        check("audio_adapters_import", lambda: _imports()),
        check("python_compile", lambda: _compile(root)),
    ]
    return {
        "agent_readiness_version": 1,
        "project": "Jazz Soul Beat",
        "checks": checks,
        "technical_status": "READY" if all(c["status"] == "PASS" for c in checks) else "BLOCKED",
        "publication": "DISABLED",
    }


def _visual(root, image):
    from scripts.visual_motion_agent import create_plan
    if not image.exists():
        # The approved base image is intentionally private; validate the
        # renderer contract without copying the source asset into the public repo.
        from scripts.visual_motion_agent import PROFILE
        assert PROFILE == "static_rain_steam_only"
        return {"profile": PROFILE, "base_image_sha256": "private_asset_not_present"}
    plan = create_plan(image)
    assert plan["animated_layers"] == ["coffee_steam"]
    assert plan["camera"] == "locked"
    return {"profile": plan["profile"], "base_image_sha256": plan["base_image_sha256"]}


def _search(root):
    policy = json.loads((root / "config/music_search_policy.json").read_text(encoding="utf-8"))
    assert policy["never_auto_approve"] is True
    assert policy["never_publish"] is True
    assert policy["target_genres"]
    return {"target_genres": policy["target_genres"], "minimum_seconds": policy["minimum_candidate_duration_seconds"]}


def _library(root, ledger):
    from scripts.longform_library_agent import plan
    result = plan(json.loads(ledger.read_text(encoding="utf-8")))
    return {"status": result["status"], "approved_seconds": result["approved_seconds"],
            "missing_seconds": result["missing_seconds"]}


def _editorial(root):
    config = json.loads((root / "config/channel_agents.json").read_text(encoding="utf-8"))
    from scripts.music_briefs import BRIEFS
    categories = config.get("editorial_categories", [])
    ids = [item.get("id") for item in categories]
    missing = [item_id for item_id in ids if item_id not in BRIEFS]
    if len(categories) != 5 or missing:
        raise RuntimeError(f"editorial_profile_mismatch: expected 5 profiles, missing={missing}")
    if any(not item.get("mission") or not item.get("display_name") for item in categories):
        raise RuntimeError("editorial_profile_missing_required_fields")
    return {"profiles": ids, "briefs": len(BRIEFS)}


def _planner():
    from scripts.weekly_planner import plan_week
    import datetime as dt
    plan = plan_week(dt.date(2026, 11, 16))
    jobs = plan.get("jobs", [])
    if len(jobs) != 3 or any(job.get("state") != "PLANNED" for job in jobs):
        raise RuntimeError("weekly_planner_did_not_create_three_planned_jobs")
    return {"jobs": len(jobs), "states": sorted({job["state"] for job in jobs})}


def _pdca(root):
    start = (root / ".github/actions/pdca-start/action.yml").read_text(encoding="utf-8")
    finish = (root / ".github/actions/pdca-finish/action.yml").read_text(encoding="utf-8")
    required_start = ("pdca-start", "drive-pull-state")
    required_finish = ("pdca-do", "pdca-check", "pdca-act", "drive-push-state")
    if any(token not in start for token in required_start):
        raise RuntimeError("pdca_start_contract_incomplete")
    if any(token not in finish for token in required_finish):
        raise RuntimeError("pdca_finish_contract_incomplete")
    return {"plan": True, "do": True, "check": True, "act": True}


def _twelve_video_queue():
    from scripts.twelve_video_plan import build_plan
    import datetime as dt
    result = build_plan(dt.date(2026, 11, 18))
    jobs = result.get("jobs", [])
    if len(jobs) != 12 or any(job.get("visual_profile") != "static_rain_steam_only" for job in jobs):
        raise RuntimeError("twelve_video_queue_contract_incomplete")
    return {"jobs": len(jobs), "parallel_music_lanes": result["parallel_music_lanes"]}


def _imports():
    for module in ("scripts.stable_audio3_producer", "scripts.diffrhythm2_producer",
                   "scripts.music_audio_qc", "scripts.approval_gate", "scripts.production_gate",
                   "scripts.music_producer_agent"):
        importlib.import_module(module)
    return {"modules": 6}


def _compile(root):
    result = subprocess.run([sys.executable, "-m", "compileall", "-q", "scripts"],
                            cwd=root, capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or "compileall failed")
    return {"directory": "scripts"}


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
    return 0 if result["technical_status"] == "READY" else 2


if __name__ == "__main__":
    raise SystemExit(main())
