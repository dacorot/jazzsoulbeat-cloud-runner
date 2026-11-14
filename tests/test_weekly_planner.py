"""Safety and rotation regression tests for weekly plans."""
import datetime as dt
import unittest
from scripts.weekly_planner import CATEGORIES, plan_week, transition

class WeeklyPlanTests(unittest.TestCase):
    def test_three_days_qhd_private_gate(self):
        result = plan_week(dt.date(2026, 11, 14))
        self.assertEqual(result["target_videos"], 3)
        self.assertEqual(len(result["jobs"]), 3)
        self.assertEqual([x["target_date"] for x in result["jobs"]], ["2026-11-09", "2026-11-11", "2026-11-13"])
        for item in result["jobs"]:
            self.assertEqual((item["width"], item["height"]), (2560, 1440))
            self.assertTrue(7200 <= item["duration_seconds"] <= 10800)
            self.assertEqual(item["youtube_upload_visibility"], "private")
            self.assertFalse(item["public_scheduling_enabled"])
            self.assertFalse(item["rights_verified"])
            self.assertIsNone(item["telegram_approval_id"])
            self.assertEqual(item["state"], "PLANNED")

    def test_no_direct_approval_or_public_transition(self):
        for invalid in ("APPROVED_PRIVATE_UPLOAD", "UPLOADED_PRIVATE", "PUBLIC", "PUBLISHED"):
            with self.assertRaises(ValueError):
                transition("PLANNED", invalid)
        self.assertEqual(transition("PLANNED", "ASSETS_PENDING"), "ASSETS_PENDING")

    def test_deterministic_and_rotates_all_categories(self):
        anchor = dt.date(2026, 11, 9)
        self.assertEqual(plan_week(anchor), plan_week(anchor))
        seen = set()
        ids = set()
        for w in range(5):
            p = plan_week(anchor + dt.timedelta(weeks=w))
            for j in p["jobs"]:
                seen.add(j["category"])
                self.assertNotIn(j["job_id"], ids)
                ids.add(j["job_id"])
        self.assertEqual(seen, {row[0] for row in CATEGORIES})

    def test_bogota_week_boundary(self):
        plan = plan_week(dt.date(2026, 11, 15))
        self.assertEqual(plan["week_monday"], "2026-11-09")

if __name__ == "__main__":
    unittest.main()
