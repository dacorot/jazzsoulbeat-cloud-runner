#!/usr/bin/env python3
"""Build a QHD video review only from a fully approved audio request."""
from __future__ import annotations

import argparse
import json
import secrets
from pathlib import Path

try:
    from scripts.approval_gate import ledger_lock, load, save, sha256, utc_now
    from scripts.render_review_video import render
except ModuleNotFoundError as exc:  # direct execution from scripts/
    # Only fall back for the two package modules.  A missing third-party
    # dependency (for example Pillow) must remain visible instead of being
    # misreported as a broken direct-execution import.
    if exc.name not in {"scripts", "scripts.approval_gate", "scripts.render_review_video"}:
        raise
    from approval_gate import ledger_lock, load, save, sha256, utc_now
    from render_review_video import render


def prepare(ledger_path: Path, audio_request_id: str, image: Path,
            output: Path, duration: int = 240,
            rain_mode: str = "procedural_window") -> dict:
    with ledger_lock(ledger_path):
        ledger = load(ledger_path)
        audio_request = ledger["requests"].get(audio_request_id)
        if not audio_request:
            raise ValueError("audio_request_not_found")
        if audio_request.get("artifact_kind") != "audio":
            raise ValueError("source_request_must_be_audio")
        for field in ("creative_approval", "rights_verified", "eligible_for_video_assembly"):
            if audio_request.get(field) is not True:
                raise ValueError(f"source_audio_{field}_missing")
        audio = Path(audio_request["artifact"])
        if not audio.is_absolute():
            audio = Path.cwd() / audio
        if not audio.is_file() or sha256(audio) != audio_request.get("artifact_sha256"):
            raise ValueError("source_audio_hash_changed")
        if not image.is_file():
            raise ValueError("review_image_missing")
        # Preserve compatibility with lightweight render fakes used by older
        # integration tests while allowing explicit integrated-plate mode.
        if rain_mode == "procedural_window":
            report = render(audio, image, output, duration)
        else:
            report = render(audio, image, output, duration, rain_mode)
        report_path = output.with_suffix(".review.json")
        report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

        request_id = "r_" + secrets.token_urlsafe(18)
        artifact_value = output.as_posix() if not output.is_absolute() else str(output)
        output_hash = sha256(output)
        ledger["requests"][request_id] = {
            "request_id": request_id,
            "created_at_utc": utc_now(),
            "artifact": artifact_value,
            "artifact_sha256": output_hash,
            "artifact_kind": "video",
            "source_audio_request_id": audio_request_id,
            "status": "PENDING_HUMAN_REVIEW",
            "creative_approval": False,
            "rights_verified": False,
            "eligible_for_video_assembly": False,
            "private_upload_approval": False,
            "youtube_upload": "NOT_AUTHORIZED",
            "events": [{"type": "video_review_request_created", "at_utc": utc_now(),
                        "source_audio_request_id": audio_request_id,
                        "artifact_sha256": output_hash}],
        }
        save(ledger_path, ledger)
    return {"status": "VIDEO_REVIEW_PENDING", "request_id": request_id,
            "source_audio_request_id": audio_request_id,
            "artifact": artifact_value, "artifact_sha256": output_hash,
            "review_manifest": str(report_path)}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ledger", type=Path, required=True)
    parser.add_argument("--audio-request-id", required=True)
    parser.add_argument("--image", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--duration", type=int, default=240)
    parser.add_argument("--rain-mode", choices=("procedural_window", "integrated_plate", "masked_window"),
                        default="procedural_window")
    args = parser.parse_args()
    try:
        print(json.dumps(prepare(args.ledger, args.audio_request_id, args.image,
                                 args.output, args.duration, args.rain_mode), indent=2))
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "BLOCKED", "reason": str(exc)}, indent=2))
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
