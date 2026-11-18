"""PDCA timing and reach recommendations from YouTube metrics."""
from __future__ import annotations

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

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


def next_publication_at(now: datetime | None = None) -> str:
    """Return the next initial-test slot as a UTC timestamp for YouTube."""
    zone = ZoneInfo("America/Bogota")
    current = (now or datetime.now(zone)).astimezone(zone)
    candidates = []
    for days_ahead in range(0, 8):
        day = current + timedelta(days=days_ahead)
        slot = {1: 14, 4: 12, 6: 10}.get(day.weekday())
        if slot is None:
            continue
        candidate = day.replace(hour=slot, minute=0, second=0, microsecond=0)
        if candidate > current:
            candidates.append(candidate)
    return min(candidates).astimezone(ZoneInfo("UTC")).isoformat().replace("+00:00", "Z")
