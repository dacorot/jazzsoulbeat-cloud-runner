"""Independent audio signal checks must not approve music or rights."""
from __future__ import annotations
import hashlib
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import music_audio_qc as qc


class TechnicalAudioQATests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.old = Path.cwd()
        os.chdir(self.tmp.name)
        self.staged = Path("music-production/generated")
        self.staged.mkdir(parents=True)
        self.path = self.staged / "candidate.mp3"
        self.path.write_bytes(b"a valid-shape placeholder" * 12000)
        self.record = Path("music-production/production_report.json")
        self.report = {
            "status": "generated_audio_needs_human_review",
            "file": str(self.path),
            "sha256": hashlib.sha256(self.path.read_bytes()).hexdigest(),
            "duration_actual_seconds": 180.0,
            "rights_verified": False,
            "creative_approval": False,
            "eligible_for_video_assembly": False,
            "publication_status": "NOT_PUBLISHED",
            "genre": "jazz",
            "genre_signature": "extended harmony, comping, melodic improvisation",
            "genre_authenticity_status": "PENDING_HUMAN_LISTENING",
        }
        self.save()

    def tearDown(self):
        os.chdir(self.old)
        self.tmp.cleanup()

    def save(self):
        self.record.write_text(json.dumps(self.report), encoding="utf-8")

    def fake_media(self, valid=True, silence=False):
        probe = {
            "streams": [{"codec_type": "audio", "sample_rate": "44100", "channels": 2}],
            "format": {"duration": "180.0"},
        }
        measurements = "mean_volume: -17.0 dB\nmax_volume: -1.5 dB"
        if silence:
            measurements += "\nsilence_start: 13.5\nsilence_end: 38.5"
        calls = [
            subprocess.CompletedProcess([], 0, stdout=json.dumps(probe), stderr=""),
            subprocess.CompletedProcess([], 0, stdout="", stderr=measurements),
        ]
        return patch.object(qc, "run_media_command", side_effect=calls)

    def test_valid_media_is_only_technically_passed(self):
        with self.fake_media():
            report = qc.verify_audio(self.record)
        self.assertEqual(report["status"], "PASS_TECHNICAL_AUDIO_ONLY")
        self.assertFalse(report["eligible_for_video_assembly"])
        self.assertFalse(report["creative_approval"])
        self.assertFalse(report["rights_verified"])

    def test_corrupted_file_checksum_blocks(self):
        self.path.write_bytes(self.path.read_bytes()+b"corrupted")
        with self.assertRaisesRegex(qc.AudioQualityError, "SHA-256"):
            qc.verify_audio(self.record)

    def test_previous_human_approval_field_blocks_auto_reuse(self):
        self.report["creative_approval"] = True
        self.save()
        with self.assertRaisesRegex(qc.AudioQualityError, "cannot be creatively approved"):
            qc.verify_audio(self.record)

    def test_excessive_silence_is_blocked(self):
        with self.fake_media(silence=True):
            with self.assertRaisesRegex(qc.AudioQualityError, "Excessive extended silence"):
                qc.verify_audio(self.record)

    def test_missing_audio_never_passes(self):
        self.path.unlink()
        with self.assertRaisesRegex(qc.AudioQualityError, "private staging"):
            qc.verify_audio(self.record)

    def test_extra_video_stream_blocks(self):
        probe = {
            "streams": [
                {"codec_type": "audio", "sample_rate": "44100", "channels": 2},
                {"codec_type": "video"},
            ],
            "format": {"duration": "180.0"},
        }
        with patch.object(qc, "run_media_command",
                          return_value=subprocess.CompletedProcess([], 0, stdout=json.dumps(probe), stderr="")):
            with self.assertRaisesRegex(qc.AudioQualityError, "one audio stream"):
                qc.verify_audio(self.record)

    def test_audio_outside_project_staging_blocks(self):
        outside = Path("music-production/unreviewed.mp3")
        outside.write_bytes(self.path.read_bytes())
        self.report["file"] = str(outside)
        self.save()
        with self.assertRaisesRegex(qc.AudioQualityError, "private staging"):
            qc.verify_audio(self.record)


if __name__ == "__main__":
    unittest.main()
