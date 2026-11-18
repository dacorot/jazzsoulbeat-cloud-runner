import unittest

from scripts.seasonal_music_agent import contract, create_brief


class SeasonalMusicAgentTests(unittest.TestCase):
    def test_contract(self):
        result = contract()
        self.assertTrue(result["never_auto_approve"])
        self.assertTrue(result["never_publish"])
        self.assertTrue(result["pdca"])

    def test_summer_coffee(self):
        result = create_brief("summer", "coffee_time", [{"approved": True, "rights_verified": True}])
        self.assertIn("bossa nova", result["genres"])
        self.assertEqual(result["language"], "English")

    def test_unapproved_track_blocks(self):
        with self.assertRaises(ValueError):
            create_brief("spring", "coffee_time", [{"approved": False, "rights_verified": False}])
