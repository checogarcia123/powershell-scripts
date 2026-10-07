# Architecture and diagnostic decisions

## Request to handover

1. The CLI selects a fixture or, explicitly, a live probe.
2. `run_probe()` builds a minimal Responses payload and creates a client request ID for each attempt.
3. The transport returns status, headers and bytes, or a transport fault. Live mode uses the fixed `https://api.openai.com/v1/responses` endpoint and blocks redirects.
4. `observe()` extracts only the report fields. Raw request input and generated response content are not written to disk.
5. `diagnose()` distinguishes a completed response from configuration errors, billing constraints, temporary throttling, server failures and uncertain transport outcomes.
6. Recovery either stops, defers, or waits before another permitted attempt. JSON and Markdown reports include every recorded observation.

## Recovery policy

| Evidence | Decision | Reason |
| --- | --- | --- |
| 401 / 403 / 404 / invalid parameters | Stop | Repeating unchanged credentials, permissions or payload is unlikely to repair configuration |
| 429 plus quota or spending code | Stop | An account limit requires action; a delay header cannot override this |
| 429 plus recognized temporary rate code | Retry within chosen bounds | Respect server delay and reduce traffic |
| 429 with unrecognized or missing code/type | Stop for investigation | HTTP status alone does not distinguish all limits |
| 500 / 502 / 503 / 504 | Retry within chosen bounds | Returned server/gateway failure may be transient; POST duplication remains a consideration |
| Timeout or connection fault | Stop; outcome unknown | A request might have completed without the client receiving its response |
| 2xx with completed response state | Stop successfully | Transport status and response state agree |
| 2xx with incomplete / failed / pending state | Investigate existing response | HTTP success does not establish application completion |
| Non-JSON success response | Stop for protocol investigation | A proxy or unexpected format may have intervened |

Live mode defaults to one attempt. The caller can explicitly allow up to three. `Retry-After` accepts a numeric delay or HTTP date. Without a valid instruction, exponential backoff with jitter is used. A delay that exceeds the remaining budget is deferred, not shortened. A fake transport and clock make fixture tests fast and deterministic.

## Test evidence

The 22 tests cover: same-status/different-cause classification; billing codes; unknown 429 behavior; incomplete and pending responses; malformed JSON; secret/header filtering; retry delay and time budget; attempt caps; timeout replay prevention; HTTP date parsing; all fixtures without network access; the fixed live URL and minimal payload; redirect prevention; output files; and missing setup inputs.

The transport test uses a mocked HTTP opener. It confirms request construction without sending a live request. It does not validate account access, a real model's output, network connectivity, streaming, or current server availability.

## Extensions to build yourself

Keep each change small and explainable. For example, add a fixture for an unrecognized 429 code and verify that it stops for investigation. Add a test before changing any recovery policy. Production extensions would need model-specific behavior, richer observability, privacy review, integration-specific retry semantics and monitoring.
