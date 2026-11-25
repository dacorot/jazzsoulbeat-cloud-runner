"""ACE-Step adapter fault-injection: no network, no billing, no publication."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

SOURCE = Path(__file__).resolve().parents[1] / "scripts" / "music_producer_agent.py"


class ProducerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.previous_cwd = Path.cwd()
        os.chdir(self.temp.name)
        spec = importlib.util.spec_from_file_location("producer_under_test", SOURCE)
        self.producer = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.producer)

    def tearDown(self):
        os.chdir(self.previous_cwd)
        self.temp.cleanup()

    def fake_client(self, *, api=True, result=None, error=None):
        class Client:
            def __init__(self, *args, **kwargs):
                pass

            def view_api(self, return_format="dict"):
                if not api:
                    return {"named_endpoints": {"/obsolete": {}}}
                return {
                    "named_endpoints": {
                        "/generation_wrapper": {
                            "parameters": [
                                {
                                    "parameter_name": n,
                                    "parameter_has_default": True,
                                    "parameter_default": 180,
                                } for n in (
                                    "selected_model", "param_4", "param_5",
                                    "param_6", "param_7", "param_15",
                                    "param_16", "param_23",
                                )
                            ],
                        },
                    },
                }

            def predict(self, *args, **kwargs):
                if error is not None:
                    raise error
                return str(result)

        return patch.dict(sys.modules, {"gradio_client": SimpleNamespace(Client=Client)})

    def test_success_is_only_pending_review_not_rights_verified(self):
        source = Path(self.temp.name) / "external-output.mp3"
        source.write_bytes(b"faked audio bytes" * 9000)
        probe = {
            "format": {"duration": "240.02"},
            "streams": [{"codec_type": "audio"}],
        }
        with self.fake_client(result=source), patch.object(
            self.producer.subprocess, "run",
            return_value=subprocess.CompletedProcess(
                args=["ffprobe"], returncode=0, stdout=json.dumps(probe),
            ),
        ):
            self.assertEqual(self.producer.main(), 0)
        report = json.loads((self.producer.OUT / "production_report.json").read_text())
        self.assertEqual(report["status"], "generated_audio_needs_human_review")
        self.assertIs(report["rights_verified"], False)
        self.assertIs(report["human_review_required"], True)
        self.assertEqual(report["publication_status"], "NOT_PUBLISHED")
        self.assertAlmostEqual(report["duration_actual_seconds"], 240.02)
        self.assertEqual(
            report["sha256"],
            hashlib.sha256((self.producer.AUDIO / "candidate.mp3").read_bytes()).hexdigest(),
        )

    def test_corrupt_audio_fails_closed_and_removes_candidate(self):
        source = Path(self.temp.name) / "fake.mp3"
        source.write_bytes(b"not audio" * 20000)
        with self.fake_client(result=source), patch.object(
            self.producer.subprocess, "run",
            side_effect=subprocess.CalledProcessError(1, "ffprobe"),
        ):
            self.assertEqual(self.producer.main(), 1)
        report = json.loads((self.producer.OUT / "production_report.json").read_text())
        self.assertEqual(report["status"], "blocked_invalid_audio")
        self.assertFalse((self.producer.AUDIO / "candidate.mp3").exists())
        self.assertNotIn("rights_verified", report)

    def test_changed_endpoint_is_reported_not_guessed(self):
        with self.fake_client(api=False):
            self.assertEqual(self.producer.main(), 1)
        report = json.loads((self.producer.OUT / "production_report.json").read_text())
        self.assertEqual(report["status"], "blocked_api_changed")

    def test_provider_quota_is_recorded_without_fallback(self):
        with self.fake_client(
            error=RuntimeError(
                "You have exceeded your ZeroGPU quota (180s requested vs. 145s left). "
                "Try again in 9:02:23."
            )
        ):
            self.assertEqual(self.producer.main(), 1)
        report = json.loads((self.producer.OUT / "production_report.json").read_text())
        self.assertEqual(report["status"], "blocked_free_quota")
        self.assertEqual(report["cost_policy"], "free_only")
        self.assertIn("9:02:23", report["details"]["provider_retry_hint"])
        self.assertFalse(any(self.producer.AUDIO.iterdir()))

    def test_provider_rate_limit_fails_closed(self):
        with self.fake_client(error=RuntimeError("HTTP 429: rate limit exceeded")):
            self.assertEqual(self.producer.main(), 1)
        report = json.loads((self.producer.OUT / "production_report.json").read_text())
        self.assertEqual(report["status"], "blocked_rate_limit")
        self.assertEqual(report["cost_policy"], "free_only")

    def test_generation_failure_cannot_be_marked_as_success(self):
        with self.fake_client(error=TimeoutError("free space timed out")):
            self.assertEqual(self.producer.main(), 1)
        report = json.loads((self.producer.OUT / "production_report.json").read_text())
        self.assertEqual(report["status"], "blocked_generation")

    def test_free_space_model_not_initialized_is_diagnosed(self):
        with self.fake_client(
            result="❌ Model not fully initialized. Missing components: ['model', 'vae', 'text_tokenizer', 'text_encoder']"
        ):
            self.assertEqual(self.producer.main(), 1)
        report = json.loads((self.producer.OUT / "production_report.json").read_text())
        self.assertEqual(report["status"], "blocked_model_uninitialized")
        self.assertEqual(report["cost_policy"], "free_only")
        self.assertFalse(any(self.producer.AUDIO.iterdir()))

    def test_untrusted_urls_are_not_downloaded(self):
        with self.fake_client(result="http://169.254.169.254/latest/meta-data/"):
            self.assertEqual(self.producer.main(), 1)
        result = json.loads((self.producer.OUT / "production_report.json").read_text())
        self.assertEqual(result["status"], "blocked_no_audio_file")
        self.assertFalse(any(self.producer.AUDIO.iterdir()))

    def test_invalid_category_fails_before_network(self):
        with patch.dict(os.environ, {"MUSIC_CATEGORY": "../unapproved"}, clear=False):
            self.assertEqual(self.producer.main(), 1)
        report = json.loads((self.producer.OUT / "production_report.json").read_text())
        self.assertEqual(report["status"], "blocked_invalid_brief")

    def test_too_short_track_fails_before_network(self):
        with patch.dict(os.environ, {"MUSIC_DURATION_SECONDS": "120"}, clear=False):
            self.assertEqual(self.producer.main(), 1)
        report = json.loads((self.producer.OUT / "production_report.json").read_text())
        self.assertEqual(report["status"], "blocked_invalid_brief")

    def test_success_still_cannot_be_assembled_without_human_review(self):
        source = Path(self.temp.name) / "approved-output.flac"
        source.write_bytes(b"faked media bytes" * 14000)
        probe = {"format": {"duration": "244"}, "streams": [{"codec_type": "audio"}]}
        with self.fake_client(result=source), patch.object(
            self.producer.subprocess, "run",
            return_value=subprocess.CompletedProcess(
                args=["ffprobe"], returncode=0, stdout=json.dumps(probe),
            ),
        ):
            self.assertEqual(self.producer.main(), 0)
        report = json.loads((self.producer.OUT / "production_report.json").read_text())
        self.assertEqual(report["editorial_verdict"], "PENDING_HUMAN_LISTENING")
        self.assertIs(report["creative_approval"], False)
        self.assertIs(report["eligible_for_video_assembly"], False)
        self.assertEqual(report["category"], "coffee_time")

    def test_provider_device_mismatch_is_not_a_song(self):
        message = (
            "❌ Error: Expected all tensors to be on the same device, "
            "but got mat2 is on cpu, different from other tensors on cuda:0"
        )
        with self.fake_client(result=message):
            self.assertEqual(self.producer.main(), 1)
        report = json.loads((self.producer.OUT / "production_report.json").read_text())
        self.assertEqual(report["status"], "blocked_provider_device_mismatch")
        self.assertFalse(any(self.producer.AUDIO.iterdir()))

    def test_unapproved_backend_model_is_rejected_without_network(self):
        with patch.dict(os.environ, {"ACE_STEP_MODEL": "paid-proprietary-model"}, clear=False):
            self.assertEqual(self.producer.main(), 1)
        report = json.loads((self.producer.OUT / "production_report.json").read_text())
        self.assertEqual(report["status"], "blocked_invalid_brief")

    def test_wrong_duration_is_rejected(self):
        source = Path(self.temp.name) / "bad-duration.mp3"
        source.write_bytes(b"fake-data" * 15000)
        probe = {"format": {"duration": "4.0"}, "streams": [{"codec_type": "audio"}]}
        with self.fake_client(result=source), patch.object(
            self.producer.subprocess, "run",
            return_value=subprocess.CompletedProcess(
                args=["ffprobe"], returncode=0, stdout=json.dumps(probe),
            ),
        ):
            self.assertEqual(self.producer.main(), 1)
        report = json.loads((self.producer.OUT / "production_report.json").read_text())
        self.assertEqual(report["status"], "blocked_invalid_audio")


if __name__ == "__main__":
    unittest.main()
