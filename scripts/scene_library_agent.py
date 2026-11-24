#!/usr/bin/env python3
"""Validate private scene-library inputs without inventing missing visuals."""
from __future__ import annotations

from pathlib import Path

IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp"}


def inspect(folder: Path, minimum: int = 8) -> dict:
    images = sorted(p for p in folder.rglob("*") if p.is_file() and p.suffix.lower() in IMAGE_SUFFIXES)
    effects = sorted(p for p in folder.rglob("*") if p.is_file() and p.suffix.lower() in {".mp4", ".webm", ".mov"})
    technically_complete = len(images) >= minimum and bool(effects)
    return {"status": "READY_TECHNICAL_REVIEW_REQUIRED" if technically_complete else "BLOCKED_INCOMPLETE_SCENE_LIBRARY",
            "image_count": len(images), "minimum_required": minimum,
            "effect_count": len(effects), "effects_required": True,
            "creative_approval": False, "animation_approval": False,
            "eligible_for_video_assembly": False, "generated_replacement": False}


def contract() -> dict:
    return {"id": "scene_library_agent", "minimum_scene_images": 8,
            "never_replace_approved_base": True, "never_publish": True}
