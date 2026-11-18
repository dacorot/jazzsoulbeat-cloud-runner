import unittest
import json

from scripts.library_growth_agent import contract, plan, source_heartbeat, summarize_promotion


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

    def test_delegated_source_does_not_create_false_missing_heartbeat(self):
        registry = self._registry_path()
        result = source_heartbeat(registry, {"catalog": "success"})
        self.assertEqual(result["sources_missing_heartbeat"], [])
        self.assertEqual(result["sources_disabled_or_delegated"], ["delegated"])
        self.assertEqual(result["heartbeat"], "ACTIVE")

    @staticmethod
    def _registry_path():
        import tempfile
        from pathlib import Path
        path = Path(tempfile.mkdtemp()) / "registry.json"
        path.write_text(json.dumps({"sources": [
            {"id": "catalog", "enabled": True},
            {"id": "delegated", "enabled": False},
        ]}), encoding="utf-8")
        return path


if __name__ == "__main__":
    unittest.main()
