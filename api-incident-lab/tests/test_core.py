import json
import unittest

from api_incident_lab.core import Observation, diagnose, observe, redact


class DiagnosisTests(unittest.TestCase):
    def test_billing_codes_never_retry_even_with_retry_after(self):
        for code in ("insufficient_quota", "credit_balance_exhausted", "project_spend_limit_exceeded",
                     "organization_usage_limit_exceeded", "organization_spend_limit_exceeded"):
            with self.subTest(code=code):
                result = diagnose(Observation(1, 429, "client", error_code=code, headers={"retry-after": "1"}))
                self.assertEqual(result.category, "quota_or_billing")
                self.assertFalse(result.retryable)

    def test_same_429_status_has_different_recovery_paths(self):
        temporary = diagnose(Observation(1, 429, "client", error_code="rate_limit_exceeded"))
        unknown = diagnose(Observation(1, 429, "client", error_code="unrecognized"))
        self.assertTrue(temporary.retryable)
        self.assertFalse(unknown.retryable)
        self.assertEqual(unknown.category, "unclassified_429")

    def test_configuration_failures_require_correction(self):
        for status, category in ((400, "invalid_request"), (401, "authentication"),
                                 (403, "access"), (404, "not_found")):
            with self.subTest(status=status):
                result = diagnose(Observation(1, status, "client"))
                self.assertEqual(result.category, category)
                self.assertFalse(result.retryable)

    def test_success_requires_completed_response_state(self):
        cases = (("completed", "completed"), ("incomplete", "incomplete"),
                 ("failed", "response_failed"), ("in_progress", "pending"), (None, "response_failed"))
        for state, expected in cases:
            with self.subTest(state=state):
                result = diagnose(Observation(1, 200, "client", response_status=state))
                self.assertEqual(result.category, expected)
                self.assertFalse(result.retryable)

    def test_transport_faults_do_not_replay_posts(self):
        for fault in ("timeout", "connection"):
            result = diagnose(Observation(1, None, "client", failure_kind=fault))
            self.assertEqual(result.category, "transport_unknown")
            self.assertFalse(result.retryable)

    def test_invalid_json_and_array_envelopes_are_protocol_issues(self):
        for body in (b"<html>error</html>", b"[]", b"\xff"):
            item = observe(attempt=1, status=200, headers={}, body=body, client_request_id="client")
            self.assertEqual(diagnose(item).category, "protocol")

    def test_credentials_and_unapproved_headers_are_not_recorded(self):
        key = "unusually-formatted-secret"
        body = json.dumps({"error": {"message": f"Bad key {key}; sk-demo-123; Bearer other-token"},
                           "input": "private prompt", "output": "private answer"}).encode()
        item = observe(attempt=1, status=401, body=body, client_request_id="client", secrets=(key,),
                       headers={"Authorization": f"Bearer {key}", "Set-Cookie": "secret",
                                "X-Request-ID": "req_example"})
        saved = repr(item)
        for secret in (key, "sk-demo-123", "other-token", "private prompt", "private answer", "Set-Cookie"):
            self.assertNotIn(secret, saved)
        self.assertEqual(item.headers, {"x-request-id": "req_example"})

    def test_nested_redaction_covers_known_secrets(self):
        result = redact({"items": ["abc-secret", {"message": "Bearer token-123"}]}, ("abc-secret",))
        self.assertEqual(result["items"][0], "[REDACTED]")
        self.assertEqual(result["items"][1]["message"], "Bearer [REDACTED]")


if __name__ == "__main__":
    unittest.main()
