import json
import tempfile
import unittest
from pathlib import Path

from scripts.analytics_timing_agent import recommend
from scripts.orchestrator_agent import advance, new_checkpoint, save_checkpoint
from scripts.rights_decision_agent import decide


class AutonomyAgentTests(unittest.TestCase):
    def test_orchestrator_resumes_and_keeps_public_upload_disabled(self):
        checkpoint = new_checkpoint("video-02")
        checkpoint = advance(checkpoint, stage_complete=True)
        self.assertEqual(checkpoint["stage"], "RIGHTS_AND_AUDIO_QA")
        self.assertFalse(checkpoint["public_upload"])
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "checkpoint.json"
            save_checkpoint(path, checkpoint)
            self.assertEqual(json.loads(path.read_text())["video_id"], "video-02")

    def test_rights_agent_rejects_incomplete_evidence(self):
        result = decide({"title": "Jazz", "license_name": "CC BY 4.0"})
        self.assertEqual(result["decision"], "REJECTED_INCOMPLETE_RIGHTS")
        self.assertFalse(result["eligible_for_video_assembly"])

    def test_timing_agent_has_initial_matrix_and_pdca(self):
        result = recommend()
        self.assertEqual(len(result["slots"]), 3)
        self.assertIn("pdca", result)


if __name__ == "__main__":
    unittest.main()
