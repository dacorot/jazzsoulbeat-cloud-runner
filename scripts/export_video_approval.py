#!/usr/bin/env python3
"""Export a YouTube upload manifest only after all independent approvals exist."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def export(ledger_path: Path, request_id: str, output: Path) -> dict:
    ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
    request = ledger.get("requests", {}).get(request_id)
    if not request:
        raise RuntimeError("review_request_not_found")
    artifact = Path(request.get("artifact", ""))
    actual = sha256(artifact) if artifact.is_file() else None
    if request.get("artifact_kind") != "video":
        raise RuntimeError("video_request_required")
    if actual != request.get("artifact_sha256"):
        raise RuntimeError("artifact_hash_changed")
    required = ("creative_approval", "rights_verified")
    if any(request.get(key) is not True for key in required):
        raise RuntimeError("independent_video_approvals_incomplete")
    public = request.get("youtube_upload") == "PUBLIC_SCHEDULED_AUTHORIZED"
    private = request.get("youtube_upload") == "PRIVATE_ONLY_AUTHORIZED"
    if not (public or private):
        raise RuntimeError("youtube_upload_authorization_missing")
    if public and not request.get("publication_at_utc"):
        raise RuntimeError("public_schedule_time_missing")
    record = {
        "request_id": request_id,
        "video": str(artifact),
        "video_sha256": actual,
        "creative_approval": True,
        "rights_verified": True,
        "private_upload_approval": bool(request.get("private_upload_approval")),
        "public_upload_approval": bool(request.get("public_upload_approval")),
        "youtube_visibility": "scheduled_public" if public else "private",
        "publication": "scheduled_public" if public else "private_only",
        "publication_at_utc": request.get("publication_at_utc"),
        "publication_status": "SCHEDULED_PUBLIC" if public else "NOT_PUBLIC",
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return record


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ledger", type=Path, required=True)
    parser.add_argument("--request-id", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        print(json.dumps(export(args.ledger, args.request_id, args.output), indent=2))
        return 0
    except (OSError, ValueError, RuntimeError) as exc:
        print(json.dumps({"status": "BLOCKED", "reason": str(exc)}, indent=2))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
