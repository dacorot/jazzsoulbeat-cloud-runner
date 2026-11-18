import tempfile
import unittest
from pathlib import Path

from scripts.agent_readiness import audit


class AgentReadinessTests(unittest.TestCase):
    def test_audit_reports_all_local_lanes(self):
        root = Path(__file__).resolve().parents[1]
        result = audit(root)
        self.assertEqual(result["technical_status"], "BLOCKED")
        self.assertEqual(len(result["checks"]), 22)
        failures = [item for item in result["checks"] if item["status"] != "PASS"]
        self.assertEqual([item["name"] for item in failures], ["longform_library_gate"])


if __name__ == "__main__":
    unittest.main()
