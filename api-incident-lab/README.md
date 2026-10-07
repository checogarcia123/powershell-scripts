# API Incident Lab

A small Python troubleshooting project for an AI Support Engineer application. It diagnoses simulated API failures, records sanitized evidence, applies a bounded recovery policy, and writes JSON and Markdown incident handovers. An optional live command sends a minimal OpenAI Responses API request from your own API account.

**Project status:** AI-assisted learning project in progress for Sergio Garcia. Automated offline validation is complete; Sergio's personal code walkthrough and hands-on review are next. A real API call has not been performed, and this project does not establish prior professional Python or OpenAI API experience.

## Start on Windows

1. Extract the lab ZIP or clone the repository. Open its `api-incident-lab` folder in File Explorer.
2. In the address bar, type `powershell` and press Enter. The terminal opens in that folder.
3. Run these commands. If your installation uses `python` rather than `py -3`, substitute `python` in every command.

```powershell
py -3 --version
py -3 -m unittest discover -s tests -v
py -3 -m api_incident_lab list
py -3 -m api_incident_lab demo --all
```

Requires Python 3.10 or later. Uses only the standard library: no pip packages, API key, or network are needed for the offline lab. If Python is unavailable, use the installer instructions at https://www.python.org/downloads/windows/ and reopen the terminal.

On macOS or Linux, use `python3` instead of `py -3`.

Expected results: **22 passing tests**, then **15 scenario summaries**. Reports appear in `reports/demo/`; open a `.md` file in a text editor, or inspect a JSON report:

```powershell
Get-Content .\reports\demo\rate-limit-recovery.md
Get-Content .\reports\demo\credits-exhausted.json
```

## Three useful demonstrations

```powershell
py -3 -m api_incident_lab demo --scenario rate-limit-recovery
py -3 -m api_incident_lab demo --scenario credits-exhausted
py -3 -m api_incident_lab demo --scenario timeout
```

- A temporary 429 waits for the supplied delay and then succeeds. Fixture mode advances a simulated clock; it does not actually sleep.
- A credit-related 429 stops, even with a `Retry-After` header. Account or billing action is required.
- A timeout records an unknown request outcome and avoids automatic replay of a POST.

The other scenarios cover authentication, access, model identifiers, invalid parameters, spending limits, long delays, server failures, incomplete generation, and malformed responses. Synthetic request IDs begin with `req_demo_`; they are not evidence of real API activity.

## Optional live mode

Only do this when you want to test your own API account. API access and billing are separate from a ChatGPT subscription. A live request can incur API charges. Choose a model actually available to your API project; `YOUR_AVAILABLE_MODEL` below is a placeholder, not a model ID.

```powershell
py -3 -m api_incident_lab live --model YOUR_AVAILABLE_MODEL
```

If `OPENAI_API_KEY` is not already set locally, an interactive terminal asks for it with hidden input. The tool does not save the key. Never paste it into chat, a screenshot, a Git repository, or a command-line argument. Do not put it into the portfolio website.

Default: one request, 12-second per-request timeout, 30-second recovery budget. You may explicitly choose up to three attempts:

```powershell
py -3 -m api_incident_lab live --model YOUR_AVAILABLE_MODEL --max-attempts 2
```

Retries of POST requests can duplicate work or charges. The tool does not promise idempotent execution. It will not automatically repeat a timeout or a generic connection failure. Live reports go to `reports/live/`. Exit code 0 means the response reports completion, 1 means an issue was diagnosed, and 2 means setup or command arguments need correction.

## Implementation

| File | Responsibility |
| --- | --- |
| `api_incident_lab/core.py` | Evidence extraction, error classification, credential redaction, report and handover formatting |
| `api_incident_lab/client.py` | Fixed API endpoint, redirect blocking, timeout handling, bounded retries and delay parsing |
| `api_incident_lab/fixtures.py` | Offline transport and simulated clock |
| `api_incident_lab/data/scenarios.json` | Fifteen reproducible synthetic incidents |
| `api_incident_lab/cli.py` | Offline and live commands, report files, local credential entry |
| `tests/` | Classification, recovery, redaction, transport and CLI checks |

Read `docs/architecture.md` for the decision flow and `docs/practice-tasks.md` for exercises. Explain each decision in your own words before presenting the project in an interview.

## What the tool does and does not establish

The classifier uses HTTP status, structured error codes, and response state. The report separates observations from interpretation. It records approved trace/rate headers and client-generated request IDs. It excludes the Authorization header, input prompt, raw response body, and generated answer. Known credentials and common API-key/token patterns are redacted from captured error messages; this is not a general-purpose personal-data sanitizer. Review any live report before sharing it.

The tool diagnoses a narrow Responses API probe. It does not measure customer impact, monitor a production service, test streaming or tool calls, implement concurrency control, or verify generated content quality. Socket timeouts and retry budgets limit waiting but are not a guaranteed hard process deadline for every operating-system network operation. A completed fixture is a learning result, not a real customer incident resolution.

## Primary references

Checked for this project on 7 October 2026. Recheck the documentation before extending live behavior.

- Responses API: https://developers.openai.com/api/reference/python/resources/responses/methods/create
- API errors: https://developers.openai.com/api/docs/guides/error-codes
- Rate limits: https://developers.openai.com/api/docs/guides/rate-limits
- Request IDs and debugging: https://developers.openai.com/api/reference/overview
- API key handling: https://help.openai.com/en/articles/5112595-best-practices-for-api-key-safety
