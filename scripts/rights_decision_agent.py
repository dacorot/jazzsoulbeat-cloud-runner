"""Deterministic rights decision gate: accept complete evidence, reject ambiguity."""
from __future__ import annotations

ALLOWED_LICENSES = {"CC0 1.0", "CC BY 1.0", "CC BY 2.0", "CC BY 2.5", "CC BY 3.0", "CC BY 4.0"}
REQUIRED = ("title", "artist", "source_url", "license_name", "license_evidence_url",
            "creator_authority", "composition_rights", "performance_rights",
            "recording_rights", "commercial_use", "attribution")


def contract() -> dict:
    return {"id": "rights_decision_agent", "pdca": True,
            "auto_accept_only_complete_evidence": True,
            "auto_reject_ambiguous": True, "never_publish": True}


def decide(candidate: dict) -> dict:
    missing = [field for field in REQUIRED if not str(candidate.get(field, "")).strip()]
    license_name = str(candidate.get("license_name", "")).strip()
    if license_name not in ALLOWED_LICENSES:
        missing.append("recognized_commercial_license")
    if missing:
        return {"decision": "REJECTED_INCOMPLETE_RIGHTS", "rights_verified": False,
                "eligible_for_video_assembly": False, "missing_evidence": sorted(set(missing))}
    return {"decision": "ELIGIBLE_FOR_LIBRARY", "rights_verified": True,
            "eligible_for_video_assembly": True, "missing_evidence": []}
