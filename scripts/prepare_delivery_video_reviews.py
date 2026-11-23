#!/usr/bin/env python3
"""Create hash-bound creative review requests for an existing private delivery."""
from __future__ import annotations

import argparse
import hashlib
import json
import secrets
from datetime import datetime, timezone
from pathlib import Path


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def prepare(manifest_path: Path, agent_root: Path, ledger_path: Path, plan_path: Path) -> dict:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    ledger = json.loads(ledger_path.read_text(encoding="utf-8")) if ledger_path.is_file() else {
        "schema_version": 1, "requests": {}
    }
    requests = ledger.setdefault("requests", {})
    created = []
    for item in manifest.get("videos", []):
        relative = Path(item["video"])
        artifact = relative if relative.is_absolute() else agent_root / relative
        if not artifact.is_file():
            raise FileNotFoundError(f"delivery_video_missing:{artifact}")
        actual_hash = digest(artifact)
        if actual_hash != item.get("sha256"):
            raise ValueError(f"delivery_video_hash_mismatch:{artifact}")
        existing = next((r for r in requests.values()
                         if r.get("artifact_sha256") == actual_hash
                         and r.get("artifact_kind") == "video"), None)
        if existing:
            created.append(existing)
            continue
        request_id = "r_" + secrets.token_urlsafe(18)
        request = {
            "request_id": request_id,
            "created_at_utc": now(),
            "artifact": str(artifact),
            "artifact_sha256": actual_hash,
            "artifact_kind": "video",
            "status": "PENDING_HUMAN_REVIEW",
            "creative_approval": False,
            "rights_verified": False,
            "eligible_for_video_assembly": False,
            "private_upload_approval": False,
            "public_upload_approval": False,
            "youtube_upload": "NOT_AUTHORIZED",
            "delivery_video": relative.as_posix(),
            "duration_seconds": item.get("duration_seconds"),
            "events": [{"type": "delivery_video_review_request_created", "at_utc": now(),
                        "artifact_sha256": actual_hash}],
        }
        requests[request_id] = request
        created.append(request)
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    ledger_path.write_text(json.dumps(ledger, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    plan = {"status": "READY", "request_count": len(created),
            "request_ids": [r["request_id"] for r in created],
            "ledger": str(ledger_path), "created_at_utc": now()}
    plan_path.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return plan


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--agent-root", type=Path, required=True)
    parser.add_argument("--ledger", type=Path, required=True)
    parser.add_argument("--plan", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(prepare(args.manifest.resolve(), args.agent_root.resolve(),
                             args.ledger.resolve(), args.plan.resolve()), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
