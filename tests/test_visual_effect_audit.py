from pathlib import Path

from scripts.visual_effect_audit import audit


def test_effects_are_required_and_verified(tmp_path: Path):
    video = tmp_path / "video.mp4"
    video.write_bytes(b"video")
    provenance = {"camera": "locked", "video_sha256": "hash", "effect_manifest": {"effects": ["localized_coffee_steam"], "mask_required": True}}
    report = {"execution_status": "RENDERED", "video_sha256": "hash"}
    result = audit(video, provenance, report)
    assert result["status"] == "PASS"


def test_empty_effect_manifest_fails(tmp_path: Path):
    video = tmp_path / "video.mp4"
    video.write_bytes(b"video")
    result = audit(video, {"camera": "locked", "video_sha256": "hash", "effect_manifest": {"effects": [], "mask_required": True}}, {"execution_status": "RENDERED", "video_sha256": "hash"})
    assert result["status"] == "FAIL"
    assert "no_defined_effects" in result["failures"]
