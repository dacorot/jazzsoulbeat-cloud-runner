#!/usr/bin/env python3
"""Send one Telegram alert per distinct pipeline-health fingerprint."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import urllib.parse
import urllib.request
from pathlib import Path


def alert(report_path: Path, state_path: Path) -> str:
    report = json.loads(report_path.read_text(encoding="utf-8"))
    if report.get("status") != "ALERT":
        return "NO_ALERT_HEALTHY"
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = os.environ.get("JAZZ_SOUL_BEAT_TELEGRAM_CHAT_ID", "").strip()
    if not token or not chat_id:
        return "ALERT_NOT_SENT_MISSING_TELEGRAM_CONFIG"
    fingerprint = hashlib.sha256(json.dumps(report.get("checkpoints", []), sort_keys=True).encode()).hexdigest()
    previous = {}
    if state_path.is_file():
        previous = json.loads(state_path.read_text(encoding="utf-8"))
    if previous.get("fingerprint") == fingerprint:
        return "ALERT_ALREADY_SENT"
    details = "; ".join(
        f"{item.get('video_id', item.get('path'))}: {item.get('status')}"
        for item in report.get("checkpoints", []) if item.get("status") != "HEALTHY"
    ) or "Pipeline health alert"
    body = urllib.parse.urlencode({"chat_id": chat_id, "text": f"Jazz Soul Beat alert: {details}"}).encode()
    request = urllib.request.Request(
        f"https://api.telegram.org/bot{token}/sendMessage", data=body, method="POST",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        if response.status != 200:
            raise RuntimeError("telegram_alert_http_error")
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(json.dumps({"fingerprint": fingerprint, "sent_at": report.get("checked_at")}) + "\n", encoding="utf-8")
    return "ALERT_SENT"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--state", type=Path, required=True)
    args = parser.parse_args()
    print(alert(args.report, args.state))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
