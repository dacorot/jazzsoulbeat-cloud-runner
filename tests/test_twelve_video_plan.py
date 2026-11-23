import unittest
from datetime import date

from scripts.twelve_video_plan import build_plan


class TwelveVideoPlanTests(unittest.TestCase):
    def test_creates_twelve_gated_jobs(self):
        result = build_plan(date(2026, 11, 18))
        self.assertEqual(result["target_videos"], 12)
        self.assertEqual(len(result["jobs"]), 12)
        self.assertTrue(all(job["visual_profile"] in {"rain", "steam", "mist", "snow", "breeze"} for job in result["jobs"]))
        self.assertTrue(all(7200 <= job["target_duration_seconds"] <= 10800 for job in result["jobs"]))
        self.assertTrue(all(job["target_duration_seconds"] in {7200, 10800} for job in result["jobs"]))
        self.assertTrue(result["no_track_repetition"])
        self.assertEqual(len(result["parallel_music_lanes"]), 3)


if __name__ == "__main__":
    unittest.main()
