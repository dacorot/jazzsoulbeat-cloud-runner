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
PUBLICATION_REQUIREMENTS = {\n    "CC BY": {\n        "credit_creator": True,\n        "credit_title": True,\n        "source_link": True,\n        "license_link": True,\n        "modifications_notice": True,\n        "no_endorsement_claim": True,\n        "if_attribution_is_impossible": "obtain a separate standard license",\n    },\n    "CC0": {\n        "credit_creator": False,\n        "credit_title": False,\n        "source_link": False,\n        "license_link": False,\n        "modifications_notice": False,\n        "no_endorsement_claim": True,\n        "if_attribution_is_impossible": "no attribution condition from CC0",\n    },\n}\nLICENSE_URLS = {
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



if __name__ == "__main__":
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Audit rights evidence without approving publication.")
    parser.add_argument("--csv", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    report = audit_catalog(args.csv)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": report["status"],
        "rows": report["rows"],
        "compliance_ready": report["compliance_ready"],
        "needs_human_confirmation": report["needs_human_confirmation"],
        "rights_verified": report["rights_verified"],
        "publication": report["publication"],
    }, ensure_ascii=False))
