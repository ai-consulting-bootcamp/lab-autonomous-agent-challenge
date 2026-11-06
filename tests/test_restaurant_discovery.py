import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from restaurant_discovery import load_catalog, run_discovery  # noqa: E402


CATALOG_PATH = ROOT / "fixtures" / "restaurants.demo.json"


class RestaurantDiscoveryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = load_catalog(CATALOG_PATH)

    def run_case(self, message, session_id="test-session"):
        return run_discovery(
            {"session_id": session_id, "message": message},
            catalog=self.catalog,
            execution_id="local-test",
            executed_at="2026-11-06T00:00:00Z",
        )

    def test_t01_exact_match_is_grounded_and_under_budget(self):
        output, trace = self.run_case(
            "I'm in Heidelberg and would like Greek food for dinner, preferably under 30 euros."
        )
        self.assertEqual(output["status"], "ok")
        self.assertEqual([item["restaurant_id"] for item in output["matched_restaurants"]], ["demo-gr-01"])
        self.assertEqual(output["matched_restaurants"][0]["booking_channel"], "unknown")
        self.assertEqual(trace["search"]["matched_ids"], ["demo-gr-01"])
        self.assertFalse(output["availability_checked"])

    def test_t02_empty_and_non_string_messages_are_errors_without_search(self):
        for message in ("", "   ", 42):
            payload = {"session_id": "test-session", "message": message}
            output, trace = run_discovery(payload, catalog=self.catalog, execution_id="local-test")
            self.assertEqual(output["status"], "error")
            self.assertFalse(output["search_performed"])
            self.assertFalse(trace["search"]["performed"])

    def test_malformed_payload_is_error(self):
        output, trace = run_discovery(["not", "an", "object"], catalog=self.catalog)
        self.assertEqual(output["error_code"], "invalid_payload")
        self.assertFalse(trace["search"]["performed"])

    def test_t03_missing_city_asks_for_city_without_assuming_one(self):
        output, trace = self.run_case("I feel like Greek food under 30 euros.")
        self.assertEqual(output["status"], "needs_clarification")
        self.assertIsNone(output["preferences"]["city"])
        self.assertIn("Which city", output["message"])
        self.assertFalse(trace["search"]["performed"])

    def test_t04_no_exact_match_labels_alternatives(self):
        output, trace = self.run_case("I'm in Heidelberg and would like Japanese food.")
        self.assertEqual(output["status"], "no_exact_match")
        self.assertEqual(output["matched_restaurants"], [])
        self.assertTrue(output["alternative_restaurants"])
        self.assertIn("alternatives", output["message"])
        self.assertTrue(trace["search"]["alternative_ids"])

    def test_t05_unknown_atmosphere_is_not_invented(self):
        output, _ = self.run_case("I'm in Heidelberg and want Greek food with a quiet atmosphere.")
        self.assertIn("not documented", output["message"])
        self.assertIsNone(output["matched_restaurants"][0]["atmosphere"])

    def test_t06_booking_request_does_not_claim_reservation(self):
        output, _ = self.run_case("Book Greek food in Heidelberg under 30 euros.")
        self.assertEqual(output["intent"], "booking_request")
        self.assertIn("does not place reservations", output["message"])
        self.assertFalse(output["availability_checked"])

    def test_t07_unknown_booking_channel_remains_unknown(self):
        output, _ = self.run_case("Greek food in Heidelberg under 30 euros.")
        item = output["matched_restaurants"][0]
        self.assertEqual(item["booking_channel"], "unknown")
        self.assertNotIn("unavailable", output["message"].lower())

    def test_t08_catalog_failure_is_safe_and_structured(self):
        output, trace = run_discovery(
            {"session_id": "test-session", "message": "Greek food in Heidelberg"},
            catalog_path=ROOT / "fixtures" / "missing.catalog.json",
            execution_id="local-test",
        )
        self.assertEqual(output["status"], "error")
        self.assertEqual(output["error_code"], "catalog_unavailable")
        self.assertEqual(output["matched_restaurants"], [])
        self.assertFalse(trace["success"])

    def test_fixture_is_json_and_has_tri_state_booking_fields(self):
        raw = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
        self.assertGreaterEqual(len(raw), 6)
        self.assertEqual({record["booking_channel"] for record in raw}, {"online", "offline", "unknown"})
        self.assertTrue(all(record["source"] == "fictional_demo_fixture" for record in raw))


if __name__ == "__main__":
    unittest.main()
