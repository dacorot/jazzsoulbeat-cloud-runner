import tempfile
import unittest
from pathlib import Path

from scripts.agent_readiness import audit


class AgentReadinessTests(unittest.TestCase):
    def test_audit_reports_all_local_lanes(self):
        root = Path(__file__).resolve().parents[1]
        result = audit(root)
        self.assertEqual(result["technical_status"], "BLOCKED")
        library = next(item for item in result["checks"] if item["name"] == "longform_library_gate")
        self.assertEqual(library["status"], "FAIL")
        self.assertIn("missing_unique_tracks", library["details"]["error"])
        self.assertEqual(len(result["checks"]), 25)
        failures = [item for item in result["checks"] if item["status"] != "PASS"]
        self.assertEqual(
            {item["name"] for item in failures},
            {"longform_library_gate", "project_compliance_audit"},
        )


if __name__ == "__main__":
    unittest.main()
