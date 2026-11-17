#!/usr/bin/env python3
"""Read-only rights and provenance triage for music candidates.

The agent automates evidence checks and attribution preparation. It never
turns evidence into a legal approval or enables publication.
"""
from __future__ import annotations

from pathlib import Path
import csv
from urllib.parse import urlparse

ALLOWED_LICENSES = {
    "CC0 1.0",
    "CC BY 1.0",
    "CC BY 2.0",
    "CC BY 2.5",
    "CC BY 3.0",
    "CC BY 4.0",
}
COMMERCIAL_LICENSES = {"CC0 1.0", "CC BY 1.0", "CC BY 2.0", "CC BY 2.5", "CC BY 3.0", "CC BY 4.0"}
LICENSE_URLS = {
    "CC BY 4.0": "https://creativecommons.org/licenses/by/4.0/",
    "CC0 1.0": "https://creativecommons.org/publicdomain/zero/1.0/",
}


def _https(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme == "https" and bool(parsed.netloc)


def _attribution(row: dict, license_name: str) -> str:
    title = (row.get("title") or "Untitled").strip()
    artist = (row.get("artist") or row.get("creator") or "Unknown creator").strip()
    source = (row.get("source_url") or "").strip()
    license_url = (row.get("license_url") or LICENSE_URLS.get(license_name, "")).strip()
    if license_name.startswith("CC BY"):
        return (
            f"{title} — {artist} ({source})\n"
            f"Licensed under {license_name}: {license_url}"
        )
    return f"{title} — {artist} ({source})\n{license_name}: {license_url}"


def audit_catalog(path: Path) -> dict:
    """Classify evidence without changing approval, rights, or publication state."""
    rows = list(csv.DictReader(path.open(newline="", encoding="utf-8-sig")))
    reviewable, incomplete, compliance_ready = [], [], []
    attribution_manifest = []

    for row in rows:
        title = (row.get("title") or "").strip()
        source_url = (row.get("source_url") or "").strip()
        license_name = (row.get("license") or row.get("license_name") or "").strip()
        license_url = (row.get("license_url") or LICENSE_URLS.get(license_name, "")).strip()
        evidence_ok = bool(title and _https(source_url) and license_name in ALLOWED_LICENSES)
        license_ok = bool(license_url and (_https(license_url) or license_url.startswith("http://")))
        if evidence_ok and license_ok:
            reviewable.append(row)
            if license_name in COMMERCIAL_LICENSES:
                compliance_ready.append(row)
                attribution_manifest.append({
                    "title": title,
                    "artist": (row.get("artist") or row.get("creator") or "").strip(),
                    "license": license_name,
                    "license_url": license_url,
                    "source_url": source_url,
                    "attribution": _attribution(row, license_name),
                    "status": "READY_FOR_HUMAN_CONFIRMATION",
                })
        else:
            incomplete.append(row)

    return {
        "status": "REVIEW_ONLY",
        "rows": len(rows),
        "reviewable": len(reviewable),
        "incomplete": len(incomplete),
        "compliance_ready": len(compliance_ready),
        "needs_human_confirmation": len(compliance_ready),
        "attribution_manifest": attribution_manifest,
        "rights_verified": False,
        "approval_mutated": False,
        "publication": "DISABLED",
    }


def contract() -> dict:
    return {
        "id": "rights_provenance_agent",
        "mode": "read_only",
        "automates": [
            "HTTPS source evidence check",
            "allowlisted commercial license check",
            "per-track attribution generation",
        ],
        "never_auto_approve": True,
        "never_publish": True,
    }
