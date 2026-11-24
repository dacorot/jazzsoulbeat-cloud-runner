import json
from pathlib import Path

from scripts.video_release_board import review


def _run(tmp_path: Path, *, transition_status="PASS"):
    for name in ("video.mp4", "mix.mp3", "thumb.jpg", "description.txt", "MUSIC_SOURCE.txt"):
        (tmp_path / name).write_bytes(b"x")
    (tmp_path / "AUDIO_TRANSITION_REPORT.json").write_text(json.dumps({
        "status": transition_status, "failures": [], "track_count": 2,
        "transition_count": 1, "silence_durations_seconds": [], "tracks": [{"sha256": "a"}],
        "learning_features": {"boundary_count": 1},
    }))
    (tmp_path / "VISUAL_SCENE_PROVENANCE.json").write_text(json.dumps({
        "publication": "PRIVATE_REVIEW_ONLY", "camera": "locked", "scene_count": 1,
        "approved_image_sha256": "image",
        "visual_uniqueness": "REQUIRED_AND_HASH_BOUND",
        "reference_perceptual_signature": "0101",
        "playlist": "coffee_time",
        "music_visual_match": "LINKED_TO_PLAYLIST_AND_TRACK_METADATA",
    }))
    (tmp_path / "EFFECT_AUDIT.json").write_text(json.dumps({"status": "PASS", "effects_verified": True, "effects": ["localized_coffee_steam"]}))


def test_all_roles_must_pass(tmp_path):
    _run(tmp_path)
    result = review(tmp_path, 7200)
    assert result["status"] == "APPROVED_PRIVATE"
    assert {item["role"] for item in result["checks"]} == {"supervisor", "coordinator", "audio_director", "visual_director", "metadata_director"}


def test_failure_requests_rework(tmp_path):
    _run(tmp_path, transition_status="FAIL")
    assert review(tmp_path, 7200)["status"] == "REWORK_REQUIRED"
