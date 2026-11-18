#!/usr/bin/env python3
"""Hash-bound human review ledger for Jazz Soul Beat.

This is the policy core for Telegram or another review UI.  It deliberately
does not grant rights, upload to YouTube, or infer approval from technical QA.
The ledger is append-only in spirit: each request has one terminal decision,
and the current artifact hash must match the reviewed hash exactly.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import secrets
import sys
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

try:
    import fcntl
except ImportError:  # pragma: no cover - Windows uses the workflow's serialized runner.
    fcntl = None


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load(path: Path) -> dict:
    if not path.exists():
        return {"schema_version": 1, "requests": {}}
    value = json.loads(path.read_text(encoding="utf-8"))
    if value.get("schema_version") != 1 or not isinstance(value.get("requests"), dict):
        raise ValueError("Unsupported approval ledger schema")
    return value


def save(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


@contextmanager
def ledger_lock(path: Path):
    """Serialize load-modify-save operations across local and CI workers."""
    if fcntl is None:
        yield
        return
    lock_path = path.with_suffix(path.suffix + ".lock")
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    with lock_path.open("a+", encoding="utf-8") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def fail(message: str) -> int:
    print(json.dumps({"status": "BLOCKED", "reason": message}, indent=2))
    return 2


def create(args: argparse.Namespace) -> int:
    artifact = args.artifact.resolve()
    if not artifact.is_file():
        return fail("artifact_missing")
    with ledger_lock(args.ledger):
        ledger = load(args.ledger)
        # The stable prefix prevents a URL-safe token beginning with '-' from
        # being parsed as a command-line option by approval/Telegram tooling.
        request_id = "r_" + secrets.token_urlsafe(18)
        artifact_hash = sha256(artifact)
        ledger["requests"][request_id] = {
            "request_id": request_id,
            "created_at_utc": utc_now(),
            "artifact": str(artifact),
            "artifact_sha256": artifact_hash,
            "artifact_kind": args.kind,
            "status": "PENDING_HUMAN_REVIEW",
            "creative_approval": False,
            "rights_verified": False,
            "eligible_for_video_assembly": False,
            "youtube_upload": "NOT_AUTHORIZED",
            "events": [{"type": "request_created", "at_utc": utc_now()}],
        }
        save(args.ledger, ledger)
    print(json.dumps({"status": "PENDING_HUMAN_REVIEW", "request_id": request_id,
                      "artifact_sha256": artifact_hash, "ledger": str(args.ledger)}, indent=2))
    return 0


def record_decision(ledger: dict, request_id: str, artifact_path: Path,
                    reviewer_id: str, decision: str) -> tuple[bool, str, dict]:
    """Record one creative decision after rechecking identity-independent facts."""
    if decision not in {"approve", "reject"}:
        return False, "invalid_decision", {}
    request = ledger["requests"].get(request_id)
    if not request:
        return False, "request_not_found", {}
    if request["status"] != "PENDING_HUMAN_REVIEW":
        return False, "request_already_decided", {}
    artifact = Path(request["artifact"])
    if artifact_path.resolve() != artifact.resolve():
        return False, "artifact_path_mismatch", {}
    if not artifact.is_file():
        return False, "artifact_missing", {}
    current_hash = sha256(artifact)
    if current_hash != request["artifact_sha256"]:
        return False, "artifact_hash_changed", {}
    approved = decision == "approve"
    request["status"] = "CREATIVE_APPROVED_PENDING_RIGHTS" if approved else "REJECTED"
    request["creative_approval"] = approved
    request["rights_verified"] = False
    request["eligible_for_video_assembly"] = False
    request["youtube_upload"] = "NOT_AUTHORIZED"
    request["events"].append({
        "type": "creative_decision", "decision": decision,
        "reviewer_id": reviewer_id, "artifact_sha256": current_hash, "at_utc": utc_now(),
    })
    return True, "ok", {"status": request["status"], "request_id": request_id,
                         "creative_approval": approved, "rights_verified": False,
                         "youtube_upload": "NOT_AUTHORIZED"}


def record_private_upload(ledger: dict, request_id: str, artifact_path: Path,
                          reviewer_id: str) -> tuple[bool, str, dict]:
    """Record the distinct private-upload authorization for an exact video."""
    request = ledger["requests"].get(request_id)
    if not request:
        return False, "request_not_found", {}
    if request.get("artifact_kind") != "video":
        return False, "private_upload_requires_video_request", {}
    if request.get("creative_approval") is not True:
        return False, "creative_approval_missing", {}
    if request.get("rights_verified") is not True:
        return False, "rights_verification_missing", {}
    if request.get("eligible_for_video_assembly") is not True:
        return False, "video_assembly_eligibility_missing", {}
    if request.get("status") != "RIGHTS_VERIFIED_PENDING_PRIVATE_UPLOAD":
        return False, "invalid_private_upload_state", {}
    artifact = Path(request["artifact"])
    if artifact_path.resolve() != artifact.resolve() or not artifact.is_file():
        return False, "artifact_path_or_file_invalid", {}
    current_hash = sha256(artifact)
    if current_hash != request.get("artifact_sha256"):
        return False, "artifact_hash_changed", {}
    if request.get("private_upload_approval") is True:
        return False, "private_upload_already_decided", {}
    request["private_upload_approval"] = True
    request["youtube_upload"] = "PRIVATE_ONLY_AUTHORIZED"
    request["events"].append({
        "type": "private_upload_decision", "decision": "approve_private",
        "reviewer_id": reviewer_id, "artifact_sha256": current_hash, "at_utc": utc_now(),
    })
    return True, "ok", {"status": "PRIVATE_UPLOAD_AUTHORIZED", "request_id": request_id,
                         "creative_approval": True, "rights_verified": True,
                         "private_upload_approval": True, "youtube_upload": "PRIVATE_ONLY_AUTHORIZED"}


def record_public_schedule(ledger: dict, request_id: str, artifact_path: Path,
                           reviewer_id: str, publication_at: str) -> tuple[bool, str, dict]:
    """Authorize scheduled public publication for this exact reviewed video."""
    request = ledger["requests"].get(request_id)
    if not request:
        return False, "request_not_found", {}
    required = (request.get("artifact_kind") == "video",
                request.get("creative_approval") is True,
                request.get("rights_verified") is True,
                request.get("eligible_for_video_assembly") is True,
                request.get("status") == "RIGHTS_VERIFIED_PENDING_PRIVATE_UPLOAD")
    if not all(required):
        return False, "public_schedule_gates_incomplete", {}
    if not publication_at or "T" not in publication_at or not publication_at.endswith("Z"):
        return False, "publication_time_must_be_utc", {}
    artifact = Path(request["artifact"])
    if artifact_path.resolve() != artifact.resolve() or not artifact.is_file():
        return False, "artifact_path_or_file_invalid", {}
    current_hash = sha256(artifact)
    if current_hash != request.get("artifact_sha256"):
        return False, "artifact_hash_changed", {}
    if request.get("public_upload_approval") is True:
        return False, "public_schedule_already_authorized", {}
    request["public_upload_approval"] = True
    request["private_upload_approval"] = False
    request["youtube_upload"] = "PUBLIC_SCHEDULED_AUTHORIZED"
    request["publication"] = "scheduled_public"
    request["publication_at_utc"] = publication_at
    request["events"].append({
        "type": "public_schedule_decision", "decision": "approve_public_schedule",
        "reviewer_id": reviewer_id, "artifact_sha256": current_hash,
        "publication_at_utc": publication_at, "at_utc": utc_now(),
    })
    return True, "ok", {"status": "PUBLIC_SCHEDULE_AUTHORIZED", "request_id": request_id,
                         "creative_approval": True, "rights_verified": True,
                         "public_upload_approval": True, "publication_at_utc": publication_at,
                         "youtube_upload": "PUBLIC_SCHEDULED_AUTHORIZED"}


def record_rights_review(ledger: dict, request_id: str, reviewer_id: str,
                         evidence_url: str, notes: str, decision: str) -> tuple[bool, str, dict]:
    """Record a human rights review; never infer it from technical QA."""
    if decision not in {"verify", "reject"}:
        return False, "invalid_rights_decision", {}
    parsed = urlparse(evidence_url or "")
    if decision == "verify" and (parsed.scheme != "https" or not parsed.hostname):
        return False, "rights_evidence_must_be_https", {}
    if decision == "verify" and not (notes or "").strip():
        return False, "rights_review_notes_required", {}
    request = ledger["requests"].get(request_id)
    if not request:
        return False, "request_not_found", {}
    if request.get("creative_approval") is not True:
        return False, "creative_approval_missing", {}
    if request.get("status") != "CREATIVE_APPROVED_PENDING_RIGHTS":
        return False, "invalid_rights_review_state", {}
    artifact = Path(request["artifact"])
    if not artifact.is_file() or sha256(artifact) != request.get("artifact_sha256"):
        return False, "artifact_hash_changed", {}
    verified = decision == "verify"
    request["rights_verified"] = verified
    request["eligible_for_video_assembly"] = verified
    request["private_upload_approval"] = False
    request["youtube_upload"] = "NOT_AUTHORIZED"
    request["events"].append({
        "type": "rights_review", "decision": decision, "reviewer_id": reviewer_id,
        "evidence_url": evidence_url, "notes": notes, "artifact_sha256": request["artifact_sha256"],
        "at_utc": utc_now(),
    })
    request["status"] = "RIGHTS_VERIFIED_PENDING_PRIVATE_UPLOAD" if verified else "RIGHTS_REJECTED"
    return True, "ok", {"status": request["status"], "request_id": request_id,
                         "creative_approval": True, "rights_verified": verified,
                         "eligible_for_video_assembly": verified,
                         "private_upload_approval": False, "youtube_upload": "NOT_AUTHORIZED"}


def decide(args: argparse.Namespace) -> int:
    configured_reviewer = os.environ.get("JAZZ_SOUL_BEAT_REVIEWER_ID", "").strip()
    if not configured_reviewer or args.reviewer_id != configured_reviewer:
        return fail("reviewer_identity_not_authorized")
    with ledger_lock(args.ledger):
        ledger = load(args.ledger)
        ok, reason, result = record_decision(ledger, args.request_id, args.artifact,
                                             args.reviewer_id, args.decision)
        if not ok:
            return fail(reason)
        save(args.ledger, ledger)
    print(json.dumps(result, indent=2))
    return 0


def rights_review(args: argparse.Namespace) -> int:
    configured_reviewer = os.environ.get("JAZZ_SOUL_BEAT_RIGHTS_REVIEWER_ID", "").strip()
    if not configured_reviewer or args.reviewer_id != configured_reviewer:
        return fail("rights_reviewer_identity_not_authorized")
    with ledger_lock(args.ledger):
        ledger = load(args.ledger)
        ok, reason, result = record_rights_review(
            ledger, args.request_id, args.reviewer_id, args.evidence_url, args.notes, args.decision
        )
        if not ok:
            return fail(reason)
        save(args.ledger, ledger)
    print(json.dumps(result, indent=2))
    return 0


def verify(args: argparse.Namespace) -> int:
    ledger = load(args.ledger)
    request = ledger["requests"].get(args.request_id)
    if not request:
        return fail("request_not_found")
    artifact = Path(request["artifact"])
    valid = artifact.is_file() and sha256(artifact) == request["artifact_sha256"]
    result = {
        "status": "VALID" if valid else "BLOCKED",
        "request_id": args.request_id,
        "artifact_sha256_matches": valid,
        "creative_approval": bool(request.get("creative_approval")),
        "rights_verified": bool(request.get("rights_verified")),
        "eligible_for_video_assembly": bool(request.get("eligible_for_video_assembly")),
        "youtube_upload": request.get("youtube_upload", "NOT_AUTHORIZED"),
    }
    print(json.dumps(result, indent=2))
    return 0 if valid else 2


def supersede(args: argparse.Namespace) -> int:
    """Retire an unreviewed artifact when a safer hash-bound replacement exists."""
    with ledger_lock(args.ledger):
        ledger = load(args.ledger)
        request = ledger["requests"].get(args.request_id)
        replacement = ledger["requests"].get(args.replacement_request_id)
        if not request:
            return fail("request_not_found")
        if not replacement:
            return fail("replacement_request_not_found")
        if request.get("status") != "PENDING_HUMAN_REVIEW":
            return fail("only_pending_request_can_be_superseded")
        if replacement.get("status") != "PENDING_HUMAN_REVIEW":
            return fail("replacement_request_must_be_pending")
        if request.get("artifact_kind") != replacement.get("artifact_kind"):
            return fail("replacement_kind_mismatch")
        request["status"] = "SUPERSEDED"
        request["creative_approval"] = False
        request["rights_verified"] = False
        request["eligible_for_video_assembly"] = False
        request["youtube_upload"] = "NOT_AUTHORIZED"
        request.setdefault("events", []).append({
            "type": "request_superseded",
            "replacement_request_id": args.replacement_request_id,
            "replacement_artifact_sha256": replacement.get("artifact_sha256"),
            "at_utc": utc_now(),
        })
        save(args.ledger, ledger)
    print(json.dumps({"status": "SUPERSEDED", "request_id": args.request_id,
                      "replacement_request_id": args.replacement_request_id}, indent=2))
    return 0


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    sub = root.add_subparsers(dest="command", required=True)
    make = sub.add_parser("create-request")
    make.add_argument("--artifact", type=Path, required=True)
    make.add_argument("--kind", default="audio")
    make.add_argument("--ledger", type=Path, required=True)
    make.set_defaults(func=create)
    decide_parser = sub.add_parser("decide")
    decide_parser.add_argument("--request-id", required=True)
    decide_parser.add_argument("--artifact", type=Path, required=True)
    decide_parser.add_argument("--reviewer-id", required=True)
    decide_parser.add_argument("--decision", choices=("approve", "reject"), required=True)
    decide_parser.add_argument("--ledger", type=Path, required=True)
    decide_parser.set_defaults(func=decide)
    rights = sub.add_parser("rights-review")
    rights.add_argument("--request-id", required=True)
    rights.add_argument("--reviewer-id", required=True)
    rights.add_argument("--decision", choices=("verify", "reject"), required=True)
    rights.add_argument("--evidence-url", required=True)
    rights.add_argument("--notes", required=True)
    rights.add_argument("--ledger", type=Path, required=True)
    rights.set_defaults(func=rights_review)
    check = sub.add_parser("verify")
    check.add_argument("--request-id", required=True)
    check.add_argument("--ledger", type=Path, required=True)
    check.set_defaults(func=verify)
    retire = sub.add_parser("supersede")
    retire.add_argument("--request-id", required=True)
    retire.add_argument("--replacement-request-id", required=True)
    retire.add_argument("--ledger", type=Path, required=True)
    retire.set_defaults(func=supersede)
    return root


if __name__ == "__main__":
    args = parser().parse_args()
    try:
        raise SystemExit(args.func(args))
    except (OSError, ValueError, json.JSONDecodeError) as error:
        raise SystemExit(f"approval ledger error: {error}")
