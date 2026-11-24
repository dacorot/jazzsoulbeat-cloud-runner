import hashlib
import json
from pathlib import Path

from scripts.autonomous_learning import default_model
from scripts.autonomous_music_gate import evaluate


def test_clean_soft_jazz_is_eligible(tmp_path: Path):
    audio = tmp_path / "soft-jazz.mp3"
    audio.write_bytes(b"verified-audio")
    policy = json.loads(Path("config/autonomous_learning.json").read_text(encoding="utf-8"))
    candidate = {
        "title": "Soft Jazz Rain",
        "artist": "Ketsa",
        "genres": ["jazz", "soft jazz"],
        "source_url": "https://ketsa.uk/soft-jazz-rain/",
        "license_name": "CC BY 4.0",
        "artifact": str(audio),
        "artifact_sha256": hashlib.sha256(audio.read_bytes()).hexdigest(),
        "duration_seconds": 240,
        "technical_ok": True,
        "instrumental": True,
    }
    result, summary = evaluate(candidate, policy, default_model(policy["feature_order"]))
    assert summary["decision"] == "approved"
    assert result["eligible_for_video_assembly"] is True


def test_funky_candidate_is_quarantined(tmp_path: Path):
    audio = tmp_path / "funk.mp3"
    audio.write_bytes(b"verified-audio")
    policy = json.loads(Path("config/autonomous_learning.json").read_text(encoding="utf-8"))
    candidate = {
        "title": "Funky Groove Night",
        "genres": ["jazz", "funky groove"],
        "source_url": "https://ketsa.uk/funky-groove-night/",
        "license_name": "CC BY 4.0",
        "artifact": str(audio),
        "artifact_sha256": hashlib.sha256(audio.read_bytes()).hexdigest(),
        "duration_seconds": 240,
        "technical_ok": True,
        "instrumental": True,
    }
    result, summary = evaluate(candidate, policy, default_model(policy["feature_order"]))
    assert summary["decision"] == "quarantined"
    assert "forbidden_term" in result["quarantine_reasons"]
