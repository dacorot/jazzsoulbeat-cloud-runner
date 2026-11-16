#!/usr/bin/env python3
"""Evidence-based readiness audit; never promotes or approves any artifact."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def source_evidence(root: Path, path: Path) -> dict:
    """Return portable, hash-bound evidence for an audit input file."""
    relative = path.relative_to(root).as_posix()
    return {
        "path": relative,
        "sha256": sha256(path) if path.is_file() else None,
        "exists": path.is_file(),
    }


def probe(path: Path) -> dict:
    result = subprocess.run([
        "ffprobe", "-v", "error", "-show_entries",
        "stream=codec_type,codec_name,width,height,channels:format=duration", "-of", "json", str(path)
    ], check=True, capture_output=True, text=True)
    return json.loads(result.stdout)


def audit(root: Path) -> dict:
    music_root = root / "music-production"
    ledger_path = music_root / "approval_ledger.json"
    ledger = json.loads(ledger_path.read_text(encoding="utf-8")) if ledger_path.is_file() else {"requests": {}}
    ledger_requests = ledger.get("requests", {})
    candidates = []
    index_path = music_root / "AUDITION_INDEX.json"
    if index_path.is_file():
        index = json.loads(index_path.read_text(encoding="utf-8"))
        for item in index.get("candidates", []):
            path = root / item["file"]
            intact = path.is_file() and sha256(path) == item.get("sha256")
            request = ledger_requests.get(item.get("approval_request_id"), {})
            request_matches = (
                request.get("status") != "SUPERSEDED"
                and Path(request.get("artifact", "")).resolve() == path.resolve()
                and request.get("artifact_sha256") == item.get("sha256")
                and request.get("artifact_sha256") == (sha256(path) if intact else None)
            )
            candidates.append({"title": item.get("title"), "file": str(path), "hash_intact": intact,
                               "creative_approval": request_matches and request.get("creative_approval") is True,
                               "rights_verified": request_matches and request.get("rights_verified") is True})
    review_reports = sorted((music_root / "visual-review").glob("*.review.json")) if (music_root / "visual-review").is_dir() else []
    qhd_reviews = []
    for report_path in review_reports:
        report = json.loads(report_path.read_text(encoding="utf-8"))
        raw_video = Path(report.get("video", ""))
        video = raw_video if raw_video.is_absolute() else root / raw_video
        expected_video_hash = str(report.get("video_sha256", "")).strip()
        video_intact = video.is_file() and bool(expected_video_hash) and sha256(video) == expected_video_hash
        qhd_reviews.append({"file": str(video), "manifest_status": report.get("status"),
                            "file_intact": video_intact,
                            "qhd": report.get("width") == 2560 and report.get("height") == 1440,
                            "duration_seconds": report.get("duration_seconds"),
                            "creative_approval": report.get("creative_approval") is True})
    requests = [x for x in ledger_requests.values() if x.get("status") != "SUPERSEDED"]
    gates = {
        "original_audio_candidate_with_intact_hash": any(x["hash_intact"] for x in candidates),
        "human_creative_audio_approval": any(x["creative_approval"] for x in candidates),
        "rights_verification": any(x["rights_verified"] for x in candidates),
        "qhd_review_render_exists": any(x["qhd"] and x["file_intact"] for x in qhd_reviews),
        "full_2_to_3_hour_final_video": any(
            x["qhd"] and x["file_intact"] and (x.get("duration_seconds") or 0) >= 7200
            and x.get("creative_approval") for x in qhd_reviews
        ),
        "telegram_credentials_configured": all(os.environ.get(name, "").strip() for name in (
            "TELEGRAM_BOT_TOKEN", "JAZZ_SOUL_BEAT_TELEGRAM_REVIEWER_ID", "JAZZ_SOUL_BEAT_TELEGRAM_CHAT_ID")),
        "private_upload_approval": any(x.get("youtube_upload") == "PRIVATE_ONLY_AUTHORIZED" for x in requests),
    }
    sources = {"approval_ledger": source_evidence(root, ledger_path)}
    if index_path.is_file():
        sources["audition_index"] = source_evidence(root, index_path)
    return {
        "status": "READY" if all(gates.values()) else "INCOMPLETE",
        "generated_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "sources": sources,
        "gates": gates,
        "candidate_count": len(candidates), "candidates": candidates,
        "qhd_review_count": len(qhd_reviews), "qhd_reviews": qhd_reviews,
        "approval_request_count": len(requests),
        "publication": "DISABLED", "note": "This audit reports evidence; it never approves, uploads or publishes.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = audit(args.root.resolve())
    serialized = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(serialized, encoding="utf-8")
    print(serialized, end="")
    return 0 if result["status"] == "READY" else 1


if __name__ == "__main__":
    raise SystemExit(main())
