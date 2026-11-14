#!/usr/bin/env python3
"""Assemble parallel-lane outputs into a traceable delivery/readiness package.

This coordinator never grants music rights, invents missing assets, or publishes.
It reports READY_FOR_REVIEW only when evidence and production media are present.
"""
from __future__ import annotations

import csv
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else "incoming")
OUT = Path(sys.argv[2] if len(sys.argv) > 2 else "delivery-package")
AUDIO = {".mp3", ".wav", ".flac", ".ogg", ".m4a", ".aiff"}
IMAGE = {".png", ".jpg", ".jpeg", ".webp"}
VIDEO = {".mp4", ".mov", ".mkv"}
TEXT = {".txt", ".json", ".csv", ".md", ".log"}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def csv_rows(path: Path):
    try:
        with path.open(newline="", encoding="utf-8-sig") as handle:
            return list(csv.DictReader(handle))
    except (OSError, UnicodeError, csv.Error):
        return []


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    files = sorted(p for p in ROOT.rglob("*") if p.is_file())
    inventory = []
    for path in files:
        rel = path.relative_to(ROOT).as_posix()
        suffix = path.suffix.lower()
        kind = ("audio" if suffix in AUDIO else "image" if suffix in IMAGE
                else "video" if suffix in VIDEO else "report" if suffix in TEXT else "other")
        inventory.append({
            "path": rel, "kind": kind, "bytes": path.stat().st_size,
            "sha256": sha256(path),
        })

    catalogs = [p for p in ROOT.rglob("candidate_catalog.csv")] + [p for p in ROOT.rglob("approved_catalog.csv")]
    catalog_rows = []
    for catalog in catalogs:
        catalog_rows.extend(csv_rows(catalog))
    approved_flag_rows = [
        row for row in catalog_rows
        if any((row.get(field) or "").strip().lower() in {"1", "true", "yes", "approved"}
               for field in ("approved", "rights_verified"))
    ]
    audio_candidates = [x for x in inventory if x["kind"] == "audio" and "parallel-video-engine-qa" not in x["path"].lower()]
    scene_images = [
        x for x in inventory if x["kind"] == "image"
        and any(token in x["path"].lower() for token in ("scenes/", "visual-agents/"))
    ]
    review_videos = [
        x for x in inventory if x["kind"] == "video" and "review" in x["path"].lower()
    ]
    final_videos = [
        x for x in inventory if x["kind"] == "video" and x not in review_videos
        and ("final" in Path(x["path"]).name.lower() or "delivery" in x["path"].lower())
    ]
    synthetic_videos = [
        x for x in inventory if x["kind"] == "video"
        and x not in final_videos and x not in review_videos
    ]

    gates = {
        "audio_candidates_delivered": bool(audio_candidates),
        "rights_approved_catalog_entries": bool(approved_flag_rows),
        "original_scene_images_delivered": len(scene_images) >= 8,
        "final_video_delivered": bool(final_videos),
    }
    ready = all(gates.values())
    report = {
        "project": "Jazz Soul Beat",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "READY_FOR_HUMAN_REVIEW" if ready else "BLOCKED_INCOMPLETE_INPUTS",
        "publication": "NOT_AUTHORIZED - no upload or publication performed",
        "summary": {
            "files_received": len(inventory),
            "audio_candidates": len(audio_candidates),
            "original_scene_images": len(scene_images),
            "minimum_original_scene_images_required": 8,
            "final_videos": len(final_videos),
            "review_videos": len(review_videos),
            "synthetic_qa_videos": len(synthetic_videos),
            "catalog_rows": len(catalog_rows),
            "approved_catalog_rows_detected": len(approved_flag_rows),
        },
        "gates": gates,
        "inventory": inventory,
        "limitations": [
            "A catalog flag is not independent legal advice; retain source license and rights evidence.",
            "Passing technical QA does not constitute creative approval.",
            "This coordinator inventories and packages delivered outputs; it does not fabricate missing assets.",
            "No public or private YouTube upload is performed by this workflow.",
        ],
    }
    (OUT / "delivery_manifest.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    lines = [
        "# Jazz Soul Beat — Delivery coordination",
        "",
        f"**Status:** {report['status']}",
        "",
        f"Files received: {len(inventory)} | audio candidates: {len(audio_candidates)} | original scenes: {len(scene_images)} | review videos: {len(review_videos)} | final videos: {len(final_videos)} | synthetic QA videos: {len(synthetic_videos)}",
        "",
        "## Delivery gates",
    ]
    lines += [f"- [{'x' if passed else ' '}] {name.replace('_', ' ')}" for name, passed in gates.items()]
    lines += [
        "",
        "## Required next actions",
        "- Review candidate audio item by item; deliver only tracks with documented rights-holder authority, license, source URL and attribution.",
        "- Deliver at least eight original scene images in the category scene library; synthetic QA frames do not count.",
        "- Render the full-length video only after approved audio covers the requested duration; synthetic test MP4s do not count.",
        "- Run final media and creative QA; keep publication blocked until explicit owner approval.",
        "",
        "See delivery_manifest.json for the file inventory and SHA-256 checksums.",
    ]
    (OUT / "DELIVERY_REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "summary": report["summary"], "gates": gates}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
