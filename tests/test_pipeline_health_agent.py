import json
from pathlib import Path

from scripts.pipeline_health_agent import audit


def test_health_is_idle_without_checkpoints(tmp_path):
    report = audit(tmp_path / "output", tmp_path / "report.json")
    assert report["status"] == "HEALTHY_IDLE"
    assert report["checkpoint_count"] == 0


def test_invalid_checkpoint_is_alert(tmp_path):
    root = tmp_path / "output" / "orchestrator"
    root.mkdir(parents=True)
    (root / "video-02.checkpoint.json").write_text(json.dumps({"schema_version": 1, "stage": "BAD"}), encoding="utf-8")
    report = audit(tmp_path / "output", tmp_path / "report.json")
    assert report["status"] == "ALERT"
    assert report["checkpoints"][0]["status"] == "INVALID_CHECKPOINT"
