import json
import unittest
from pathlib import Path

from scripts.library_growth_agent import source_heartbeat


class LibrarySourceRegistryTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(__file__).resolve().parents[1]
        self.registry = self.root / "config/library_source_registry.json"

    def test_registry_has_multiple_free_fallback_sources(self):
        data = json.loads(self.registry.read_text(encoding="utf-8"))
        self.assertGreaterEqual(len(data["sources"]), 6)
        self.assertTrue(data["free_only"])
        self.assertTrue(data["never_auto_approve"])
        self.assertTrue(data["never_publish"])

    def test_heartbeat_fails_when_all_sources_are_silent(self):
        with self.assertRaises(RuntimeError):
            source_heartbeat(self.registry, {})

    def test_heartbeat_reports_active_fallback_cycle(self):
        data = json.loads(self.registry.read_text(encoding="utf-8"))
        outcomes = {row["id"]: "failure" for row in data["sources"]}
        outcomes["openverse"] = "success"
        result = source_heartbeat(self.registry, outcomes)
        self.assertEqual(result["heartbeat"], "ACTIVE")
        self.assertEqual(result["sources_succeeded"], ["openverse"])


if __name__ == "__main__":
    unittest.main()
