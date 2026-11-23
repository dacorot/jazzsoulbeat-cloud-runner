#!/usr/bin/env python3
"""Guarded visual-motion agent for fixed-camera ambient review videos.

This agent selects one approved scene and one approved localized effect profile.
It never generates or replaces the scene, moves the camera, grants creative
approval, or publishes anything.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


PROFILES = {
    "rain": (["window_rain"], ["rain_masked"]),
    "steam": (["coffee_steam"], ["approved_base_plate"]),
    "mist": (["localized_mist"], ["approved_base_plate"]),
    "snow": (["window_snow"], ["snow_masked"]),
    "breeze": (["curtain_breeze"], ["approved_base_plate"]),
}
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
                height: int = DEFAULT_SIZE[1], effect_profile: str = "rain") -> dict:
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
    if effect_profile not in PROFILES:
        raise ValueError("visual_motion_agent_unknown_effect_profile")
    animated_layers, static_layers = PROFILES[effect_profile]
    return {
        "agent_id": "visual_motion_agent",
        "profile": effect_profile,
        "base_image": str(image),
        "base_image_sha256": sha256(image),
        "duration_seconds": duration,
        "motion_cycle_seconds": DEFAULT_DURATION,
        "fps": fps,
        "width": width,
        "height": height,
        "camera": "locked",
        "animated_layers": animated_layers,
        "static_layers": static_layers,
        "effect_profile": effect_profile,
        "rain_placement": "behind_window_mullions" if effect_profile == "rain" else "not_applicable",
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
    parser.add_argument("--effect-profile", choices=sorted(PROFILES), default="rain")
    args = parser.parse_args()
    plan = create_plan(args.image, duration=args.duration, fps=args.fps,
                       width=args.width, height=args.height,
                       effect_profile=args.effect_profile)
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n",
                                encoding="utf-8")
    print(json.dumps(plan, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
