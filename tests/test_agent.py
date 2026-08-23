import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from agent import load_json, stable_intake_id, triage  # noqa: E402


class IntakeTriageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rules = load_json(ROOT / "config" / "routing_rules.json")

    def test_successful_intake_routes_to_senior_review(self):
        payload = load_json(ROOT / "input" / "sample_payload.json")
        record = triage(payload, self.rules)
        self.assertEqual(record["status"], "ready_for_consultant_review")
        self.assertEqual(record["route"], "senior_impact_consultant")
        self.assertEqual(record["priority_score"], 85)
        self.assertEqual(record["readiness_score"], 100)
        self.assertTrue(record["review_required"])

    def test_invalid_intake_is_not_scored(self):
        payload = load_json(ROOT / "input" / "invalid_payload.json")
        record = triage(payload, self.rules)
        self.assertEqual(record["http_status"], 422)
        self.assertEqual(record["route"], "intake_follow_up")
        self.assertIsNone(record["priority_score"])
        self.assertIn("requested_outcome", record["missing_fields"])
        self.assertEqual(len(record["validation_errors"]), 3)

    def test_same_event_produces_same_idempotency_key(self):
        payload = load_json(ROOT / "input" / "sample_payload.json")
        self.assertEqual(stable_intake_id(payload), stable_intake_id(dict(payload)))

    def test_fixture_files_are_valid_json(self):
        for relative in ["input/sample_payload.json", "input/invalid_payload.json"]:
            with (ROOT / relative).open(encoding="utf-8") as handle:
                self.assertIsInstance(json.load(handle), dict)


if __name__ == "__main__":
    unittest.main()

