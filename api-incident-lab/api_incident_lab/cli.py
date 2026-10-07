"""Command-line interface. Live requests are optional and can incur API charges."""

from __future__ import annotations

import argparse
import getpass
import json
import os
import sys
from pathlib import Path

from .client import OpenAITransport, run_probe
from .core import handover, markdown_report
from .fixtures import demo, load_scenarios


def write_report(report: dict, directory: Path) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    # The stem comes from a known fixture ID or the fixed live-probe ID.
    stem = report["scenario"]
    (directory / f"{stem}.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    (directory / f"{stem}.md").write_text(markdown_report(report), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="API Incident Lab: offline scenarios and an optional live probe.")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("list", help="List offline scenarios")
    offline = sub.add_parser("demo", help="Run simulated scenarios without a key, charges, or network")
    selection = offline.add_mutually_exclusive_group(required=True)
    selection.add_argument("--all", action="store_true")
    selection.add_argument("--scenario")
    offline.add_argument("--output-dir", type=Path, default=Path("reports/demo"))
    live = sub.add_parser("live", help="Send a minimal paid API request from your own local account")
    live.add_argument("--model", default=os.environ.get("OPENAI_MODEL"))
    live.add_argument("--max-attempts", type=int, choices=(1, 2, 3), default=1,
                      help="Default 1; retries of POST requests may duplicate work or charges")
    live.add_argument("--timeout", type=float, default=12)
    live.add_argument("--time-budget", type=float, default=30)
    live.add_argument("--output-dir", type=Path, default=Path("reports/live"))
    args = parser.parse_args(argv)
    scenarios = load_scenarios()
    if args.command == "list":
        for item in scenarios:
            print(f"{item['id']}: {item['title']}")
        return 0
    if args.command == "demo":
        selected = scenarios if args.all else [item for item in scenarios if item["id"] == args.scenario]
        if not selected:
            parser.error("Unknown scenario; run 'python -m api_incident_lab list' to see choices")
        for item in selected:
            report = demo(item)
            write_report(report, args.output_dir)
            print(f"{item['id']}: {report['diagnosis']['title']} ({len(report['observations'])} attempt(s))")
        print(f"JSON and Markdown reports saved in {args.output_dir.resolve()}")
        return 0
    if not args.model:
        parser.error("Choose a model available to your API project using --model or OPENAI_MODEL")
    if args.timeout <= 0 or args.time_budget <= 0:
        parser.error("--timeout and --time-budget must be positive")
    key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not key and sys.stdin.isatty():
        key = getpass.getpass("Local API key (hidden; not saved): ").strip()
    if not key:
        parser.error("Set OPENAI_API_KEY locally or run from an interactive terminal. Never paste a key into chat.")
    print("Live mode: this sends a minimal request to your API account and can incur charges.")
    report = run_probe(OpenAITransport(key), model=args.model,
                       max_attempts=args.max_attempts, timeout=args.timeout,
                       time_budget=args.time_budget, secrets=(key,))
    write_report(report, args.output_dir)
    print(handover(report))
    print(f"Sanitized reports saved in {args.output_dir.resolve()}")
    return 0 if report["diagnosis"]["category"] == "completed" else 1
