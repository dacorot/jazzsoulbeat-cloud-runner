import tempfile
import unittest
from pathlib import Path

from scripts.visual_motion_agent import create_plan


class VisualMotionAgentTests(unittest.TestCase):
    def test_plan_allows_only_steam_motion_and_static_rain(self):
        with tempfile.TemporaryDirectory() as directory:
            image = Path(directory) / "approved.png"
            image.write_bytes(b"approved base")
            plan = create_plan(image)
        self.assertEqual(plan["profile"], "static_rain_steam_only")
        self.assertEqual(plan["animated_layers"], ["coffee_steam"])
        self.assertIn("exterior_rain_texture", plan["static_layers"])
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


if __name__ == "__main__":
    unittest.main()
