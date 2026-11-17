#!/usr/bin/env python3
"""Compare music candidates with the existing catalog before any download."""
from __future__ import annotations
import argparse, csv, hashlib, json
from pathlib import Path

def normalize(value: str) -> str:
    return " ".join(str(value or "").casefold().replace("_", " ").split())

def fingerprint(row: dict) -> dict:
    raw_duration = str(row.get("duration_seconds") or "").strip()
    return {"sha256": str(row.get("sha256") or row.get("audio_sha256") or "").strip().lower(),
            "source_url": normalize(row.get("source_url") or row.get("download_url")),
            "title_creator": (normalize(row.get("title")), normalize(row.get("creator") or row.get("artist"))),
            "duration": round(float(raw_duration), 1) if raw_duration else None}

def load_rows(paths: list[Path]) -> list[dict]:
    rows = []
    for path in paths:
        if path.is_file() and path.suffix.lower() == ".csv":
            with path.open(newline="", encoding="utf-8-sig") as handle:
                rows.extend(csv.DictReader(handle))
        elif path.is_file() and path.suffix.lower() == ".json":
            value = json.loads(path.read_text(encoding="utf-8"))
            rows.extend(value if isinstance(value, list) else value.get("candidates", []))
    return rows

def compare(existing: list[dict], candidates: list[dict]) -> dict:
    known = [fingerprint(row) for row in existing]
    unique, duplicates = [], []
    for candidate in candidates:
        current = fingerprint(candidate)
        matches = []
        for index, item in enumerate(known):
            same_hash = current["sha256"] and current["sha256"] == item["sha256"]
            same_source = current["source_url"] and current["source_url"] == item["source_url"]
            same_title = current["title_creator"] == item["title_creator"] and current["title_creator"] != ("", "")
            same_duration = current["duration"] is not None and item["duration"] is not None and abs(current["duration"] - item["duration"]) <= 1.0
            if same_hash or same_source or (same_title and same_duration):
                matches.append(index)
        if matches:
            duplicates.append({"candidate": candidate, "matched_existing_indexes": matches})
        else:
            unique.append(candidate); known.append(current)
    return {"status": "DEDUPLICATED", "existing_count": len(existing),
            "candidate_count": len(candidates), "unique_count": len(unique),
            "duplicate_count": len(duplicates), "unique": unique, "duplicates": duplicates,
            "download_allowed": True, "approval_mutated": False, "rights_verified": False}

def audio_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""): digest.update(chunk)
    return digest.hexdigest()

def contract() -> dict:
    return {"id": "music_dedup_agent", "compare_before_download": True,
            "dedup_keys": ["sha256", "source_url", "title_creator_duration"],
            "never_auto_approve": True, "never_publish": True}

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--existing", nargs="*", type=Path, default=[])
    parser.add_argument("--candidates", nargs="*", type=Path, default=[])
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = compare(load_rows(args.existing), load_rows(args.candidates))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: result[k] for k in ("status", "existing_count", "candidate_count", "unique_count", "duplicate_count")}, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
