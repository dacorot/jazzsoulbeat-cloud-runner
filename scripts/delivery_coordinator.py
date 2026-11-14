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

    catalogs = [p for p in ROOT.rglob("approved_catalog.csv")]
    approved_rows = []
    for catalog in catalogs:
        approved_rows.extend(csv_rows(catalog))
    approved_flag_rows = [
        row for row in approved_rows
        if (row.get("approved") or row.get("rights_verified") or "").strip().lower()
        in {"1", "true", "yes", "approved"}
    ]
    audio_files = [x for x in inventory if x["kind"] == "audio"]
    image_files = [x for x in inventory if x["kind"] == "image"]
    video_files = [x for x in inventory if x["kind"] == "video"]

    gates = {
        "audio_files_delivered": bool(audio_files),
        "rights_approved_catalog_entries": bool(approved_flag_rows),
        "visual_assets_delivered": bool(image_files),
        "final_video_delivered": bool(video_files),
    }
    ready = all(gates.values())
    report = {
        "project": "Jazz Soul Beat",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "READY_FOR_HUMAN_REVIEW" if ready else "BLOCKED_INCOMPLETE_INPUTS",
        "publication": "NOT_AUTHORIZED - no upload or publication performed",
        "summary": {
            "files_received": len(inventory),
            "audio_files": len(audio_files),
            "image_files": len(image_files),
            "video_files": len(video_files),
            "catalog_rows": len(approved_rows),
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
        f"Files received: {len(inventory)} | audio: {len(audio_files)} | images: {len(image_files)} | videos: {len(video_files)}",
        "",
        "## Delivery gates",
    ]
    lines += [f"- [{'x' if passed else ' '}] {name.replace('_', ' ')}" for name, passed in gates.items()]
    lines += [
        "",
        "## Required next actions",
        "- Deliver audio files with per-track license, source URL, attribution and rights evidence.",
        "- Deliver approved original visual scenes for the selected category.",
        "- Render the full-length video only after the approved audio library covers the requested duration.",
        "- Run final media and creative QA; keep publication blocked until explicit owner approval.",
        "",
        "See delivery_manifest.json for the file inventory and SHA-256 checksums.",
    ]
    (OUT / "DELIVERY_REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "summary": report["summary"], "gates": gates}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
