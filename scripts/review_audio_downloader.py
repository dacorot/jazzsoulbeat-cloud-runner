#!/usr/bin/env python3
"""Download unique audio candidates into a review-only, hash-bound staging area.

This is deliberately not a production importer: it never changes rights,
creative approval, catalog eligibility or publication state.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import urllib.request
from pathlib import Path
from urllib.parse import urlparse

from scripts.music_dedup_agent import compare, load_rows

MAX_BYTES = 30_000_000
SUFFIXES = {".mp3", ".flac", ".ogg", ".wav", ".m4a", ".aiff"}


def contract() -> dict:
    return {"id": "review_audio_downloader", "compare_before_download": True,
            "review_only": True, "never_auto_approve": True, "never_publish": True}


def safe_name(value: str) -> str:
    result = "".join(ch if ch.isalnum() or ch in "._-" else "_" for ch in str(value or "candidate"))
    return result.strip("._")[:100] or "candidate"


def download_unique(existing: list[dict], candidates: list[dict], output: Path, limit: int = 40) -> dict:
    dedup = compare(existing, candidates)
    output.mkdir(parents=True, exist_ok=True)
    manifest = []
    skipped = []
    for index, row in enumerate(dedup["unique"][:limit], 1):
        url = str(row.get("download_url") or row.get("source_url") or "").strip()
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"} or not row.get("download_url"):
            skipped.append({"candidate": row, "reason": "download_url_missing_or_invalid"})
            continue
        target = output / f"{index:03d}-{safe_name(row.get('title'))}{Path(parsed.path).suffix.lower()}"
        if target.suffix.lower() not in SUFFIXES:
            target = target.with_suffix(".audio")
        request = urllib.request.Request(url, headers={"User-Agent": "JazzSoulBeatReviewDownloader/1.0"})
        digest = hashlib.sha256()
        total = 0
        try:
            with urllib.request.urlopen(request, timeout=60) as response, target.open("wb") as handle:
                while True:
                    chunk = response.read(1024 * 1024)
                    if not chunk:
                        break
                    total += len(chunk)
                    if total > MAX_BYTES:
                        raise ValueError("audio_candidate_exceeds_30MB")
                    digest.update(chunk)
                    handle.write(chunk)
            manifest.append({"title": row.get("title", ""), "creator": row.get("creator") or row.get("artist", ""),
                             "source_url": row.get("source_url", ""), "download_url": url,
                             "file": str(target), "bytes": total, "sha256": digest.hexdigest(),
                             "rights_status": "pending_primary_source_and_rights_review",
                             "creative_approval": False, "rights_verified": False,
                             "eligible_for_video_assembly": False, "youtube_upload": "NOT_AUTHORIZED"})
        except Exception as error:  # keep the lane auditable and continue
            if target.exists():
                target.unlink()
            skipped.append({"candidate": row, "reason": str(error)[:200]})
    report = {"status": "REVIEW_ONLY_DOWNLOADED", "dedup": dedup,
              "downloaded_count": len(manifest), "skipped_count": len(skipped),
              "downloaded": manifest, "skipped": skipped,
              "approval_mutated": False, "rights_verified": False,
              "publication": "DISABLED"}
    (output / "review-download-manifest.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--existing", nargs="*", type=Path, default=[])
    parser.add_argument("--candidates", nargs="*", type=Path, default=[])
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--limit", type=int, default=40)
    args = parser.parse_args()
    report = download_unique(load_rows(args.existing), load_rows(args.candidates), args.output, args.limit)
    print(json.dumps({k: report[k] for k in ("status", "downloaded_count", "skipped_count", "approval_mutated", "rights_verified", "publication")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
