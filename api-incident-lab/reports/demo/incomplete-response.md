# Response is incomplete

Mode: simulated
Scenario: incomplete-response
UTC: 2026-10-07T01:29:37+00:00

The request returned HTTP success but the response reports incomplete generation.

## Recommended next steps

1. Inspect incomplete_details.reason; a token limit may require a different output budget.
2. Explain the incomplete result and decide whether a revised request is appropriate.
3. Do not report HTTP 200 alone as a fully successful result.

## Incident handover

```text
Scenario: incomplete-response (simulated)
Observed: HTTP 200; attempts=1; error_code=none; response_status=incomplete.
Interpretation: Response is incomplete. The request returned HTTP success but the response reports incomplete generation.
Recovery decision: No automatic retry: investigate or correct the issue first.
Trace: request_id=req_demo_incomplete; client_request_id=5d9e7e7b-2fa0-47a5-8f06-8740d4c1fab3
Next: Inspect incomplete_details.reason; a token limit may require a different output budget.
Business impact and customer scope: not established by this technical probe.
```

## Sanitized evidence

```json
{
  "schema_version": 1,
  "generated_at_utc": "2026-10-07T01:29:37+00:00",
  "mode": "simulated",
  "scenario": "incomplete-response",
  "description": "HTTP 200 is not enough to close the incident when the response state is incomplete.",
  "diagnosis": {
    "category": "incomplete",
    "title": "Response is incomplete",
    "summary": "The request returned HTTP success but the response reports incomplete generation.",
    "retryable": false,
    "next_steps": [
      "Inspect incomplete_details.reason; a token limit may require a different output budget.",
      "Explain the incomplete result and decide whether a revised request is appropriate.",
      "Do not report HTTP 200 alone as a fully successful result."
    ]
  },
  "observations": [
    {
      "attempt": 1,
      "http_status": 200,
      "client_request_id": "5d9e7e7b-2fa0-47a5-8f06-8740d4c1fab3",
      "duration_ms": 0,
      "failure_kind": null,
      "error_code": null,
      "error_type": null,
      "error_message": null,
      "response_status": "incomplete",
      "incomplete_reason": "max_output_tokens",
      "headers": {
        "x-request-id": "req_demo_incomplete"
      },
      "valid_json": true
    }
  ],
  "retry_decisions": [],
  "stop_reason": "No automatic retry: investigate or correct the issue first.",
  "logging_policy": "No API credentials, input prompts, raw response bodies, or generated content are saved."
}
```
