from scripts.copyright_quarantine_agent import build_views


def test_changed_rights_are_quarantined_without_deletion():
    result = build_views({
        "checked_at": "2026-11-17T00:00:00+00:00",
        "records": [
            {"source_url": "https://example.test/changed", "decision": "REMOVE_FROM_ACTIVE_CATALOG_PENDING_CONFIRMATION"},
            {"source_url": "https://example.test/ok", "decision": "KEEP_PENDING_NEXT_WEEKLY_CHECK"},
        ],
    })
    assert result["counts"] == {"quarantined": 1, "active_pending_review": 1}
    assert result["automatic_deletion"] is False
    assert result["automatic_rights_approval"] is False
