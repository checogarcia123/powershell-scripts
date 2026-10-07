# Practical exercises

## Exercise 1 — Explain two different 429 responses

Run the `rate-limit-recovery` and `credits-exhausted` scenarios. Open both reports. Identify the shared status code, the different error codes, the delay decision, and the resulting number of attempts. Explain why a credit-related error should not be placed in a retry loop.

## Exercise 2 — Trace a request through the code

Start at `cli.main()`. Follow `demo()` to `run_probe()`, `observe()`, `diagnose()` and `write_report()`. Identify the point where raw body data becomes a limited evidence record. Locate the redaction call and the allowlist of response headers.

## Exercise 3 — Make an explainable change

Copy the `credits-exhausted` fixture into a new `organization-spend-limit` scenario. Change its code to `organization_spend_limit_exceeded`. Run that scenario and add its expected category/attempt count to the all-fixtures test. Show that it stops after one attempt. Make this change yourself; it is a good first demonstration of understanding rather than only running prepared code.

## Exercise 4 — Write a customer update

For the timeout fixture, write four sentences: what was observed, what is still unknown, the next investigation action, and when you will provide an update. Do not assert an outage, DNS failure or successful completion without evidence. Choose a hypothetical next-update interval and label it as a training assumption.

## Exercise 5 — Break the retry policy intentionally

In a separate local copy, temporarily change the billing decision to allow retries. Run the tests and find the failure. Restore the correct behavior. Explain how that test protects against unnecessary requests and poor incident handling.

## Readiness check

You are ready to show this lab when you can run it on your own computer, explain the five main files, interpret the reports, make one small tested change, and describe the limits of offline evidence. Describe AI assistance openly. Only claim hands-on OpenAI API integration after you have actually completed and understood a live test.
