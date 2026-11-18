"""Crash-safe sequential coordinator for the Jazz Soul Beat pipeline."""
from __future__ import annotations

import json
from pathlib import Path

STAGES = (
    "MUSIC_DISCOVERY", "RIGHTS_AND_AUDIO_QA", "VIDEO_ASSEMBLY",
    "RELEASE_QA", "WAITING_HUMAN_APPROVAL", "PRIVATE_UPLOAD",
    "VERIFY_UPLOAD", "PDCA_COMPLETE",
)
TRANSITIONS = {
    "MUSIC_DISCOVERY": "RIGHTS_AND_AUDIO_QA",
    "RIGHTS_AND_AUDIO_QA": "VIDEO_ASSEMBLY",
    "VIDEO_ASSEMBLY": "RELEASE_QA",
    "RELEASE_QA": "WAITING_HUMAN_APPROVAL",
    "WAITING_HUMAN_APPROVAL": "PRIVATE_UPLOAD",
    "PRIVATE_UPLOAD": "VERIFY_UPLOAD",
    "VERIFY_UPLOAD": "PDCA_COMPLETE",
}


def contract() -> dict:
    return {"id": "orchestrator_agent", "pdca": True,
            "sequential_videos": True, "resumable": True,
            "public_upload": False, "never_publish": True,
            "human_gate": "final_video_approval"}


def new_checkpoint(video_id: str) -> dict:
    if not video_id.strip():
        raise ValueError("video_id_required")
    return {"schema_version": 1, "video_id": video_id, "stage": STAGES[0],
            "completed_stages": [], "human_approval": False,
            "private_upload": False, "public_upload": False,
            "pdca_events": [], "status": "RUNNABLE"}


def advance(checkpoint: dict, *, stage_complete: bool = False,
            human_approved: bool = False, upload_verified: bool = False) -> dict:
    current = checkpoint.get("stage")
    if current not in STAGES:
        raise ValueError("invalid_checkpoint_stage")
    if current == "WAITING_HUMAN_APPROVAL" and not human_approved:
        return {**checkpoint, "status": "WAITING_HUMAN_APPROVAL"}
    if current == "VERIFY_UPLOAD" and not upload_verified:
        return {**checkpoint, "status": "WAITING_UPLOAD_VERIFICATION"}
    if current not in {"WAITING_HUMAN_APPROVAL", "VERIFY_UPLOAD"} and not stage_complete:
        return {**checkpoint, "status": "WAITING_STAGE_COMPLETION"}
    next_stage = TRANSITIONS.get(current)
    completed = list(checkpoint.get("completed_stages", []))
    if current not in completed:
        completed.append(current)
    result = {**checkpoint, "completed_stages": completed}
    if current == "WAITING_HUMAN_APPROVAL":
        result["human_approval"] = True
    if current == "PRIVATE_UPLOAD":
        result["private_upload"] = True
    if current == "VERIFY_UPLOAD":
        result["upload_verified"] = True
    if next_stage is None:
        result["stage"] = "PDCA_COMPLETE"
        result["status"] = "COMPLETE"
        result["pdca_events"] = [*checkpoint.get("pdca_events", []),
                                  {"cycle": "CHECK", "result": "complete"}]
    else:
        result["stage"] = next_stage
        result["status"] = "WAITING_HUMAN_APPROVAL" if next_stage == "WAITING_HUMAN_APPROVAL" else "RUNNABLE"
    return result


def save_checkpoint(path: Path, checkpoint: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(checkpoint, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)
