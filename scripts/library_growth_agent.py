"""Plan and report the next safe actions for growing the approved library.

This agent does not invent approvals. It measures the capacity gap, prioritizes
the discovery lanes that can provide primary evidence, and reports how many
seconds can actually be promoted after the rights decision gate.
"""
from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path


TARGET_SECONDS = 7200.0


@dataclass(frozen=True)
class Lane:
    id: str
    purpose: str
    priority: int
    requires_human_review: bool


LANES = (
    Lane("official_creator_catalogs", "Ketsa and other creator-owned catalogues", 1, True),
    Lane("open_license_primary_pages", "CC0/CC BY sources with primary item pages", 2, True),
    Lane("community_catalogs", "Commons, ccMixter and Openverse leads", 3, True),
    Lane("original_auditions", "Original jazz/soul auditions for listening review", 4, True),
)


def contract() -> dict:
    return {
        "id": "library_growth_agent",
        "pdca": True,
        "target_seconds": TARGET_SECONDS,
        "lanes": [lane.id for lane in LANES],
        "never_auto_approve": True,
        "never_publish": True,
    }


def plan(approved_seconds: float, promoted_seconds: float = 0.0) -> dict:
    approved = max(0.0, float(approved_seconds))
    promoted = max(0.0, float(promoted_seconds))
    total = approved + promoted
    missing = max(0.0, TARGET_SECONDS - total)
    return {
        "agent_id": "library_growth_agent",
        "target_seconds": TARGET_SECONDS,
        "approved_seconds": round(approved, 2),
        "promoted_seconds": round(promoted, 2),
        "available_seconds": round(total, 2),
        "missing_seconds": round(missing, 2),
        "status": "READY_FOR_LONGFORM_ASSEMBLY" if missing == 0 else "GROWTH_REQUIRED",
        "next_lanes": [lane.id for lane in sorted(LANES, key=lambda item: item.priority)],
        "human_review_required": True,
        "publication": "DISABLED",
        "pdca_next_action": "Run discovery, audit primary evidence, decide rights, then promote only eligible hashes.",
    }


def summarize_promotion(report: dict) -> dict:
    approved = report.get("approved", [])
    seconds = sum(float(row.get("duration_seconds", 0) or 0) for row in approved)
    return {
        "promoted_tracks": len(approved),
        "promoted_seconds": round(seconds, 2),
        "rejected_tracks": len(report.get("rejected", [])),
        "publication": "DISABLED",
    }


def source_heartbeat(registry_path: Path, outcomes: dict[str, str]) -> dict:
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    sources = registry.get("sources", [])
    known = {str(row.get("id")) for row in sources}
    unknown = sorted(set(outcomes) - known)
    succeeded = sorted(source_id for source_id in known if outcomes.get(source_id) == "success")
    failed = sorted(source_id for source_id in known if outcomes.get(source_id) == "failure")
    missing = sorted(source_id for source_id in known if source_id not in outcomes)
    if not succeeded:
        raise RuntimeError("all_library_sources_failed")
    return {
        "agent_id": "library_growth_agent",
        "sources_configured": len(sources),
        "sources_succeeded": succeeded,
        "sources_failed": failed,
        "sources_missing_heartbeat": missing,
        "unknown_outcomes": unknown,
        "heartbeat": "ACTIVE" if not missing else "DEGRADED",
        "publication": "DISABLED",
        "pdca_next_action": "Audit successful source outputs and send eligible hashes to the rights gate.",
    }
