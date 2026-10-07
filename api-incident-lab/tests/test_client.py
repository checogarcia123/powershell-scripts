import json
import unittest
from datetime import datetime, timezone
from unittest.mock import patch

from api_incident_lab.client import API_URL, HttpResult, NoRedirects, OpenAITransport, retry_after_seconds, run_probe
from api_incident_lab.fixtures import FixtureTransport, SimulatedClock, demo, load_scenarios


class RecoveryTests(unittest.TestCase):
    def run_case(self, responses, **kwargs):
        transport = FixtureTransport(responses)
        clock = SimulatedClock()
        result = run_probe(transport, max_attempts=3, mode="test", clock=clock.now,
                           sleep=clock.advance, jitter=lambda: 0, **kwargs)
        return result, transport, clock

    def test_retry_after_is_respected_before_recovery(self):
        report, transport, clock = self.run_case([
            {"status": 429, "headers": {"Retry-After": "4"}, "body": {"error": {"code": "rate_limit_exceeded"}}},
            {"status": 200, "body": {"status": "completed"}},
        ])
        self.assertEqual(transport.calls, 2)
        self.assertEqual(clock.seconds, 4)
        self.assertEqual(report["diagnosis"]["category"], "completed")
        self.assertEqual(report["retry_decisions"][0]["source"], "Retry-After")

    def test_long_retry_after_is_deferred_not_clamped(self):
        report, transport, clock = self.run_case([
            {"status": 429, "headers": {"retry-after": "120"}, "body": {"error": {"code": "slow_down"}}}
        ])
        self.assertEqual(transport.calls, 1)
        self.assertEqual(clock.seconds, 0)
        self.assertEqual(report["retry_decisions"][0]["action"], "defer")
        self.assertIn("exceeds", report["stop_reason"])

    def test_billing_error_stops_despite_retry_after(self):
        report, transport, clock = self.run_case([
            {"status": 429, "headers": {"retry-after": "1"}, "body": {"error": {"code": "credit_balance_exhausted"}}}
        ])
        self.assertEqual(transport.calls, 1)
        self.assertEqual(clock.seconds, 0)
        self.assertEqual(report["retry_decisions"], [])

    def test_server_retry_attempts_are_capped(self):
        report, transport, clock = self.run_case([{"status": 500, "body": {"error": {"type": "server_error"}}}])
        self.assertEqual(transport.calls, 3)
        self.assertEqual(clock.seconds, 3)
        self.assertIn("Attempt limit", report["stop_reason"])

    def test_transport_failure_stops_with_trace_id(self):
        report, transport, clock = self.run_case([{"failure_kind": "timeout"}])
        self.assertEqual(transport.calls, 1)
        self.assertEqual(clock.seconds, 0)
        self.assertIsNotNone(report["observations"][0]["client_request_id"])

    def test_live_default_is_one_attempt(self):
        transport = FixtureTransport([{"status": 503}])
        report = run_probe(transport)
        self.assertEqual(transport.calls, 1)
        self.assertEqual(report["retry_decisions"], [])

    def test_retry_after_accepts_http_date_and_rejects_invalid_values(self):
        now = datetime(2026, 10, 7, tzinfo=timezone.utc)
        self.assertEqual(retry_after_seconds("Wed, 07 Oct 2026 00:00:05 GMT", now), 5)
        for value in (None, "garbage", "-2", "nan", "inf"):
            self.assertIsNone(retry_after_seconds(value, now))

    def test_each_fixture_runs_without_network_and_matches_expected_outcome(self):
        outcomes = {
            "completed": ("completed", 1), "authentication": ("authentication", 1),
            "access-denied": ("access", 1), "model-not-found": ("not_found", 1),
            "invalid-request": ("invalid_request", 1), "rate-limit-recovery": ("completed", 2),
            "credits-exhausted": ("quota_or_billing", 1), "project-spend-limit": ("quota_or_billing", 1),
            "long-retry-delay": ("rate_limit", 1), "overload-recovery": ("completed", 2),
            "persistent-server-error": ("server_temporary", 3), "timeout": ("transport_unknown", 1),
            "connection-failure": ("transport_unknown", 1), "incomplete-response": ("incomplete", 1),
            "invalid-response": ("protocol", 1),
        }
        with patch("urllib.request.OpenerDirector.open", side_effect=AssertionError("Network forbidden")):
            for case in load_scenarios():
                with self.subTest(case=case["id"]):
                    report = demo(case)
                    self.assertEqual((report["diagnosis"]["category"], len(report["observations"])), outcomes[case["id"]])

    def test_invalid_recovery_limits_are_rejected(self):
        transport = FixtureTransport([{"status": 200}])
        for kwargs in ({"max_attempts": 0}, {"max_attempts": 4}, {"timeout": 0}, {"time_budget": -1}):
            with self.assertRaises(ValueError):
                run_probe(transport, **kwargs)


class TransportTests(unittest.TestCase):
    def test_fixed_origin_minimal_payload_and_private_key_header(self):
        captured = {}

        class Response:
            status = 200
            headers = {"x-request-id": "req_transport"}

            def __enter__(self): return self
            def __exit__(self, *args): return False
            def read(self, limit): return b'{"status":"completed"}'

        class Opener:
            def open(self, request, timeout):
                captured["url"] = request.full_url
                captured["headers"] = dict(request.header_items())
                captured["payload"] = json.loads(request.data)
                return Response()

        transport = OpenAITransport("a-private-key")
        transport.opener = Opener()
        report = run_probe(transport, model="available-test-model", secrets=("a-private-key",))
        self.assertEqual(captured["url"], API_URL)
        self.assertFalse(captured["payload"]["store"])
        self.assertFalse(captured["payload"]["stream"])
        self.assertEqual(captured["payload"]["model"], "available-test-model")
        self.assertNotIn("a-private-key", json.dumps(report))
        self.assertIn("X-client-request-id", captured["headers"])

    def test_redirects_do_not_forward_credentials(self):
        self.assertIsNone(NoRedirects().redirect_request(None, None, 302, "redirect", {}, "https://other.invalid"))


if __name__ == "__main__":
    unittest.main()
