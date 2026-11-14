"""Musical brief contracts: genre identity, real song form, safe original-only prompts."""
import unittest

from scripts.music_briefs import BRIEFS, choose_brief


class MusicBriefTests(unittest.TestCase):
    def test_five_editorial_channel_categories_have_distinct_arrangements(self):
        self.assertEqual(set(BRIEFS), {
            "coffee_time", "work_study", "sleep", "chill", "christian_instrumental"
        })
        self.assertEqual(len({b.title for b in BRIEFS.values()}), len(BRIEFS))
        self.assertEqual(len({b.arrangement for b in BRIEFS.values()}), len(BRIEFS))
        for brief in BRIEFS.values():
            self.assertGreater(len(brief.arrangement), 80)
            self.assertTrue(65 <= brief.bpm <= 85)
            prompt = brief.prompt(180)
            self.assertIn("original instrumental jazz/soul", prompt.lower())
            self.assertIn("natural ending", prompt.lower())
            self.assertIn("no cover", prompt.lower())

    def test_reject_short_loops_and_too_long_songs(self):
        for value in (0, 120, 179, 361, 500, 180.1, True, "180"):
            for brief in BRIEFS.values():
                with self.subTest(category=brief.slug, duration=value):
                    with self.assertRaises(ValueError):
                        brief.prompt(value)

    def test_six_minute_song_allowed(self):
        for brief in BRIEFS.values():
            self.assertIn("360-second original", brief.prompt(360))

    def test_invalid_category_is_not_silently_replaced(self):
        for value in ("", "coffee", "../chill", "christian", None, 1):
            with self.subTest(value=value), self.assertRaises(ValueError):
                choose_brief(value)

    def test_prompts_are_in_english_and_do_not_imitate_named_artist(self):
        forbidden = ("fly me to the moon", "the girl from ipanema", "frank sinatra",
                     "astrud gilberto", "what a wonderful world")
        for brief in BRIEFS.values():
            p = brief.prompt(240).lower()
            self.assertTrue(all(t not in p for t in forbidden))
            self.assertNotIn("©", p)
            self.assertIn("not background music created by looping", p)


if __name__ == "__main__":
    unittest.main()
