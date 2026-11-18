import json
from pathlib import Path

from scripts import copyright_watch_agent as watcher


def test_classify_license_text_is_conservative():
    assert watcher.classify_license_text("CC BY 4.0 commercial attribution") == "CC_BY_EVIDENCE_PRESENT"
    assert watcher.classify_license_text("All rights reserved") == "RESTRICTIVE_OR_NONCOMMERCIAL"
    assert watcher.classify_license_text("unclear") == "LICENSE_NOT_IDENTIFIED"


def test_audit_records_change_without_deleting_or_approving(tmp_path, monkeypatch):
    root = tmp_path / "tracks"
    root.mkdir()
    (root / "library.csv").write_text(
        "title,source_url,license_name\nSong,https://example.test/song,CC BY 4.0\n",
        encoding="utf-8",
    )
    state = tmp_path / "state.json"
    report = tmp_path / "report.json"
    state.write_text(json.dumps({"sources": {"https://example.test/song": {"evidence_sha256": "old"}}}), encoding="utf-8")
    monkeypatch.setattr(watcher, "fetch_evidence", lambda url: ("new", "CC BY 4.0", 200))
    result = watcher.audit([root], state, report)
    row = result["records"][0]
    assert row["status"] == "SOURCE_CHANGED_REVIEW_REQUIRED"
    assert row["decision"] == "REMOVE_FROM_ACTIVE_CATALOG_PENDING_CONFIRMATION"
    assert report.is_file() and state.is_file()
    assert result["policy"]["automatic_deletion"] is False
    assert result["policy"]["automatic_rights_approval"] is False
