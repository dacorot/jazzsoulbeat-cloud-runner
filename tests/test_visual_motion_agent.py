import tempfile
import unittest
from pathlib import Path

from scripts.visual_motion_agent import create_plan


class VisualMotionAgentTests(unittest.TestCase):
    def test_plan_allows_only_locked_plate_motion(self):
        with tempfile.TemporaryDirectory() as directory:
            image = Path(directory) / "approved.png"
            image.write_bytes(b"approved base")
            plan = create_plan(image)
        self.assertEqual(plan["profile"], "single_approved_plate_integrated_motion")
        self.assertEqual(plan["animated_layers"], ["coffee_steam", "window_reflections"])
        self.assertEqual(plan["static_layers"], ["approved_base_plate"])
        self.assertEqual(plan["rain_mode"], "audition_only_until_external_masked_compositing_human_review")
        self.assertTrue(plan["rain_mask_required"])
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
