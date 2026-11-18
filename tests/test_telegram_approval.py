import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from scripts.telegram_approval import apply_update, build_review_message, callback_data, parse_callback


class TelegramApprovalTests(unittest.TestCase):
    def make_ledger(self, root: Path):
        artifact = root / "candidate.mp3"
        artifact.write_bytes(b"candidate")
        request_id = "request_ABC123"
        ledger = root / "ledger.json"
        ledger.write_text(json.dumps({"schema_version": 1, "requests": {request_id: {
            "request_id": request_id, "artifact": str(artifact),
            "artifact_sha256": hashlib.sha256(b"candidate").hexdigest(),
            "status": "PENDING_HUMAN_REVIEW", "creative_approval": False,
            "rights_verified": False, "eligible_for_video_assembly": False,
            "youtube_upload": "NOT_AUTHORIZED", "events": []
        }}}))
        return artifact, ledger, request_id

    def test_callback_is_strict_and_bounded(self):
        value = callback_data("request_ABC123", "approve")
        self.assertLessEqual(len(value.encode()), 64)
        self.assertEqual(parse_callback(value), ("request_ABC123", "approve"))
        with self.assertRaises(ValueError):
            parse_callback("jsb1:request_ABC123:approve:extra")

    def test_telegram_identity_and_hash_are_checked(self):
        with tempfile.TemporaryDirectory() as directory:
            artifact, ledger, request_id = self.make_ledger(Path(directory))
            update = {"callback_query": {"from": {"id": 77},
                      "data": callback_data(request_id, "approve")}}
            unauthorized = apply_update(update, ledger, "88")
            self.assertEqual(unauthorized["reason"], "telegram_identity_not_authorized")
            artifact.write_bytes(b"tampered")
            tampered = apply_update(update, ledger, "77")
            self.assertEqual(tampered["reason"], "artifact_hash_changed")

    def test_authorized_decision_stays_creative_only(self):
        with tempfile.TemporaryDirectory() as directory:
            artifact, ledger, request_id = self.make_ledger(Path(directory))
            request = json.loads(ledger.read_text())["requests"][request_id]
            caption, markup = build_review_message(request, request_id)
            self.assertIn(request["artifact_sha256"], caption)
            self.assertIn("callback_data", markup["inline_keyboard"][0][0])
            update = {"callback_query": {"from": {"id": 77},
                      "data": callback_data(request_id, "approve")}}
            result = apply_update(update, ledger, "77")
            self.assertTrue(result["creative_approval"])
            state = json.loads(ledger.read_text())["requests"][request_id]
            self.assertFalse(state["rights_verified"])
            self.assertFalse(state["eligible_for_video_assembly"])
            self.assertEqual(state["youtube_upload"], "NOT_AUTHORIZED")

    def test_private_upload_is_separate_and_requires_rights(self):
        with tempfile.TemporaryDirectory() as directory:
            artifact, ledger, request_id = self.make_ledger(Path(directory))
            state = json.loads(ledger.read_text())
            request = state["requests"][request_id]
            request.update({"artifact_kind": "video", "creative_approval": True,
                            "rights_verified": True, "eligible_for_video_assembly": True,
                            "status": "RIGHTS_VERIFIED_PENDING_PRIVATE_UPLOAD"})
            ledger.write_text(json.dumps(state))
            update = {"callback_query": {"from": {"id": 77},
                      "data": callback_data(request_id, "private")}}
            result = apply_update(update, ledger, "77")
            self.assertEqual(result["status"], "PRIVATE_UPLOAD_AUTHORIZED")
            final = json.loads(ledger.read_text())["requests"][request_id]
            self.assertTrue(final["private_upload_approval"])
            self.assertEqual(final["youtube_upload"], "PRIVATE_ONLY_AUTHORIZED")

    def test_rights_verified_video_message_exposes_only_private_action(self):
        with tempfile.TemporaryDirectory() as directory:
            artifact, ledger, request_id = self.make_ledger(Path(directory))
            state = json.loads(ledger.read_text())
            request = state["requests"][request_id]
            request.update({"artifact_kind": "video", "creative_approval": True,
                            "rights_verified": True, "eligible_for_video_assembly": True,
                            "status": "RIGHTS_VERIFIED_PENDING_PRIVATE_UPLOAD"})
            _, markup = build_review_message(request, request_id)
            buttons = [button["text"] for row in markup["inline_keyboard"] for button in row]
            self.assertEqual(buttons, ["Authorize PRIVATE YouTube upload", "Schedule PUBLIC publication"])

    def test_public_schedule_is_separate_and_hash_bound(self):
        with tempfile.TemporaryDirectory() as directory:
            artifact, ledger, request_id = self.make_ledger(Path(directory))
            state = json.loads(ledger.read_text())
            request = state["requests"][request_id]
            request.update({"artifact_kind": "video", "creative_approval": True,
                            "rights_verified": True, "eligible_for_video_assembly": True,
                            "status": "RIGHTS_VERIFIED_PENDING_PRIVATE_UPLOAD"})
            ledger.write_text(json.dumps(state))
            update = {"callback_query": {"from": {"id": 77},
                      "data": callback_data(request_id, "public")}}
            result = apply_update(update, ledger, "77")
            self.assertEqual(result["status"], "PUBLIC_SCHEDULE_AUTHORIZED")
            final = json.loads(ledger.read_text())["requests"][request_id]
            self.assertTrue(final["public_upload_approval"])
            self.assertTrue(final["publication_at_utc"].endswith("Z"))
            self.assertEqual(final["youtube_upload"], "PUBLIC_SCHEDULED_AUTHORIZED")


if __name__ == "__main__":
    unittest.main()
