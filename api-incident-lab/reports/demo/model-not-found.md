# Model or resource was not found

Mode: simulated
Scenario: model-not-found
UTC: 2026-10-07T01:29:37+00:00

The requested model or resource could not be resolved for this project.

## Recommended next steps

1. Check the exact resource or model identifier and API endpoint.
2. Confirm the project has access to the requested model; do not guess a replacement.
3. Preserve the request ID, UTC time, and affected project for escalation.

## Incident handover

```text
Scenario: model-not-found (simulated)
Observed: HTTP 404; attempts=1; error_code=model_not_found; response_status=not received.
Interpretation: Model or resource was not found. The requested model or resource could not be resolved for this project.
Recovery decision: No automatic retry: investigate or correct the issue first.
Trace: request_id=req_demo_model; client_request_id=e00952e3-6f2c-4ec1-b649-a88623e7301d
Next: Check the exact resource or model identifier and API endpoint.
Business impact and customer scope: not established by this technical probe.
```

## Sanitized evidence

```json
{
  "schema_version": 1,
  "generated_at_utc": "2026-10-07T01:29:37+00:00",
  "mode": "simulated",
  "scenario": "model-not-found",
  "description": "A model identifier may be incorrect or unavailable to the requesting project.",
  "diagnosis": {
    "category": "not_found",
    "title": "Model or resource was not found",
    "summary": "The requested model or resource could not be resolved for this project.",
    "retryable": false,
    "next_steps": [
      "Check the exact resource or model identifier and API endpoint.",
      "Confirm the project has access to the requested model; do not guess a replacement.",
      "Preserve the request ID, UTC time, and affected project for escalation."
    ]
  },
  "observations": [
    {
      "attempt": 1,
      "http_status": 404,
      "client_request_id": "e00952e3-6f2c-4ec1-b649-a88623e7301d",
      "duration_ms": 0,
      "failure_kind": null,
      "error_code": "model_not_found",
      "error_type": "invalid_request_error",
      "error_message": "The requested fixture model is not available to this project.",
      "response_status": null,
      "incomplete_reason": null,
      "headers": {
        "x-request-id": "req_demo_model"
      },
      "valid_json": true
    }
  ],
  "retry_decisions": [],
  "stop_reason": "No automatic retry: investigate or correct the issue first.",
  "logging_policy": "No API credentials, input prompts, raw response bodies, or generated content are saved."
}
```
