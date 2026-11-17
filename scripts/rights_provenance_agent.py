#!/usr/bin/env python3
"""Read-only rights and provenance triage for music candidates."""
from __future__ import annotations
from pathlib import Path
import csv
ALLOWED_LICENSES = {"CC0 1.0", "CC BY 1.0", "CC BY 2.0", "CC BY 2.5", "CC BY 3.0", "CC BY 4.0"}
def audit_catalog(path: Path) -> dict:
    """Classify catalog rows; never changes approval or rights state."""
    rows = list(csv.DictReader(path.open(newline="", encoding="utf-8-sig")))
    reviewable, incomplete = [], []
    for row in rows:
        evidence = all((row.get(k) or "").strip() for k in ("title", "source_url"))
        license_name = (row.get("license") or row.get("license_name") or "").strip()
        (reviewable if evidence and license_name in ALLOWED_LICENSES else incomplete).append(row)
    return {"status": "REVIEW_ONLY", "rows": len(rows), "reviewable": len(reviewable),
            "incomplete": len(incomplete), "rights_verified": False, "approval_mutated": False}
def contract() -> dict:
    return {"id": "rights_provenance_agent", "mode": "read_only",
            "never_auto_approve": True, "never_publish": True}
