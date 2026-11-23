#!/usr/bin/env python3
"""Notify Telegram without uploading oversized delivery MP4 files."""
from __future__ import annotations

import argparse
import json
import os
import urllib.request
from pathlib import Path

try:
    from scripts.telegram_approval import callback_data
except ModuleNotFoundError:
    from telegram_approval import callback_data


def send(token: str, method: str, payload: dict) -> dict:
    request = urllib.request.Request(
        f"https://api.telegram.org/bot{token}/{method}",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(request, timeout=30) as response:
        result = json.loads(response.read().decode())
    if not result.get("ok"):
        raise RuntimeError(f"telegram_api_rejected:{method}")
    return result


def notify(ledger_path: Path, request_id: str) -> None:
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = os.environ.get("JAZZ_SOUL_BEAT_TELEGRAM_CHAT_ID", "").strip()
    if not token or not chat_id:
        raise RuntimeError("telegram_credentials_missing")
    ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
    request = ledger.get("requests", {}).get(request_id)
    if not request or request.get("status") != "PENDING_HUMAN_REVIEW":
        raise RuntimeError("request_not_pending")
    markup = {"inline_keyboard": [[
        {"text": "Approve video", "callback_data": callback_data(request_id, "approve")},
        {"text": "Reject", "callback_data": callback_data(request_id, "reject")},
    ]]}
    caption = ("Jazz Soul Beat — VIDEO REVIEW\n"
               f"Video: {request.get('delivery_video', Path(request['artifact']).name)}\n"
               f"Duration: {request.get('duration_seconds')} seconds\n"
               f"SHA-256: {request['artifact_sha256']}\n\n"
               "Open the private delivery from Drive/local review storage. "
               "This decision is creative only; rights and YouTube publication remain blocked.")
    send(token, "sendMessage", {"chat_id": chat_id, "text": caption,
                                 "reply_markup": markup, "disable_web_page_preview": True})


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ledger", type=Path, required=True)
    parser.add_argument("--request-id", required=True)
    args = parser.parse_args()
    notify(args.ledger.resolve(), args.request_id)
    print(json.dumps({"status": "NOTIFIED", "request_id": args.request_id}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
