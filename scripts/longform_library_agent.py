#!/usr/bin/env python3
"""Check whether the approved audio library can support a 2–3 hour video."""
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path


TARGET_SECONDS = 7200
MAX_TARGET_SECONDS = 10800


def media_duration(path: str) -> float:
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=nw=1:nk=1", path],
            check=True, capture_output=True, text=True, timeout=30,
        )
        return float(result.stdout.strip())
    except (OSError, subprocess.SubprocessError, ValueError):
        return 0.0


def plan(ledger: dict, target_seconds: int = TARGET_SECONDS) -> dict:
    if not 7200 <= target_seconds <= MAX_TARGET_SECONDS:
        raise ValueError("longform_target_must_be_between_2_and_3_hours")
    approved = []
    seen = set()
    for request_id, request in ledger.get("requests", {}).items():
        if request.get("artifact_kind") != "audio":
            continue
        if not all(request.get(field) is True for field in (
                "creative_approval", "rights_verified", "eligible_for_video_assembly")):
            continue
        artifact = str(request.get("artifact", ""))
        digest = request.get("artifact_sha256")
        key = (artifact, digest)
        if key in seen:
            continue
        seen.add(key)
        duration = request.get("duration_seconds")
        if duration is None:
            duration = request.get("technical_duration_seconds", 0)
        if not duration and Path(artifact).is_file():
            duration = media_duration(artifact)
        approved.append({"request_id": request_id, "artifact": artifact,
                         "artifact_sha256": digest, "duration_seconds": float(duration or 0)})
    approved.sort(key=lambda row: row["request_id"])
    total = sum(row["duration_seconds"] for row in approved)
    missing = max(0.0, target_seconds - total)
    return {
        "agent_id": "longform_library_agent",
        "target_seconds": target_seconds,
        "approved_unique_tracks": len(approved),
        "approved_seconds": round(total, 2),
        "missing_seconds": round(missing, 2),
        "status": "READY_FOR_LONGFORM_ASSEMBLY" if missing == 0 else "BLOCKED_NEEDS_MORE_APPROVED_TRACKS",
        "tracks": approved,
        "no_track_repetition": True,
        "publication": "DISABLED"
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ledger", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--target-seconds", type=int, default=TARGET_SECONDS,
                        help="Long-form target in the 2–3 hour range (7200–10800 seconds).")
    args = parser.parse_args()
    result = plan(json.loads(args.ledger.read_text(encoding="utf-8")), args.target_seconds)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result["status"] == "READY_FOR_LONGFORM_ASSEMBLY" else 2


if __name__ == "__main__":
    raise SystemExit(main())
