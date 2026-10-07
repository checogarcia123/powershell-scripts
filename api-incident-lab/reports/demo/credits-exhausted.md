# Usage or spending limit reached

Mode: simulated
Scenario: credits-exhausted
UTC: 2026-10-07T01:29:37+00:00

This is a quota, credit, or spending constraint. Waiting briefly will not repair it.

## Recommended next steps

1. Check credits, usage, and project or organization limits with the account owner.
2. Resolve the returned limit before making another request, even if Retry-After is present.
3. Preserve the request ID, UTC time, and affected project for escalation.

## Incident handover

```text
Scenario: credits-exhausted (simulated)
Observed: HTTP 429; attempts=1; error_code=credit_balance_exhausted; response_status=not received.
Interpretation: Usage or spending limit reached. This is a quota, credit, or spending constraint. Waiting briefly will not repair it.
Recovery decision: No automatic retry: investigate or correct the issue first.
Trace: request_id=req_demo_credit; client_request_id=84ad1504-df2d-4796-8be5-823208679c58
Next: Check credits, usage, and project or organization limits with the account owner.
Business impact and customer scope: not established by this technical probe.
```

## Sanitized evidence

```json
{
  "schema_version": 1,
  "generated_at_utc": "2026-10-07T01:29:37+00:00",
  "mode": "simulated",
  "scenario": "credits-exhausted",
  "description": "The same HTTP status has a different recovery path: replenishing credits or resolving billing. Retry-After does not override the error code.",
  "diagnosis": {
    "category": "quota_or_billing",
    "title": "Usage or spending limit reached",
    "summary": "This is a quota, credit, or spending constraint. Waiting briefly will not repair it.",
    "retryable": false,
    "next_steps": [
      "Check credits, usage, and project or organization limits with the account owner.",
      "Resolve the returned limit before making another request, even if Retry-After is present.",
      "Preserve the request ID, UTC time, and affected project for escalation."
    ]
  },
  "observations": [
    {
      "attempt": 1,
      "http_status": 429,
      "client_request_id": "84ad1504-df2d-4796-8be5-823208679c58",
      "duration_ms": 0,
      "failure_kind": null,
      "error_code": "credit_balance_exhausted",
      "error_type": "insufficient_quota",
      "error_message": "Credit balance exhausted.",
      "response_status": null,
      "incomplete_reason": null,
      "headers": {
        "x-request-id": "req_demo_credit",
        "retry-after": "1"
      },
      "valid_json": true
    }
  ],
  "retry_decisions": [],
  "stop_reason": "No automatic retry: investigate or correct the issue first.",
  "logging_policy": "No API credentials, input prompts, raw response bodies, or generated content are saved."
}
```
