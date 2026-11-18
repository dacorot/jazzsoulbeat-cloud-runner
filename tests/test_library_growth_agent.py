import unittest

from scripts.library_growth_agent import contract, plan, summarize_promotion


class LibraryGrowthTests(unittest.TestCase):
    def test_contract_is_private_and_pending_safe(self):
        result = contract()
        self.assertTrue(result["pdca"])
        self.assertTrue(result["never_auto_approve"])
        self.assertTrue(result["never_publish"])

    def test_reports_capacity_gap(self):
        result = plan(690)
        self.assertEqual(result["status"], "GROWTH_REQUIRED")
        self.assertEqual(result["missing_seconds"], 6510.0)
        self.assertFalse(result["human_review_required"])
        self.assertEqual(result["final_human_gate"], "video_artifact_approval_only")

    def test_counts_only_promoted_report_rows(self):
        result = summarize_promotion({
            "approved": [{"duration_seconds": 240}, {"duration_seconds": 180}],
            "rejected": [{"title": "ambiguous"}],
        })
        self.assertEqual(result["promoted_tracks"], 2)
        self.assertEqual(result["promoted_seconds"], 420)
        self.assertEqual(result["rejected_tracks"], 1)


if __name__ == "__main__":
    unittest.main()
