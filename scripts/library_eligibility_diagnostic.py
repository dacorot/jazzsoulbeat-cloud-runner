#!/usr/bin/env python3
"""Read-only eligibility report for restored Jazz Soul Beat library state."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sqlite3
from pathlib import Path
from urllib.parse import quote


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def reasons(row: dict, agent_root: Path, *, requested_genre: str = "jazz") -> list[str]:
    result = []
    if int(row.get("approved") or 0) != 1:
        result.append("approved_false")
    if int(row.get("rights_verified") or 0) != 1:
        result.append("rights_verified_false")
    try:
        if float(row.get("duration") or 0) <= 180:
            result.append("duration_not_over_180_seconds")
    except (TypeError, ValueError):
        result.append("duration_missing_or_invalid")
    if row.get("collection") != "evergreen":
        result.append("not_evergreen")
    if str(row.get("season") or ""):
        result.append("season_not_empty")
    if not str(row.get("genre") or "").strip():
        result.append("genre_missing")
    if not str(row.get("mood") or "").strip():
        result.append("mood_missing")
    if not str(row.get("instruments") or "").strip() and not str(row.get("metadata_source") or "").startswith("Official Ketsa"):
        result.append("instruments_missing")
    genre = str(row.get("genre") or "").casefold()
    if requested_genre and requested_genre not in genre:
        result.append("requested_genre_not_present")
    energy = str(row.get("energy") or "").casefold()
    fields = " ".join(str(row.get(key) or "") for key in ("title", "genre", "mood", "instruments", "feel")).casefold()
    disallowed = ("funk", "funky", "groove", "grooving", "hip hop", "hip-hop", "boom bap", "trip hop", "trip-hop", "blues", "bossa", "disco", "house", "edm", "trap", "reggaeton", "rock", "country", "shuffle", "upbeat", "party", "energetic", "lively", "fast", "celebratory")
    if any(term in fields for term in disallowed):
        result.append("channel_disallowed_term")
    if not any(term in genre for term in ("jazz", "soul", "lofi", "lo-fi")):
        result.append("channel_genre_mismatch")
    if not any(term in energy for term in ("low", "soft", "quiet", "mellow", "relaxed")):
        result.append("channel_energy_mismatch")
    path_value = str(row.get("file") or "")
    path = agent_root / path_value
    if not path.is_file():
        result.append("artifact_missing")
    elif path.is_symlink():
        result.append("artifact_symlink")
    expected = str(row.get("artifact_sha256") or row.get("sha256") or "")
    if expected and path.is_file() and sha256(path) != expected:
        result.append("artifact_sha256_mismatch")
    if not expected:
        result.append("artifact_sha256_missing")
    return sorted(set(result))


def track_record(row: dict, agent_root: Path) -> dict:
    path_value = str(row.get("file") or "")
    path = agent_root / path_value
    expected = str(row.get("artifact_sha256") or row.get("sha256") or "")
    actual = sha256(path) if path.is_file() and not path.is_symlink() else ""
    eligibility_reasons = reasons(row, agent_root)
    return {
        "track_id": row.get("track_id") or row.get("id") or path_value,
        "name": row.get("title") or row.get("name") or "",
        "path": path_value,
        "resolved_path": str(path),
        "sha256_calculated": actual,
        "sha256_registered": expected,
        "sha256_match": bool(actual and expected and actual == expected),
        "duration_seconds": row.get("duration") or 0,
        "genre": row.get("genre") or "",
        "subgenre": row.get("subgenre") or "",
        "source": row.get("source_url") or row.get("metadata_source") or "",
        "rights_holder": row.get("rights_holder") or row.get("artist") or "",
        "license": row.get("license") or "",
        "provenance_evidence": row.get("license_url") or row.get("source_url") or "",
        "rights_verified": bool(int(row.get("rights_verified") or 0)),
        "human_approval": bool(int(row.get("approved") or 0)) and bool(int(row.get("creative_approval") or 0)),
        "editorial_status": row.get("review_status") or row.get("status") or "",
        "production_eligible": not eligibility_reasons,
        "eligibility_reasons": eligibility_reasons,
    }


def open_read_only_database(db_path: Path) -> sqlite3.Connection:
    """Open SQLite without write capability, even if the caller is compromised."""
    resolved = db_path.resolve(strict=True)
    uri = f"file:{quote(str(resolved), safe='/')}?mode=ro"
    connection = sqlite3.connect(uri, uri=True)
    connection.execute("PRAGMA query_only=ON")
    setting = connection.execute("PRAGMA query_only").fetchone()
    if not setting or setting[0] != 1:
        connection.close()
        raise RuntimeError("SQLite query_only could not be enabled")
    return connection


def load_tracks(db_path: Path) -> list[dict]:
    connection = open_read_only_database(db_path)
    connection.row_factory = sqlite3.Row
    try:
        rows = [dict(row) for row in connection.execute("SELECT * FROM tracks")]
        return sorted(rows, key=lambda row: str(row.get("id") or row.get("track_id") or row.get("file") or ""))
    finally:
        connection.close()


def recent_candidates(agent_root: Path) -> list[dict]:
    rows = []
    root = agent_root / "output" / "original-music"
    reports = {p.parent: p for p in root.glob("batch-*/**/production_report.json")}
    candidate_dirs = sorted({p.parent for p in root.glob("batch-*/**/candidate-*/*") if p.is_file()})
    for candidate_dir in candidate_dirs:
        report = reports.get(candidate_dir)
        data = {}
        if report:
            try:
                data = json.loads(report.read_text(encoding="utf-8"))
            except (OSError, ValueError, TypeError):
                data = {}
        audio = next((path for path in candidate_dir.iterdir() if path.suffix.lower() in {".wav", ".mp3", ".flac", ".m4a", ".ogg"}), None)
        if audio is None:
            continue
        rows.append({
            "report": str(report.relative_to(agent_root)) if report else "",
            "artifact": str(audio.relative_to(agent_root)),
            "artifact_sha256": sha256(audio),
            "genre": data.get("genre", ""),
            "duration_seconds": data.get("duration_actual_seconds", 0),
            "rights_verified": data.get("rights_verified", False),
            "creative_approval": data.get("creative_approval", False),
            "eligible_for_video_assembly": data.get("eligible_for_video_assembly", False),
            "model_provenance_url": data.get("model_card_url", ""),
            "model_license": data.get("model_license", ""),
            "status": data.get("status", ""),
            "pending_review": True,
            "eligibility_reasons": ["rights_verified_false", "human_approval_pending", "not_promoted"],
        })
    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    tracks = load_tracks(args.agent_root / "data" / "agent.db")
    approved = [row for row in tracks if int(row.get("approved") or 0) == 1 and int(row.get("rights_verified") or 0) == 1]
    records = [track_record(row, args.agent_root) for row in tracks]
    report = {
        "mode": "READ_ONLY_LIBRARY_DIAGNOSTIC",
        "requested_collection": "evergreen",
        "requested_genre": "jazz",
        "approved_rights_verified_count": len(approved),
        "approved_rights_verified_seconds": round(sum(float(row.get("duration") or 0) for row in approved), 2),
        "tracks": records,
        "recent_original_candidates": recent_candidates(args.agent_root),
        "publication": "DISABLED",
        "rights_mutation": "NONE",
        "library_mutation": "NONE",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    csv_path = args.output.with_suffix(".csv")
    fields = list(records[0].keys()) if records else ["track_id", "name", "production_eligible", "eligibility_reasons"]
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for record in records:
            normalized = dict(record)
            normalized["eligibility_reasons"] = ";".join(record["eligibility_reasons"])
            writer.writerow(normalized)
    print(json.dumps({key: report[key] for key in ("approved_rights_verified_count", "approved_rights_verified_seconds", "publication", "library_mutation")}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
