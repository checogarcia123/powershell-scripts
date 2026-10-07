"""Deterministic scenarios: no network requests, API key, charges, or real waits."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from .client import HttpResult, run_probe


def load_scenarios() -> list[dict]:
    path = Path(__file__).parent / "data" / "scenarios.json"
    return json.loads(path.read_text(encoding="utf-8"))


class FixtureTransport:
    def __init__(self, responses: list[dict]):
        self.responses = responses
        self.calls = 0

    def __call__(self, payload: dict, client_request_id: str, timeout: float) -> HttpResult:
        response = self.responses[min(self.calls, len(self.responses) - 1)]
        self.calls += 1
        body = response.get("body", {})
        encoded = body.encode("utf-8") if isinstance(body, str) else json.dumps(body).encode("utf-8")
        return HttpResult(response.get("status"), response.get("headers", {}), encoded,
                          response.get("failure_kind"))


class SimulatedClock:
    def __init__(self):
        self.seconds = 0.0

    def now(self) -> float:
        return self.seconds

    def advance(self, seconds: float) -> None:
        self.seconds += seconds


def demo(scenario: dict) -> dict:
    clock = SimulatedClock()
    return run_probe(FixtureTransport(scenario["responses"]),
                     max_attempts=scenario.get("max_attempts", 3), mode="simulated",
                     scenario=scenario["id"], description=scenario["description"],
                     clock=clock.now, sleep=clock.advance,
                     utcnow=lambda: datetime(2026, 10, 7, tzinfo=timezone.utc),
                     jitter=lambda: 0.0)
