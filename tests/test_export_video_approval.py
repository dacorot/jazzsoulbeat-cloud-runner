import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "export_video_approval.py"


class ExportVideoApprovalTests(unittest.TestCase):
    def test_incomplete_video_approval_is_blocked(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            video = root / "video.mp4"
            video.write_bytes(b"video")
            digest = hashlib.sha256(b"video").hexdigest()
            ledger = root / "ledger.json"
            ledger.write_text(json.dumps({"requests": {"v1": {
                "artifact": str(video), "artifact_sha256": digest, "artifact_kind": "video",
                "creative_approval": True, "rights_verified": False,
                "private_upload_approval": False, "youtube_upload": "NOT_AUTHORIZED"
            }}}))
            result = subprocess.run([sys.executable, str(SCRIPT), "--ledger", ledger,
                                     "--request-id", "v1", "--output", root / "approval.json"],
                                    cwd=ROOT, text=True, capture_output=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("incomplete", result.stdout)

    def test_complete_private_approval_exports_exact_manifest(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            video = root / "video.mp4"
            video.write_bytes(b"video")
            digest = hashlib.sha256(b"video").hexdigest()
            ledger = root / "ledger.json"
            ledger.write_text(json.dumps({"requests": {"v1": {
                "artifact": str(video), "artifact_sha256": digest, "artifact_kind": "video",
                "creative_approval": True, "rights_verified": True,
                "private_upload_approval": True, "youtube_upload": "PRIVATE_ONLY_AUTHORIZED"
            }}}))
            output = root / "approval.json"
            result = subprocess.run([sys.executable, str(SCRIPT), "--ledger", ledger,
                                     "--request-id", "v1", "--output", output],
                                    cwd=ROOT, text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            record = json.loads(output.read_text())
            self.assertEqual(record["video_sha256"], digest)
            self.assertEqual(record["youtube_visibility"], "private")
            self.assertFalse(record["public_upload_approval"])

    def test_complete_public_schedule_exports_slot(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            video = root / "video.mp4"
            video.write_bytes(b"video")
            digest = hashlib.sha256(b"video").hexdigest()
            ledger = root / "ledger.json"
            ledger.write_text(json.dumps({"requests": {"v1": {
                "artifact": str(video), "artifact_sha256": digest, "artifact_kind": "video",
                "creative_approval": True, "rights_verified": True,
                "eligible_for_video_assembly": True, "public_upload_approval": True,
                "publication_at_utc": "2026-11-20T17:00:00Z",
                "youtube_upload": "PUBLIC_SCHEDULED_AUTHORIZED"
            }}}))
            output = root / "approval.json"
            result = subprocess.run([sys.executable, str(SCRIPT), "--ledger", ledger,
                                     "--request-id", "v1", "--output", output],
                                    cwd=ROOT, text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            record = json.loads(output.read_text())
            self.assertEqual(record["youtube_visibility"], "scheduled_public")
            self.assertEqual(record["publication_at_utc"], "2026-11-20T17:00:00Z")


if __name__ == "__main__":
    unittest.main()
