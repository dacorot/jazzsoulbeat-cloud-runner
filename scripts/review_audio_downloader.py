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

try:
    from scripts.music_dedup_agent import compare, load_rows
except ModuleNotFoundError as exc:  # direct execution from the workflow
    if exc.name != "scripts":
        raise
    from music_dedup_agent import compare, load_rows

MAX_BYTES = 30_000_000
SUFFIXES = {".mp3", ".flac", ".ogg", ".wav", ".m4a", ".aiff"}

# Editorial exclusions approved for removal from review staging.
EXCLUDED_TITLES = {"vibing over venus", "got funk", "style funk", "c-funk", "enter the party", "funky chunk", "kool kats"}


def contract() -> dict:
    return {"id": "review_audio_downloader", "compare_before_download": True,
            "review_only": True, "never_auto_approve": True, "never_publish": True}


def safe_name(value: str) -> str:
    result = "".join(ch if ch.isalnum() or ch in "._-" else "_" for ch in str(value or "candidate"))
    return result.strip("._")[:100] or "candidate"


def download_url(row: dict) -> str:
    for key in ("download_url", "file_url", "audio_url", "download", "url"):
        value = str(row.get(key) or "").strip()
        if value.startswith(("http://", "https://")):
            return value
    return ""


def download_unique(existing: list[dict], candidates: list[dict], output: Path, limit: int = 40, offset: int = 0) -> dict:
    excluded = [row for row in candidates if str(row.get("title") or "").strip().casefold() in EXCLUDED_TITLES]
    candidates = [row for row in candidates if str(row.get("title") or "").strip().casefold() not in EXCLUDED_TITLES]
    dedup = compare(existing, candidates)
    output.mkdir(parents=True, exist_ok=True)
    manifest = []
    skipped = []
    for index, row in enumerate(dedup["unique"][offset:offset + limit], 1):
        url = download_url(row)
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"}:
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
                content_type = str(response.headers.get("Content-Type") or "").lower()
                first_chunk = response.read(1024 * 1024)
                magic_ok = first_chunk.startswith((b"ID3", b"OggS", b"fLaC", b"RIFF"))
                if not magic_ok and not content_type.startswith("audio/") and "octet-stream" not in content_type:
                    raise ValueError("response_is_not_audio")
                chunk = first_chunk
                while chunk:
                    total += len(chunk)
                    if total > MAX_BYTES:
                        raise ValueError("audio_candidate_exceeds_30MB")
                    digest.update(chunk)
                    handle.write(chunk)
                    chunk = response.read(1024 * 1024)
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
              "excluded_count": len(excluded), "excluded_titles": sorted({row.get("title", "") for row in excluded}),
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
    parser.add_argument("--offset", type=int, default=0)
    args = parser.parse_args()
    report = download_unique(load_rows(args.existing), load_rows(args.candidates), args.output, args.limit, args.offset)
    print(json.dumps({k: report[k] for k in ("status", "downloaded_count", "skipped_count", "approval_mutated", "rights_verified", "publication")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
