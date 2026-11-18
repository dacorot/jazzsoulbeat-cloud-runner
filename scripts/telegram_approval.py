#!/usr/bin/env python3
"""Telegram review adapter for the hash-bound approval ledger.

The adapter only handles creative review decisions. It cannot approve rights,
make a track assembly-eligible, or authorize public publication. A webhook or
bounded polling job can call ``apply-update`` with Telegram's JSON update.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import urllib.parse
import urllib.request
from pathlib import Path

try:
    from scripts.approval_gate import load, record_decision, record_private_upload, record_public_schedule, save, sha256
except ModuleNotFoundError as exc:  # direct execution: python scripts/telegram_approval.py
    if exc.name not in {"scripts", "scripts.approval_gate"}:
        raise
    from approval_gate import load, record_decision, record_private_upload, record_public_schedule, save, sha256

PREFIX = "jsb1"
CALLBACK_RE = re.compile(r"^jsb1:([A-Za-z0-9_-]{8,64}):(approve|reject|private|public)$")


def callback_data(request_id: str, decision: str) -> str:
    value = f"{PREFIX}:{request_id}:{decision}"
    if len(value.encode("utf-8")) > 64:
        raise ValueError("Telegram callback_data exceeds 64 bytes")
    return value


def parse_callback(value: str) -> tuple[str, str]:
    match = CALLBACK_RE.fullmatch(value or "")
    if not match:
        raise ValueError("invalid_callback_data")
    return match.group(1), match.group(2)


def _api_url(token: str, method: str) -> str:
    return f"https://api.telegram.org/bot{token}/{method}"


def _post_json(token: str, method: str, payload: dict) -> dict:
    request = urllib.request.Request(
        _api_url(token, method),
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        result = json.loads(response.read().decode("utf-8"))
    if not result.get("ok"):
        raise RuntimeError(f"Telegram API rejected {method}")
    return result


def _post_document(token: str, chat_id: str, document: Path, caption: str, markup: dict) -> dict:
    boundary = "----JazzSoulBeatTelegramBoundary"
    parts = []

    def field(name: str, value: str) -> None:
        parts.extend([
            f"--{boundary}\r\nContent-Disposition: form-data; name=\"{name}\"\r\n\r\n".encode(),
            value.encode(), b"\r\n",
        ])

    field("chat_id", chat_id)
    field("caption", caption)
    field("reply_markup", json.dumps(markup, separators=(",", ":")))
    content = document.read_bytes()
    parts.extend([
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"document\"; filename=\"{document.name}\"\r\nContent-Type: application/octet-stream\r\n\r\n".encode(),
        content, b"\r\n", f"--{boundary}--\r\n".encode(),
    ])
    request = urllib.request.Request(
        _api_url(token, "sendDocument"), data=b"".join(parts),
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"}, method="POST",
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        result = json.loads(response.read().decode("utf-8"))
    if not result.get("ok"):
        raise RuntimeError("Telegram API rejected sendDocument")
    return result


def build_review_message(request: dict, request_id: str) -> tuple[str, dict]:
    artifact = Path(request["artifact"])
    status = request.get("status")
    if status == "RIGHTS_VERIFIED_PENDING_PRIVATE_UPLOAD":
        intro = "Rights review is recorded. Only private YouTube upload authorization remains."
    else:
        intro = "Approve only the creative listening decision. Rights and YouTube remain blocked."
    caption = (
        "Jazz Soul Beat — HUMAN LISTENING REVIEW\n"
        f"Request: {request_id}\n"
        f"File: {artifact.name}\n"
        f"SHA-256: {request['artifact_sha256']}\n\n"
        + intro
    )
    markup = {"inline_keyboard": []}
    if status == "PENDING_HUMAN_REVIEW":
        markup["inline_keyboard"].append([
            {"text": "Approve creative review", "callback_data": callback_data(request_id, "approve")},
            {"text": "Reject", "callback_data": callback_data(request_id, "reject")},
        ])
    if (status == "RIGHTS_VERIFIED_PENDING_PRIVATE_UPLOAD"
            and request.get("artifact_kind") == "video"
            and request.get("creative_approval") is True
            and request.get("rights_verified") is True
            and request.get("eligible_for_video_assembly") is True):
        markup["inline_keyboard"].append([
            {"text": "Authorize PRIVATE YouTube upload", "callback_data": callback_data(request_id, "private")},
            {"text": "Schedule PUBLIC publication", "callback_data": callback_data(request_id, "public")},
        ])
    return caption, markup


def apply_update(update: dict, ledger_path: Path, reviewer_id: str) -> dict:
    callback = update.get("callback_query") or {}
    telegram_user = str((callback.get("from") or {}).get("id", ""))
    if not reviewer_id or telegram_user != str(reviewer_id):
        return {"status": "BLOCKED", "reason": "telegram_identity_not_authorized"}
    request_id, decision = parse_callback(str(callback.get("data", "")))
    ledger = load(ledger_path)
    request = ledger["requests"].get(request_id)
    if not request:
        return {"status": "BLOCKED", "reason": "request_not_found", "request_id": request_id}
    if decision == "private":
        ok, reason, result = record_private_upload(
            ledger, request_id, Path(request["artifact"]), telegram_user
        )
    elif decision == "public":
        from scripts.analytics_timing_agent import next_publication_at
        ok, reason, result = record_public_schedule(
            ledger, request_id, Path(request["artifact"]), telegram_user,
            next_publication_at(),
        )
    else:
        ok, reason, result = record_decision(
            ledger, request_id, Path(request["artifact"]), telegram_user, decision
        )
    if not ok:
        return {"status": "BLOCKED", "reason": reason, "request_id": request_id}
    save(ledger_path, ledger)
    return result


def notify(args: argparse.Namespace) -> int:
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = os.environ.get("JAZZ_SOUL_BEAT_TELEGRAM_CHAT_ID", "").strip()
    if not token or not chat_id:
        print(json.dumps({"status": "BLOCKED", "reason": "telegram_credentials_missing"}, indent=2))
        return 2
    ledger = load(args.ledger)
    request = ledger["requests"].get(args.request_id)
    if not request or request.get("status") not in {
        "PENDING_HUMAN_REVIEW", "RIGHTS_VERIFIED_PENDING_PRIVATE_UPLOAD"
    }:
        print(json.dumps({"status": "BLOCKED", "reason": "request_not_pending"}, indent=2))
        return 2
    artifact = Path(request["artifact"])
    if not artifact.is_file() or sha256(artifact) != request["artifact_sha256"]:
        print(json.dumps({"status": "BLOCKED", "reason": "artifact_hash_changed"}, indent=2))
        return 2
    caption, markup = build_review_message(request, args.request_id)
    _post_document(token, chat_id, artifact, caption, markup)
    request.setdefault("events", []).append({"type": "telegram_review_notified", "at_utc": "runtime"})
    save(args.ledger, ledger)
    print(json.dumps({"status": "NOTIFIED", "request_id": args.request_id}, indent=2))
    return 0


def poll_once(args: argparse.Namespace) -> int:
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    reviewer_id = os.environ.get("JAZZ_SOUL_BEAT_TELEGRAM_REVIEWER_ID", "").strip()
    if not token or not reviewer_id:
        print(json.dumps({"status": "NOOP", "reason": "telegram_credentials_missing"}, indent=2))
        return 0
    offset = int(args.offset_file.read_text(encoding="utf-8").strip()) if args.offset_file.exists() else 0
    result = _post_json(token, "getUpdates", {"offset": offset, "timeout": 0, "allowed_updates": ["callback_query"]})
    updates = result.get("result", [])
    processed = 0
    for update in updates:
        callback = update.get("callback_query") or {}
        if callback:
            decision = apply_update(update, args.ledger, reviewer_id)
            print(json.dumps({"update_id": update.get("update_id"), **decision}, ensure_ascii=False))
            callback_id = callback.get("id")
            if callback_id:
                _post_json(token, "answerCallbackQuery", {"callback_query_id": callback_id,
                                                            "text": decision.get("status", "BLOCKED")})
            processed += 1
        offset = max(offset, int(update.get("update_id", -1)) + 1)
    args.offset_file.parent.mkdir(parents=True, exist_ok=True)
    args.offset_file.write_text(str(offset) + "\n", encoding="utf-8")
    print(json.dumps({"status": "POLL_COMPLETE", "updates": len(updates), "processed": processed,
                      "next_offset": offset}, indent=2))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    send = sub.add_parser("notify")
    send.add_argument("--ledger", type=Path, required=True)
    send.add_argument("--request-id", required=True)
    send.set_defaults(func=notify)
    apply = sub.add_parser("apply-update")
    apply.add_argument("--ledger", type=Path, required=True)
    apply.add_argument("--update-json", type=Path, required=True)
    apply.add_argument("--reviewer-id", default=os.environ.get("JAZZ_SOUL_BEAT_TELEGRAM_REVIEWER_ID", ""))
    apply.set_defaults(func=lambda args: _apply_cli(args))
    poll = sub.add_parser("poll-once")
    poll.add_argument("--ledger", type=Path, required=True)
    poll.add_argument("--offset-file", type=Path, required=True)
    poll.set_defaults(func=poll_once)
    args = parser.parse_args()
    return args.func(args)


def _apply_cli(args: argparse.Namespace) -> int:
    result = apply_update(json.loads(args.update_json.read_text(encoding="utf-8")), args.ledger, args.reviewer_id)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("status") != "BLOCKED" else 2


if __name__ == "__main__":
    raise SystemExit(main())
