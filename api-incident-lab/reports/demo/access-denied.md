# Access was denied

Mode: simulated
Scenario: access-denied
UTC: 2026-10-07T01:29:37+00:00

The request reached the service but access was denied; the body is needed to narrow the cause.

## Recommended next steps

1. Read the error code and check project permissions, policy, and supported region as applicable.
2. Verify the account and model access rather than automatically retrying.
3. Preserve the request ID, UTC time, and affected project for escalation.

## Incident handover

```text
Scenario: access-denied (simulated)
Observed: HTTP 403; attempts=1; error_code=unsupported_country_region_territory; response_status=not received.
Interpretation: Access was denied. The request reached the service but access was denied; the body is needed to narrow the cause.
Recovery decision: No automatic retry: investigate or correct the issue first.
Trace: request_id=req_demo_access; client_request_id=ae2fd432-a140-40fc-8f36-590e655aac76
Next: Read the error code and check project permissions, policy, and supported region as applicable.
Business impact and customer scope: not established by this technical probe.
```

## Sanitized evidence

```json
{
  "schema_version": 1,
  "generated_at_utc": "2026-10-07T01:29:37+00:00",
  "mode": "simulated",
  "scenario": "access-denied",
  "description": "Inspect access and region evidence rather than guessing the cause from the status alone.",
  "diagnosis": {
    "category": "access",
    "title": "Access was denied",
    "summary": "The request reached the service but access was denied; the body is needed to narrow the cause.",
    "retryable": false,
    "next_steps": [
      "Read the error code and check project permissions, policy, and supported region as applicable.",
      "Verify the account and model access rather than automatically retrying.",
      "Preserve the request ID, UTC time, and affected project for escalation."
    ]
  },
  "observations": [
    {
      "attempt": 1,
      "http_status": 403,
      "client_request_id": "ae2fd432-a140-40fc-8f36-590e655aac76",
      "duration_ms": 0,
      "failure_kind": null,
      "error_code": "unsupported_country_region_territory",
      "error_type": null,
      "error_message": "Access from this region is not supported.",
      "response_status": null,
      "incomplete_reason": null,
      "headers": {
        "x-request-id": "req_demo_access"
      },
      "valid_json": true
    }
  ],
  "retry_decisions": [],
  "stop_reason": "No automatic retry: investigate or correct the issue first.",
  "logging_policy": "No API credentials, input prompts, raw response bodies, or generated content are saved."
}
```
