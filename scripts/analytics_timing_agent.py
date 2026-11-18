"""PDCA timing and reach recommendations from YouTube metrics."""
from __future__ import annotations

DEFAULT_SLOTS = ("Tuesday 14:00", "Friday 12:00", "Sunday 10:00")


def contract() -> dict:
    return {"id": "analytics_timing_agent", "pdca": True,
            "timezone": "America/Bogota", "never_publish": True,
            "uses_channel_metrics": True}


def recommend(metrics: list[dict] | None = None) -> dict:
    rows = metrics or []
    if not rows:
        return {"slots": list(DEFAULT_SLOTS), "basis": "initial_test_matrix",
                "next_measurement": ["impressions", "CTR", "retention", "audience_online"],
                "pdca": "Collect at least 3 comparable releases before changing slots."}
    ranked = sorted(rows, key=lambda row: (float(row.get("ctr", 0)),
                                           float(row.get("retention", 0))), reverse=True)
    slots = [row.get("slot") for row in ranked if row.get("slot")]
    return {"slots": slots[:3] or list(DEFAULT_SLOTS), "basis": "channel_metrics",
            "sample_size": len(rows), "pdca": "Retest the lowest-performing slot next cycle."}
