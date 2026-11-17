import unittest
from datetime import date

from scripts.twelve_video_plan import build_plan


class TwelveVideoPlanTests(unittest.TestCase):
    def test_creates_twelve_gated_jobs(self):
        result = build_plan(date(2026, 11, 18))
        self.assertEqual(result["target_videos"], 12)
        self.assertEqual(len(result["jobs"]), 12)
        self.assertTrue(all(job["visual_profile"] == "static_rain_steam_only" for job in result["jobs"]))
        self.assertTrue(all(job["target_duration_seconds"] == 3600 for job in result["jobs"]))
        self.assertTrue(result["no_track_repetition"])


if __name__ == "__main__":
    unittest.main()
