# Authentication failed

Mode: simulated
Scenario: authentication
UTC: 2026-10-07T01:29:37+00:00

The service rejected authentication. Repeating the same credentials will not resolve it.

## Recommended next steps

1. Confirm the key is present in the local environment and belongs to the intended project.
2. Check key validity, organization membership, and relevant IP restrictions without sharing the key.
3. Preserve the request ID, UTC time, and affected project for escalation.

## Incident handover

```text
Scenario: authentication (simulated)
Observed: HTTP 401; attempts=1; error_code=invalid_api_key; response_status=not received.
Interpretation: Authentication failed. The service rejected authentication. Repeating the same credentials will not resolve it.
Recovery decision: No automatic retry: investigate or correct the issue first.
Trace: request_id=req_demo_auth; client_request_id=8e883e23-f123-492e-9e03-8340ae046ffe
Next: Confirm the key is present in the local environment and belongs to the intended project.
Business impact and customer scope: not established by this technical probe.
```

## Sanitized evidence

```json
{
  "schema_version": 1,
  "generated_at_utc": "2026-10-07T01:29:37+00:00",
  "mode": "simulated",
  "scenario": "authentication",
  "description": "A key rejected by the service is a configuration issue, not a retry problem.",
  "diagnosis": {
    "category": "authentication",
    "title": "Authentication failed",
    "summary": "The service rejected authentication. Repeating the same credentials will not resolve it.",
    "retryable": false,
    "next_steps": [
      "Confirm the key is present in the local environment and belongs to the intended project.",
      "Check key validity, organization membership, and relevant IP restrictions without sharing the key.",
      "Preserve the request ID, UTC time, and affected project for escalation."
    ]
  },
  "observations": [
    {
      "attempt": 1,
      "http_status": 401,
      "client_request_id": "8e883e23-f123-492e-9e03-8340ae046ffe",
      "duration_ms": 0,
      "failure_kind": null,
      "error_code": "invalid_api_key",
      "error_type": "invalid_request_error",
      "error_message": "Incorrect API key provided: [REDACTED]",
      "response_status": null,
      "incomplete_reason": null,
      "headers": {
        "x-request-id": "req_demo_auth"
      },
      "valid_json": true
    }
  ],
  "retry_decisions": [],
  "stop_reason": "No automatic retry: investigate or correct the issue first.",
  "logging_policy": "No API credentials, input prompts, raw response bodies, or generated content are saved."
}
```
