import tempfile
import unittest
from pathlib import Path

from scripts.visual_motion_agent import create_plan


class VisualMotionAgentTests(unittest.TestCase):
    def test_plan_requires_an_effect_profile(self):
        with tempfile.TemporaryDirectory() as directory:
            image = Path(directory) / "approved.png"
            image.write_bytes(b"approved base")
            plan = create_plan(image)
        self.assertEqual(plan["profile"], "rain")
        self.assertIn("window_rain", plan["animated_layers"])
        self.assertEqual(plan["effect_profile"], "rain")
        self.assertEqual(plan["camera"], "locked")
        self.assertFalse(plan["creative_approval"])

    def test_plan_rejects_other_render_contracts(self):
        with tempfile.TemporaryDirectory() as directory:
            image = Path(directory) / "approved.png"
            image.write_bytes(b"approved base")
            with self.assertRaisesRegex(ValueError, "20_to_360"):
                create_plan(image, duration=10)
            with self.assertRaisesRegex(ValueError, "30_fps"):
                create_plan(image, fps=24)
            with self.assertRaisesRegex(ValueError, "unknown_effect_profile"):
                create_plan(image, effect_profile="none")


if __name__ == "__main__":
    unittest.main()
