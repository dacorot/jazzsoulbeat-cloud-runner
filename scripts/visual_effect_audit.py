#!/usr/bin/env python3
"""Hard gate for declared, executed and reviewable visual effects."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ALLOWED = {
    "localized_coffee_steam",
    "window_reflections",
    "masked_window_atmosphere",
    "approved_plate_localized_atmosphere",
}


def audit(video: Path, provenance: dict, effect_report: dict) -> dict:
    failures = []
    effects = provenance.get("effect_manifest", {}).get("effects", [])
    mask_status = provenance.get("effect_manifest", {}).get("mask_status", "")
    # A clean locked plate is safer than an unmasked effect. Effects are
    # optional; any declared effect still requires a verified scene mask.
    if not effects and mask_status != "no_verified_scene_masks_no_effects":
        failures.append("empty_effect_manifest_without_safe_status")
    if any(effect not in ALLOWED for effect in effects):
        failures.append("unapproved_effect_profile")
    if provenance.get("camera") != "locked":
        failures.append("camera_not_locked")
    if provenance.get("effect_manifest", {}).get("mask_required") is not True:
        failures.append("effect_mask_not_required")
    if effect_report.get("execution_status") != "RENDERED":
        failures.append("effects_not_executed")
    if not effects and effect_report.get("mask_status") != "no_verified_scene_masks_no_effects":
        failures.append("empty_effect_report_without_safe_status")
    if effect_report.get("video_sha256") != provenance.get("video_sha256"):
        failures.append("effect_report_video_hash_mismatch")
    if not video.is_file() or video.stat().st_size == 0:
        failures.append("video_missing_or_empty")
    return {
        "status": "PASS" if not failures else "FAIL",
        "failures": failures,
        "effects": effects,
        "effects_verified": not failures,
        "auditors_required": ["supervisor", "coordinator", "visual_director", "quality_auditor"],
        "publication": "DISABLED",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--video", type=Path, required=True)
    parser.add_argument("--provenance", type=Path, required=True)
    parser.add_argument("--effect-report", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    provenance = json.loads(args.provenance.read_text(encoding="utf-8"))
    effect_report = json.loads(args.effect_report.read_text(encoding="utf-8"))
    result = audit(args.video, provenance, effect_report)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
