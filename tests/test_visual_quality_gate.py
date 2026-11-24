import hashlib
import json

from scripts.visual_quality_gate import inspect


def _provenance(video):
    return {
        "approved_image_sha256": "image-hash",
        "video_sha256": hashlib.sha256(video.read_bytes()).hexdigest(),
        "motion_profile": "approved_plate_coffee_steam",
        "camera": "locked",
        "scene_count": 1,
        "publication": "DISABLED",
    }


def _config():
    return {
        "minimum_resolution": [1920, 1080],
        "allowed_effect_profiles": ["approved_plate_coffee_steam"],
        "required_provenance": ["approved_image_sha256", "video_sha256", "motion_profile", "camera", "scene_count"],
        "hard_rules": {"scene_count": 1, "camera": "locked", "publication": "DISABLED", "no_full_frame_particle_overlay": True, "no_camera_motion": True},
    }


def test_professional_visual_contract_passes(tmp_path):
    video = tmp_path / "video.mp4"
    video.write_bytes(b"render")
    result = inspect(video, _provenance(video), width=2560, height=1440, config=_config())
    assert result["status"] == "PASS"
    assert result["professional_effects"] is True


def test_bad_effect_is_quarantined(tmp_path):
    video = tmp_path / "video.mp4"
    video.write_bytes(b"render")
    provenance = _provenance(video)
    provenance["motion_profile"] = "full_frame_particle_overlay"
    result = inspect(video, provenance, width=2560, height=1440, config=_config())
    assert result["status"] == "FAIL"
    assert "unapproved_effect_profile" in result["failures"]
