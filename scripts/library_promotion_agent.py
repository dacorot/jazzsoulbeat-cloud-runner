"""Promote only hash-bound, rights-eligible candidates into the private library."""
from __future__ import annotations

import json
from pathlib import Path


REQUIRED = ("title", "artist", "artifact", "artifact_sha256", "duration_seconds",
            "license_name", "source_url", "attribution")


def contract() -> dict:
    return {"id": "library_promotion_agent", "pdca": True,
            "requires_rights_decision": True, "deduplicates_by_hash": True,
            "private_library_only": True, "never_publish": True}


def promote(candidates: list[dict], existing: list[dict] | None = None) -> dict:
    existing = existing or []
    used_hashes = {str(row.get("artifact_sha256")) for row in existing if row.get("artifact_sha256")}
    used_sources = {str(row.get("source_url")) for row in existing if row.get("source_url")}
    approved, rejected = [], []
    for candidate in candidates:
        missing = [field for field in REQUIRED if not str(candidate.get(field, "")).strip()]
        if candidate.get("decision") != "ELIGIBLE_FOR_LIBRARY" or candidate.get("rights_verified") is not True:
            missing.append("rights_decision_not_eligible")
        if candidate.get("eligible_for_video_assembly") is not True:
            missing.append("assembly_eligibility_missing")
        digest = str(candidate.get("artifact_sha256", ""))
        source = str(candidate.get("source_url", ""))
        if digest in used_hashes:
            missing.append("duplicate_artifact_hash")
        if source and source in used_sources:
            missing.append("duplicate_source_url")
        if missing:
            rejected.append({"title": candidate.get("title", ""),
                             "reasons": sorted(set(missing))})
            continue
        row = {field: candidate[field] for field in REQUIRED}
        row.update({"rights_verified": True, "eligible_for_video_assembly": True,
                    "publication": "DISABLED"})
        approved.append(row)
        used_hashes.add(digest)
        used_sources.add(source)
    return {"agent_id": "library_promotion_agent", "approved": approved,
            "rejected": rejected, "approved_seconds": round(sum(float(x["duration_seconds"]) for x in approved), 2),
            "publication": "DISABLED", "pdca_next_action": "Re-run after the next rights-audit batch."}


def promote_file(candidates_path: Path, library_path: Path, report_path: Path) -> dict:
    candidates = json.loads(candidates_path.read_text(encoding="utf-8"))
    existing = json.loads(library_path.read_text(encoding="utf-8")) if library_path.exists() else []
    result = promote(candidates, existing)
    merged = existing + result["approved"]
    library_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    library_path.write_text(json.dumps(merged, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result
