import tempfile
import unittest
from pathlib import Path

from scripts.agent_readiness import audit


class AgentReadinessTests(unittest.TestCase):
    def test_audit_reports_all_local_lanes(self):
        root = Path(__file__).resolve().parents[1]
        result = audit(root)
        self.assertEqual(result["technical_status"], "READY")
        self.assertEqual(len(result["checks"]), 18)
        self.assertTrue(all(item["status"] == "PASS" for item in result["checks"]))


if __name__ == "__main__":
    unittest.main()
