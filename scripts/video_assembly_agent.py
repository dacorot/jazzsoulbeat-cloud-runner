#!/usr/bin/env python3
"""Plan assembly from already-approved inputs; does not approve or publish."""
from __future__ import annotations
def plan(video_id: str, duration_seconds: int, audio_ids: list[str], visual_profile: str) -> dict:
    if not video_id or duration_seconds <= 0 or not audio_ids:
        raise ValueError("assembly_inputs_incomplete")
    return {"video_id": video_id, "duration_seconds": duration_seconds, "audio_ids": list(audio_ids),
            "visual_profile": visual_profile, "camera": "locked", "state": "PLANNED",
            "creative_approval": False, "rights_verified": False, "publication": "DISABLED"}
def contract() -> dict:
    return {"id": "video_assembly_agent", "requires_approved_audio": True,
            "requires_approved_visual": True, "publication": "DISABLED", "never_publish": True}
