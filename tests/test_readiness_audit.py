import json
import hashlib
import tempfile
import unittest
from pathlib import Path

from scripts.readiness_audit import audit


class ReadinessAuditTests(unittest.TestCase):
    def test_audit_records_hash_bound_source_evidence_and_generation_time(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            music = root / "music-production"
            music.mkdir(parents=True)
            ledger = music / "approval_ledger.json"
            ledger.write_text(json.dumps({"schema_version": 1, "requests": {}}), encoding="utf-8")

            result = audit(root)

            self.assertRegex(result["generated_at_utc"], r"Z$")
            evidence = result["sources"]["approval_ledger"]
            self.assertEqual(evidence["path"], "music-production/approval_ledger.json")
            self.assertEqual(evidence["sha256"], hashlib.sha256(ledger.read_bytes()).hexdigest())
            self.assertTrue(evidence["exists"])

    def test_audio_approval_is_read_from_hash_bound_ledger(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            music = root / "music-production"
            generated = music / "generated"
            generated.mkdir(parents=True)
            artifact = generated / "approved.flac"
            artifact.write_bytes(b"approved audio")
            digest = hashlib.sha256(artifact.read_bytes()).hexdigest()
            (music / "AUDITION_INDEX.json").write_text(json.dumps({"candidates": [{
                "title": "Approved", "file": "music-production/generated/approved.flac",
                "sha256": digest, "approval_request_id": "r_approved",
                "creative_approval": False, "rights_verified": False,
            }]}), encoding="utf-8")
            (music / "approval_ledger.json").write_text(json.dumps({"schema_version": 1, "requests": {
                "r_approved": {"artifact": str(artifact), "artifact_sha256": digest,
                               "status": "CREATIVE_APPROVED_PENDING_RIGHTS",
                               "creative_approval": True, "rights_verified": False}
            }}), encoding="utf-8")
            result = audit(root)
            self.assertTrue(result["gates"]["human_creative_audio_approval"])
            self.assertTrue(result["candidates"][0]["creative_approval"])
            self.assertFalse(result["gates"]["rights_verification"])

    def test_audit_never_promotes_pending_material(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "music-production").mkdir()
            result = audit(root)
            self.assertEqual(result["status"], "INCOMPLETE")
            self.assertFalse(result["gates"]["human_creative_audio_approval"])
            self.assertFalse(result["gates"]["private_upload_approval"])
            self.assertEqual(result["publication"], "HUMAN_GATED")

    def test_qhd_gate_requires_the_manifest_hash_to_match_the_mp4(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            review_dir = root / "music-production" / "visual-review"
            review_dir.mkdir(parents=True)
            video = review_dir / "review.mp4"
            video.write_bytes(b"original")
            report = {
                "video": "music-production/visual-review/review.mp4",
                "video_sha256": "wrong-hash",
                "width": 2560,
                "height": 1440,
                "duration_seconds": 240,
                "creative_approval": False,
            }
            (review_dir / "review.review.json").write_text(json.dumps(report), encoding="utf-8")
            result = audit(root)
            self.assertFalse(result["gates"]["qhd_review_render_exists"])
            self.assertFalse(result["qhd_reviews"][0]["file_intact"])

    def test_qhd_gate_rejects_a_missing_mp4_even_when_manifest_is_valid(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            review_dir = root / "music-production" / "visual-review"
            review_dir.mkdir(parents=True)
            report = {
                "video": "music-production/visual-review/missing.mp4",
                "video_sha256": "not-relevant",
                "width": 2560,
                "height": 1440,
                "duration_seconds": 240,
                "creative_approval": False,
            }
            (review_dir / "missing.review.json").write_text(json.dumps(report), encoding="utf-8")
            result = audit(root)
            self.assertFalse(result["gates"]["qhd_review_render_exists"])
            self.assertFalse(result["qhd_reviews"][0]["file_intact"])

    def test_qhd_gate_requires_a_sha256_field(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            review_dir = root / "music-production" / "visual-review"
            review_dir.mkdir(parents=True)
            video = review_dir / "review.mp4"
            video.write_bytes(b"video")
            report = {
                "video": "music-production/visual-review/review.mp4",
                "width": 2560,
                "height": 1440,
                "duration_seconds": 240,
                "creative_approval": False,
            }
            (review_dir / "review.review.json").write_text(json.dumps(report), encoding="utf-8")
            result = audit(root)
            self.assertFalse(result["gates"]["qhd_review_render_exists"])
            self.assertFalse(result["qhd_reviews"][0]["file_intact"])


if __name__ == "__main__":
    unittest.main()
