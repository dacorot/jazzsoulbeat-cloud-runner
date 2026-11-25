import tempfile
import unittest
from pathlib import Path

from scripts.agent_readiness import audit


class AgentReadinessTests(unittest.TestCase):
    def test_audit_reports_all_local_lanes(self):
        root = Path(__file__).resolve().parents[1]
        result = audit(root)
        self.assertEqual(result["technical_status"], "READY")
        self.assertEqual(len(result["checks"]), 25)
        library = next(item for item in result["checks"] if item["name"] == "longform_library_gate")
        compliance = next(item for item in result["checks"] if item["name"] == "project_compliance_audit")
        self.assertEqual(library["details"]["status"], "WAITING_FOR_PRIVATE_LIBRARY")
        self.assertEqual(compliance["details"]["status"], "WAITING_FOR_PRIVATE_LIBRARY")


if __name__ == "__main__":
    unittest.main()
