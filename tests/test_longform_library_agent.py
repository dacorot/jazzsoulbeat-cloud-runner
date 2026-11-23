import unittest

from scripts.longform_library_agent import plan


class LongformLibraryAgentTests(unittest.TestCase):
    def test_blocks_until_ten_hours_of_unique_approved_audio_exists(self):
        ledger = {"requests": {
            "a": {"artifact_kind": "audio", "creative_approval": True,
                  "rights_verified": True, "eligible_for_video_assembly": True,
                  "artifact": "a.flac", "artifact_sha256": "a", "duration_seconds": 360},
            "b": {"artifact_kind": "audio", "creative_approval": True,
                  "rights_verified": True, "eligible_for_video_assembly": True,
                  "artifact": "b.flac", "artifact_sha256": "b", "duration_seconds": 330},
        }}
        result = plan(ledger)
        self.assertEqual(result["status"], "BLOCKED_NEEDS_MORE_APPROVED_TRACKS")
        self.assertEqual(result["approved_seconds"], 690)
        self.assertTrue(result["no_track_repetition"])

    def test_ready_when_unique_approved_audio_reaches_ten_hour_target(self):
        ledger = {"requests": {
            str(i): {"artifact_kind": "audio", "creative_approval": True,
                     "rights_verified": True, "eligible_for_video_assembly": True,
                     "artifact": f"{i}.flac", "artifact_sha256": str(i),
                     "duration_seconds": 120}
            for i in range(500)
        }}
        self.assertEqual(plan(ledger)["status"], "READY_FOR_LONGFORM_ASSEMBLY")


if __name__ == "__main__":
    unittest.main()
