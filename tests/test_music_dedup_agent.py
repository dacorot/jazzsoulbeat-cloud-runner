from scripts.music_dedup_agent import compare

def test_duplicate_by_source_before_download():
    existing = [{"title": "Rain", "creator": "A", "source_url": "https://example.test/rain", "duration_seconds": "200"}]
    candidate = [{"title": "Rain", "creator": "A", "source_url": "https://example.test/rain", "duration_seconds": "200"}]
    result = compare(existing, candidate)
    assert result["duplicate_count"] == 1
    assert result["unique_count"] == 0
    assert result["download_allowed"] is True
    assert result["rights_verified"] is False

def test_new_candidate_is_compared_against_previous_new_candidate():
    result = compare([], [
        {"title": "Blue Hour", "creator": "A", "source_url": "https://example.test/1", "duration_seconds": "180"},
        {"title": "Blue Hour", "creator": "A", "source_url": "https://example.test/2", "duration_seconds": "180.4"},
    ])
    assert result["duplicate_count"] == 1
    assert result["unique_count"] == 1
