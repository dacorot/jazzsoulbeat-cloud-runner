import unittest

from scripts.library_promotion_agent import promote


class LibraryPromotionTests(unittest.TestCase):
    def candidate(self, **overrides):
        row = {
            "decision": "ELIGIBLE_FOR_LIBRARY", "rights_verified": True,
            "eligible_for_video_assembly": True, "title": "Blue Hour",
            "artist": "Artist", "artifact": "tracks/blue.mp3",
            "artifact_sha256": "a" * 64, "duration_seconds": 240,
            "license_name": "CC BY 4.0", "source_url": "https://example.test/blue",
            "attribution": "Artist — CC BY 4.0",
        }
        row.update(overrides)
        return row

    def test_promotes_only_eligible_hash_bound_candidate(self):
        result = promote([self.candidate()])
        self.assertEqual(len(result["approved"]), 1)
        self.assertEqual(result["approved_seconds"], 240)

    def test_rejects_ambiguous_candidate(self):
        result = promote([self.candidate(decision="REJECTED_INCOMPLETE_RIGHTS")])
        self.assertEqual(result["approved"], [])
        self.assertIn("rights_decision_not_eligible", result["rejected"][0]["reasons"])

    def test_rejects_duplicate_hash(self):
        result = promote([self.candidate()], existing=[self.candidate()])
        self.assertEqual(result["approved"], [])
        self.assertIn("duplicate_artifact_hash", result["rejected"][0]["reasons"])


if __name__ == "__main__":
    unittest.main()
