"""Diagnosis and reporting. No API keys, prompts, or generated output are logged."""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Iterable


SAFE_HEADERS = frozenset({
    "x-request-id", "retry-after", "x-ratelimit-limit-requests",
    "x-ratelimit-limit-tokens", "x-ratelimit-remaining-requests",
    "x-ratelimit-remaining-tokens", "x-ratelimit-reset-requests",
    "x-ratelimit-reset-tokens",
})
QUOTA_CODES = frozenset({
    "insufficient_quota", "credit_balance_exhausted",
    "organization_usage_limit_exceeded", "organization_spend_limit_exceeded",
    "project_spend_limit_exceeded", "billing_hard_limit_reached", "quota_exceeded",
})
RATE_CODES = frozenset({"rate_limit_exceeded", "slow_down", "requests", "tokens"})


def redact(value: Any, secrets: Iterable[str] = ()) -> Any:
    """Remove known credentials and common key/token forms recursively."""
    if isinstance(value, dict):
        return {str(key): redact(item, secrets) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [redact(item, secrets) for item in value]
    if not isinstance(value, str):
        return value
    for secret in secrets:
        if secret:
            value = value.replace(secret, "[REDACTED]")
    value = re.sub(r"\bsk-[A-Za-z0-9_-]+", "[REDACTED]", value)
    value = re.sub(r"(?i)\bBearer\s+[^\s,;\"']+", "Bearer [REDACTED]", value)
    return value


@dataclass(frozen=True)
class Observation:
    attempt: int
    http_status: int | None
    client_request_id: str
    duration_ms: int = 0
    failure_kind: str | None = None
    error_code: str | None = None
    error_type: str | None = None
    error_message: str | None = None
    response_status: str | None = None
    incomplete_reason: str | None = None
    headers: dict[str, str] | None = None
    valid_json: bool = True


@dataclass(frozen=True)
class Diagnosis:
    category: str
    title: str
    summary: str
    retryable: bool
    next_steps: tuple[str, ...]


def observe(
    *, attempt: int, status: int | None, headers: dict[str, str], body: bytes,
    client_request_id: str, duration_ms: int = 0,
    failure_kind: str | None = None, secrets: Iterable[str] = (),
) -> Observation:
    filtered = {key.lower(): str(value)[:512] for key, value in headers.items()
                if key.lower() in SAFE_HEADERS}
    valid_json = True
    data: dict[str, Any] = {}
    if failure_kind is None:
        try:
            parsed = json.loads(body.decode("utf-8"))
            if not isinstance(parsed, dict):
                raise ValueError("Response envelope must be an object")
            data = parsed
        except (ValueError, UnicodeDecodeError):
            valid_json = False
    error = data.get("error")
    error = error if isinstance(error, dict) else {}
    incomplete = data.get("incomplete_details")
    incomplete = incomplete if isinstance(incomplete, dict) else {}

    def field(value: Any, limit: int = 512) -> str | None:
        return redact(value[:limit], secrets) if isinstance(value, str) else None

    return Observation(
        attempt=attempt, http_status=status, client_request_id=client_request_id,
        duration_ms=duration_ms, failure_kind=failure_kind,
        error_code=field(error.get("code")), error_type=field(error.get("type")),
        error_message=field(error.get("message"), 1000),
        response_status=field(data.get("status")),
        incomplete_reason=field(incomplete.get("reason")),
        headers=redact(filtered, secrets), valid_json=valid_json,
    )


def diagnose(item: Observation) -> Diagnosis:
    status = item.http_status
    code = (item.error_code or "").lower()
    kind = (item.error_type or "").lower()
    trace = "Preserve the request ID, UTC time, and affected project for escalation."
    if item.failure_kind in {"timeout", "connection"}:
        return Diagnosis("transport_unknown", "Request outcome is unknown",
            "The client did not receive a usable response. A POST may already have been processed.", False,
            ("Check connectivity and the timeout configuration; do not assume the server rejected the request.",
             "Use the client request ID and any server-side evidence to investigate before manually repeating the request.",
             "Explain the unknown outcome and possible duplicate work or charges in the handover."))
    if status == 401:
        return Diagnosis("authentication", "Authentication failed",
            "The service rejected authentication. Repeating the same credentials will not resolve it.", False,
            ("Confirm the key is present in the local environment and belongs to the intended project.",
             "Check key validity, organization membership, and relevant IP restrictions without sharing the key.", trace))
    if status == 403:
        return Diagnosis("access", "Access was denied",
            "The request reached the service but access was denied; the body is needed to narrow the cause.", False,
            ("Read the error code and check project permissions, policy, and supported region as applicable.",
             "Verify the account and model access rather than automatically retrying.", trace))
    if status == 404:
        return Diagnosis("not_found", "Model or resource was not found",
            "The requested model or resource could not be resolved for this project.", False,
            ("Check the exact resource or model identifier and API endpoint.",
             "Confirm the project has access to the requested model; do not guess a replacement.", trace))
    if status in {400, 422}:
        return Diagnosis("invalid_request", "The request needs correction",
            "The service rejected the request parameters or payload.", False,
            ("Use the returned error details to identify the invalid field.",
             "Compare the payload with the Responses API schema and the selected model's supported parameters.",
             "Correct the request before running another attempt."))
    if status == 429:
        if code in QUOTA_CODES or kind in QUOTA_CODES:
            return Diagnosis("quota_or_billing", "Usage or spending limit reached",
                "This is a quota, credit, or spending constraint. Waiting briefly will not repair it.", False,
                ("Check credits, usage, and project or organization limits with the account owner.",
                 "Resolve the returned limit before making another request, even if Retry-After is present.", trace))
        if code in RATE_CODES or kind in RATE_CODES:
            return Diagnosis("rate_limit", "Temporary rate limit",
                "The error identifies temporary throttling. A bounded retry can be appropriate.", True,
                ("Inspect request and token rate-limit headers and any Retry-After instruction.",
                 "Reduce request concurrency or token usage; use delayed, bounded retries.",
                 "If the required delay exceeds this tool's time budget, defer the request."))
        return Diagnosis("unclassified_429", "429 requires further investigation",
            "The response does not identify a recognized temporary limit. This tool will not guess that retrying is safe.", False,
            ("Read the error body and check usage, billing, and rate-limit evidence.",
             "Determine whether the limit is temporary before selecting a recovery action.", trace))
    if status in {500, 502, 503, 504}:
        return Diagnosis("server_temporary", "Temporary server-side failure",
            "A server or gateway error was returned. This lab permits a bounded retry, with possible duplicate work considered.", True,
            ("Record the request ID and check service status if the issue persists.",
             "Respect Retry-After and the attempt/time budget; avoid unlimited retries.",
             "Consider whether repeating a POST could duplicate work before enabling retries."))
    if status is not None and 200 <= status < 300:
        if not item.valid_json:
            return Diagnosis("protocol", "Response could not be parsed",
                "HTTP success alone is insufficient: the response was not a JSON object.", False,
                ("Inspect content type, proxy behavior, and the response format locally.",
                 "Preserve sanitized evidence; this tool does not write the raw response body.", trace))
        if item.response_status == "completed":
            return Diagnosis("completed", "Response completed",
                "The response reports a completed operation. The lab does not assess generated content quality.", False,
                ("Record the completed response and request ID.",
                 "Validate the result against the application's requirements before closing a real incident."))
        if item.response_status == "incomplete":
            return Diagnosis("incomplete", "Response is incomplete",
                "The request returned HTTP success but the response reports incomplete generation.", False,
                ("Inspect incomplete_details.reason; a token limit may require a different output budget.",
                 "Explain the incomplete result and decide whether a revised request is appropriate.",
                 "Do not report HTTP 200 alone as a fully successful result."))
        if item.response_status in {"queued", "in_progress"}:
            return Diagnosis("pending", "Response is still pending",
                "The response has not completed. Replaying the creation request is not a completion check.", False,
                ("Retrieve or monitor the existing response using the appropriate API workflow.",
                 "Keep the incident open until the response reaches a terminal state."))
        return Diagnosis("response_failed", "Response did not confirm completion",
            "The response is failed or lacks the expected completion state. This tool will not automatically replay it.", False,
            ("Inspect the response status and structured error details.",
             "Investigate the existing operation before deciding whether to create a new response.", trace))
    return Diagnosis("unexpected_http", "Unexpected HTTP response",
        "The status does not match a supported recovery path. No automatic retry was attempted.", False,
        ("Check endpoint, response headers, and any redirect or intermediary behavior.", trace))


def make_report(*, mode: str, scenario: str, description: str,
                observations: list[Observation], retries: list[dict[str, Any]],
                stop_reason: str, secrets: Iterable[str] = ()) -> dict[str, Any]:
    final = diagnose(observations[-1])
    report = {
        "schema_version": 1,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "mode": mode, "scenario": scenario, "description": description,
        "diagnosis": asdict(final),
        "observations": [asdict(item) for item in observations],
        "retry_decisions": retries,
        "stop_reason": stop_reason,
        "logging_policy": "No API credentials, input prompts, raw response bodies, or generated content are saved.",
    }
    return redact(report, secrets)


def handover(report: dict[str, Any]) -> str:
    final = report["observations"][-1]
    diagnosis = report["diagnosis"]
    request_id = (final.get("headers") or {}).get("x-request-id", "not received")
    return "\n".join([
        f"Scenario: {report['scenario']} ({report['mode']})",
        f"Observed: HTTP {final['http_status'] if final['http_status'] is not None else 'not received'}; "
        f"attempts={len(report['observations'])}; error_code={final.get('error_code') or 'none'}; "
        f"response_status={final.get('response_status') or 'not received'}.",
        f"Interpretation: {diagnosis['title']}. {diagnosis['summary']}",
        f"Recovery decision: {report['stop_reason']}",
        f"Trace: request_id={request_id}; client_request_id={final['client_request_id']}",
        f"Next: {diagnosis['next_steps'][0]}",
        "Business impact and customer scope: not established by this technical probe.",
    ])


def markdown_report(report: dict[str, Any]) -> str:
    diagnosis = report["diagnosis"]
    lines = [f"# {diagnosis['title']}", "", f"Mode: {report['mode']}",
             f"Scenario: {report['scenario']}", f"UTC: {report['generated_at_utc']}", "",
             diagnosis["summary"], "", "## Recommended next steps", ""]
    lines.extend(f"{index}. {step}" for index, step in enumerate(diagnosis["next_steps"], 1))
    lines.extend(["", "## Incident handover", "", "```text", handover(report), "```", "",
                  "## Sanitized evidence", "", "```json",
                  json.dumps(report, indent=2), "```", ""])
    return "\n".join(lines)
