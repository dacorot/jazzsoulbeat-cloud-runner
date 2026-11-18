#!/usr/bin/env python3
"""Read-only heartbeat and checkpoint health audit for the pipeline."""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

STALE_SECONDS = 24 * 60 * 60
VALID_STAGES = {
    "MUSIC_DISCOVERY", "RIGHTS_AND_AUDIO_QA", "VIDEO_ASSEMBLY", "RELEASE_QA",
    "WAITING_HUMAN_APPROVAL", "PRIVATE_UPLOAD", "VERIFY_UPLOAD", "PDCA_COMPLETE",
}


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _fingerprint(value: Any) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:20]


def audit(root: Path, report_path: Path) -> dict[str, Any]:
    checkpoints = sorted(root.rglob("*.checkpoint.json")) if root.exists() else []
    now = _now()
    items = []
    status = "HEALTHY_IDLE"
    for path in checkpoints:
        item: dict[str, Any] = {"path": str(path), "status": "HEALTHY", "fingerprint": ""}
        try:
            checkpoint = json.loads(path.read_text(encoding="utf-8"))
            stage = checkpoint.get("stage")
            if checkpoint.get("schema_version") != 1 or stage not in VALID_STAGES:
                raise ValueError("invalid_checkpoint_schema_or_stage")
            age_seconds = max(0, (now - datetime.fromtimestamp(path.stat().st_mtime, timezone.utc)).total_seconds())
            item.update({"video_id": checkpoint.get("video_id"), "stage": stage, "age_seconds": round(age_seconds), "fingerprint": _fingerprint(checkpoint)})
            if age_seconds > STALE_SECONDS and checkpoint.get("status") not in {"COMPLETE", "WAITING_HUMAN_APPROVAL"}:
                item["status"] = "STALE_CHECKPOINT"
                status = "ALERT"
            elif status != "ALERT":
                status = "HEALTHY"
        except (OSError, json.JSONDecodeError, ValueError, TypeError) as exc:
            item.update({"status": "INVALID_CHECKPOINT", "error": f"{type(exc).__name__}: {str(exc)[:160]}"})
            status = "ALERT"
        items.append(item)
    report = {
        "schema_version": 1,
        "agent": "pipeline_health_agent",
        "checked_at": now.isoformat(timespec="seconds"),
        "status": status,
        "checkpoint_count": len(items),
        "checkpoints": items,
        "policy": {"read_only": True, "automatic_recovery": False, "automatic_publication": False},
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    report = audit(args.root, args.report)
    print(json.dumps({"status": report["status"], "checkpoint_count": report["checkpoint_count"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
