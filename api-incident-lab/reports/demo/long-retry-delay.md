# Temporary rate limit

Mode: simulated
Scenario: long-retry-delay
UTC: 2026-10-07T01:29:37+00:00

The error identifies temporary throttling. A bounded retry can be appropriate.

## Recommended next steps

1. Inspect request and token rate-limit headers and any Retry-After instruction.
2. Reduce request concurrency or token usage; use delayed, bounded retries.
3. If the required delay exceeds this tool's time budget, defer the request.

## Incident handover

```text
Scenario: long-retry-delay (simulated)
Observed: HTTP 429; attempts=1; error_code=slow_down; response_status=not received.
Interpretation: Temporary rate limit. The error identifies temporary throttling. A bounded retry can be appropriate.
Recovery decision: Required retry delay exceeds the remaining time budget; request deferred.
Trace: request_id=req_demo_defer; client_request_id=513de67a-080c-40f7-8c40-9d02521b9c09
Next: Inspect request and token rate-limit headers and any Retry-After instruction.
Business impact and customer scope: not established by this technical probe.
```

## Sanitized evidence

```json
{
  "schema_version": 1,
  "generated_at_utc": "2026-10-07T01:29:37+00:00",
  "mode": "simulated",
  "scenario": "long-retry-delay",
  "description": "A 120-second server delay exceeds this tool's 30-second budget. The request is deferred instead of retried early.",
  "diagnosis": {
    "category": "rate_limit",
    "title": "Temporary rate limit",
    "summary": "The error identifies temporary throttling. A bounded retry can be appropriate.",
    "retryable": true,
    "next_steps": [
      "Inspect request and token rate-limit headers and any Retry-After instruction.",
      "Reduce request concurrency or token usage; use delayed, bounded retries.",
      "If the required delay exceeds this tool's time budget, defer the request."
    ]
  },
  "observations": [
    {
      "attempt": 1,
      "http_status": 429,
      "client_request_id": "513de67a-080c-40f7-8c40-9d02521b9c09",
      "duration_ms": 0,
      "failure_kind": null,
      "error_code": "slow_down",
      "error_type": null,
      "error_message": "Reduce traffic and retry later.",
      "response_status": null,
      "incomplete_reason": null,
      "headers": {
        "x-request-id": "req_demo_defer",
        "retry-after": "120"
      },
      "valid_json": true
    }
  ],
  "retry_decisions": [
    {
      "after_attempt": 1,
      "delay_seconds": 120.0,
      "source": "Retry-After",
      "action": "defer"
    }
  ],
  "stop_reason": "Required retry delay exceeds the remaining time budget; request deferred.",
  "logging_policy": "No API credentials, input prompts, raw response bodies, or generated content are saved."
}
```
