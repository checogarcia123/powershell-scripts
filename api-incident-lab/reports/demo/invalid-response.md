# Response could not be parsed

Mode: simulated
Scenario: invalid-response
UTC: 2026-10-07T01:29:37+00:00

HTTP success alone is insufficient: the response was not a JSON object.

## Recommended next steps

1. Inspect content type, proxy behavior, and the response format locally.
2. Preserve sanitized evidence; this tool does not write the raw response body.
3. Preserve the request ID, UTC time, and affected project for escalation.

## Incident handover

```text
Scenario: invalid-response (simulated)
Observed: HTTP 200; attempts=1; error_code=none; response_status=not received.
Interpretation: Response could not be parsed. HTTP success alone is insufficient: the response was not a JSON object.
Recovery decision: No automatic retry: investigate or correct the issue first.
Trace: request_id=req_demo_protocol; client_request_id=310effb0-2b41-4798-a45f-b1dd86ac74b8
Next: Inspect content type, proxy behavior, and the response format locally.
Business impact and customer scope: not established by this technical probe.
```

## Sanitized evidence

```json
{
  "schema_version": 1,
  "generated_at_utc": "2026-10-07T01:29:37+00:00",
  "mode": "simulated",
  "scenario": "invalid-response",
  "description": "A proxy or intermediary may return HTML. The tool flags a protocol issue without logging the raw body.",
  "diagnosis": {
    "category": "protocol",
    "title": "Response could not be parsed",
    "summary": "HTTP success alone is insufficient: the response was not a JSON object.",
    "retryable": false,
    "next_steps": [
      "Inspect content type, proxy behavior, and the response format locally.",
      "Preserve sanitized evidence; this tool does not write the raw response body.",
      "Preserve the request ID, UTC time, and affected project for escalation."
    ]
  },
  "observations": [
    {
      "attempt": 1,
      "http_status": 200,
      "client_request_id": "310effb0-2b41-4798-a45f-b1dd86ac74b8",
      "duration_ms": 0,
      "failure_kind": null,
      "error_code": null,
      "error_type": null,
      "error_message": null,
      "response_status": null,
      "incomplete_reason": null,
      "headers": {
        "x-request-id": "req_demo_protocol"
      },
      "valid_json": false
    }
  ],
  "retry_decisions": [],
  "stop_reason": "No automatic retry: investigate or correct the issue first.",
  "logging_policy": "No API credentials, input prompts, raw response bodies, or generated content are saved."
}
```
