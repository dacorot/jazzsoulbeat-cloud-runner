import json

from scripts.telegram_alert_agent import alert


def test_healthy_report_sends_nothing(tmp_path):
    report = tmp_path / "report.json"
    report.write_text(json.dumps({"status": "HEALTHY_IDLE", "checkpoints": []}), encoding="utf-8")
    assert alert(report, tmp_path / "state.json") == "NO_ALERT_HEALTHY"
