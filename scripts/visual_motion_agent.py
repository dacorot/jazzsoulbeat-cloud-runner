#!/usr/bin/env python3
"""Guarded visual-motion agent for fixed-camera ambient review videos.

This agent has one job: turn one approved style-reference still into a restrained
ambient visual. The camera is locked; motion is localized to coffee steam and
a verified exterior window plate only. It never generates or replaces the scene,
moves the camera, grants creative approval, or publishes anything.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


PROFILE = "single_approved_plate_integrated_motion"
DEFAULT_DURATION = 20
DEFAULT_FPS = 30
DEFAULT_SIZE = (1920, 1080)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def create_plan(image: Path, *, duration: int = DEFAULT_DURATION,
                fps: int = DEFAULT_FPS, width: int = DEFAULT_SIZE[0],
                height: int = DEFAULT_SIZE[1]) -> dict:
    """Create the immutable contract consumed by the visual render step."""
    image = Path(image)
    if not image.is_file():
        raise FileNotFoundError(f"approved_base_image_missing: {image}")
    if duration < DEFAULT_DURATION or duration > 360:
        raise ValueError("visual_motion_agent_duration_must_be_20_to_360_seconds")
    if fps != DEFAULT_FPS:
        raise ValueError("visual_motion_agent_requires_30_fps")
    if (width, height) != DEFAULT_SIZE:
        raise ValueError("visual_motion_agent_requires_1920x1080")
    return {
        "agent_id": "visual_motion_agent",
        "profile": PROFILE,
        "base_image": str(image),
        "base_image_sha256": sha256(image),
        "duration_seconds": duration,
        "motion_cycle_seconds": DEFAULT_DURATION,
        "fps": fps,
        "width": width,
        "height": height,
        "camera": "locked",
        "animated_layers": ["coffee_steam", "window_reflections"],
        "static_layers": ["approved_base_plate"],
        "rain_mode": "audition_only_until_external_masked_compositing_human_review",
        "rain_mask_required": True,
        "rain_placement": "not_in_production",
        "creative_approval": False,
        "publication": "DISABLED",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--image", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--duration", type=int, default=DEFAULT_DURATION)
    parser.add_argument("--fps", type=int, default=DEFAULT_FPS)
    parser.add_argument("--width", type=int, default=DEFAULT_SIZE[0])
    parser.add_argument("--height", type=int, default=DEFAULT_SIZE[1])
    args = parser.parse_args()
    plan = create_plan(args.image, duration=args.duration, fps=args.fps,
                       width=args.width, height=args.height)
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n",
                                encoding="utf-8")
    print(json.dumps(plan, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
