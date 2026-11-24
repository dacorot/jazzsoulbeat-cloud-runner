#!/usr/bin/env python3
"""Evidence-bound quality gate for professional visual masters.

This is deliberately a hard contract gate, not a generative art judge. It
rejects a render when its measurable media/provenance contract is incomplete;
creative taste remains represented by the approved visual identity and final
human publication decision.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


def _ratio(width: int, height: int) -> float:
    return width / height if height else 0.0


def inspect(
    video: Path,
    provenance: dict[str, Any],
    *,
    width: int,
    height: int,
    config: dict[str, Any],
) -> dict[str, Any]:
    failures: list[str] = []
    minimum_width, minimum_height = config["minimum_resolution"]
    if width < minimum_width or height < minimum_height:
        failures.append("resolution_below_professional_minimum")
    if abs(_ratio(width, height) - 16 / 9) > 0.01:
        failures.append("aspect_ratio_not_16_9")
    if not video.is_file() or video.stat().st_size == 0:
        failures.append("video_missing_or_empty")
    else:
        actual_hash = hashlib.sha256(video.read_bytes()).hexdigest()
        if provenance.get("video_sha256") != actual_hash:
            failures.append("video_hash_mismatch")
    for field in config["required_provenance"]:
        if not provenance.get(field):
            failures.append(f"missing_provenance:{field}")
    if provenance.get("motion_profile") not in config["allowed_effect_profiles"]:
        failures.append("unapproved_effect_profile")
    for field, expected in config["hard_rules"].items():
        if field == "no_full_frame_particle_overlay":
            if provenance.get("full_frame_particle_overlay") is True:
                failures.append("forbidden_full_frame_particle_overlay")
        elif field == "no_camera_motion":
            if provenance.get("camera") != "locked":
                failures.append("camera_motion_forbidden")
        elif provenance.get(field) != expected:
            failures.append(f"contract_mismatch:{field}")
    return {
        "status": "PASS" if not failures else "FAIL",
        "failures": failures,
        "professional_effects": failures == [],
        "publication": "DISABLED",
    }


def inspect_files(video: Path, provenance_path: Path, config_path: Path, *, width: int, height: int) -> dict[str, Any]:
    provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
    config = json.loads(config_path.read_text(encoding="utf-8"))
    return inspect(video, provenance, width=width, height=height, config=config)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--video", type=Path, required=True)
    parser.add_argument("--provenance", type=Path, required=True)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--width", type=int, required=True)
    parser.add_argument("--height", type=int, required=True)
    args = parser.parse_args()
    result = inspect_files(args.video, args.provenance, args.config, width=args.width, height=args.height)
    print(json.dumps(result, indent=2, sort_keys=True))
    raise SystemExit(0 if result["status"] == "PASS" else 1)
