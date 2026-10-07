"""Fixed-origin HTTP transport and an explicitly bounded recovery policy."""

from __future__ import annotations

import json
import random
import socket
import time
import urllib.error
import urllib.request
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import Callable, Protocol

from .core import diagnose, make_report, observe

API_URL = "https://api.openai.com/v1/responses"


@dataclass(frozen=True)
class HttpResult:
    status: int | None
    headers: dict[str, str]
    body: bytes = b""
    failure_kind: str | None = None


class Transport(Protocol):
    def __call__(self, payload: dict, client_request_id: str, timeout: float) -> HttpResult: ...


class NoRedirects(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class OpenAITransport:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.opener = urllib.request.build_opener(NoRedirects())

    def __call__(self, payload: dict, client_request_id: str, timeout: float) -> HttpResult:
        request = urllib.request.Request(
            API_URL, data=json.dumps(payload).encode("utf-8"), method="POST",
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json",
                     "X-Client-Request-Id": client_request_id},
        )
        try:
            with self.opener.open(request, timeout=timeout) as response:
                return HttpResult(response.status, dict(response.headers), response.read(1_048_576))
        except urllib.error.HTTPError as error:
            return HttpResult(error.code, dict(error.headers or {}), error.read(1_048_576))
        except (TimeoutError, socket.timeout):
            return HttpResult(None, {}, failure_kind="timeout")
        except urllib.error.URLError as error:
            fault = "timeout" if isinstance(error.reason, (TimeoutError, socket.timeout)) else "connection"
            return HttpResult(None, {}, failure_kind=fault)
        except OSError:
            return HttpResult(None, {}, failure_kind="connection")


def retry_after_seconds(value: str | None, now: datetime) -> float | None:
    if value is None:
        return None
    try:
        seconds = float(value)
        return seconds if seconds >= 0 and seconds < float("inf") else None
    except ValueError:
        try:
            when = parsedate_to_datetime(value)
            if when.tzinfo is None:
                when = when.replace(tzinfo=timezone.utc)
            return max(0.0, (when - now).total_seconds())
        except (ValueError, TypeError, OverflowError):
            return None


def run_probe(
    transport: Transport, *, model: str = "fixture-model", max_attempts: int = 1,
    timeout: float = 12, time_budget: float = 30, mode: str = "live",
    scenario: str = "live-probe", description: str = "One minimal Responses API request.",
    secrets: tuple[str, ...] = (), clock: Callable[[], float] = time.monotonic,
    sleep: Callable[[float], None] = time.sleep,
    utcnow: Callable[[], datetime] = lambda: datetime.now(timezone.utc),
    jitter: Callable[[], float] = random.random,
) -> dict:
    if not 1 <= max_attempts <= 3:
        raise ValueError("max_attempts must be between 1 and 3")
    if timeout <= 0 or time_budget <= 0:
        raise ValueError("timeout and time_budget must be positive")
    payload = {"model": model, "input": "Return the word OK.",
               "max_output_tokens": 128, "store": False, "stream": False}
    start = clock()
    observations = []
    decisions = []
    stop_reason = "Attempt limit reached."
    for attempt in range(1, max_attempts + 1):
        remaining = time_budget - (clock() - start)
        if remaining <= 0:
            stop_reason = "Total time budget reached; defer further requests."
            break
        request_id = str(uuid.uuid4())
        before = clock()
        result = transport(payload, request_id, min(timeout, remaining))
        item = observe(attempt=attempt, status=result.status, headers=result.headers,
                       body=result.body, client_request_id=request_id,
                       duration_ms=max(0, round((clock() - before) * 1000)),
                       failure_kind=result.failure_kind, secrets=secrets)
        observations.append(item)
        diagnosis = diagnose(item)
        if diagnosis.category == "completed":
            stop_reason = "Completed; no additional request needed."
            break
        if not diagnosis.retryable:
            stop_reason = "No automatic retry: investigate or correct the issue first."
            break
        if attempt == max_attempts:
            stop_reason = "Attempt limit reached; hand over for investigation."
            break
        advised = retry_after_seconds((item.headers or {}).get("retry-after"), utcnow())
        delay = advised if advised is not None else (2 ** (attempt - 1)) + jitter()
        remaining = time_budget - (clock() - start)
        if delay >= remaining:
            decisions.append({"after_attempt": attempt, "delay_seconds": delay,
                              "source": "Retry-After" if advised is not None else "backoff",
                              "action": "defer"})
            stop_reason = "Required retry delay exceeds the remaining time budget; request deferred."
            break
        decisions.append({"after_attempt": attempt, "delay_seconds": delay,
                          "source": "Retry-After" if advised is not None else "backoff",
                          "action": "retry"})
        sleep(delay)
    if not observations:
        raise RuntimeError("No request was attempted within the time budget")
    return make_report(mode=mode, scenario=scenario, description=description,
                       observations=observations, retries=decisions,
                       stop_reason=stop_reason, secrets=secrets)
