"""Health check for the AppCreative engineering exercise.

Run it with:  bash check.sh

It confirms that your work builds and runs. It does not grade it.
"""
import datetime as dt
import json
import subprocess
import sys
import time
from pathlib import Path

import httpx
import yaml

ROOT = Path(__file__).resolve().parent.parent
CONFIG = json.loads((Path(__file__).resolve().parent / "config.json").read_text())
TELEMETRY_DIR = ROOT / "telemetry-output"
REPORT_FILE = ROOT / "check-results.txt"
PLACEHOLDER_EXPR = "orders_error_rate_percent > 50"

SERVICES = {
    "orders": "http://localhost:8001",
    "recommendations": "http://localhost:8002",
    "practice AI model": "http://localhost:8003",
}

OK, BAD, WARN = "✅", "❌", "⚠️ "
lines = []


def say(text=""):
    print(text, flush=True)
    lines.append(text)


def heading(text):
    say()
    say(text)
    say("-" * len(text))


def services_down():
    down = []
    for name, url in SERVICES.items():
        try:
            httpx.get(f"{url}/health", timeout=2).raise_for_status()
        except Exception:
            down.append(name)
    return down


def check_part1(running):
    heading("PART 1 · Fix and extend")
    command = [sys.executable if part == "python" else part for part in CONFIG["test_command"]]
    try:
        passed = subprocess.run(command, cwd=ROOT, capture_output=True, text=True).returncode == 0
    except FileNotFoundError:
        passed = False
    say(f"{OK} The automated tests pass" if passed
        else f"{BAD} The automated tests fail (run '{CONFIG['test_hint']}' to see why)")

    if not running:
        say(f"{WARN} Skipped the app check because the app isn't running")
        return
    try:
        resp = httpx.get(f"{SERVICES['orders']}/orders/A1001", timeout=15)
        recs = resp.json().get("recommendations", []) if resp.status_code == 200 else []
        good = len(recs) == 3 and all(
            isinstance(r, dict) and r.get("name") and r.get("reason") for r in recs
        )
        say(f"{OK} The app returns 3 recommendations for order A1001, each with a name and a reason" if good
            else f"{BAD} The app doesn't return 3 recommendations with names and reasons yet")
    except Exception as exc:
        say(f"{BAD} The app gave an error for order A1001 ({type(exc).__name__})")


def telemetry_size():
    return sum(p.stat().st_size for p in TELEMETRY_DIR.glob("*.jsonl")) if TELEMETRY_DIR.is_dir() else 0


def check_part2(running):
    heading("PART 2 · Instrument")
    if not running:
        say(f"{WARN} Skipped the telemetry check because the app isn't running")
        return
    before = telemetry_size()
    try:
        httpx.get(f"{SERVICES['orders']}/orders/A1002", timeout=15)
    except Exception:
        pass
    say("   Sent a test request and waiting up to 25 seconds for telemetry to arrive...")
    deadline = time.monotonic() + 25
    arrived = False
    while time.monotonic() < deadline:
        time.sleep(2)
        if telemetry_size() > before:
            arrived = True
            break
    say(f"{OK} Telemetry from the app is reaching the collector" if arrived
        else f"{BAD} No telemetry arrived for the test request (it should go to http://localhost:4318)")


def check_part3():
    heading("PART 3 · Alert")
    try:
        doc = yaml.safe_load((ROOT / "alert-exercise" / "my-alert.yaml").read_text()) or {}
        rules = [r for g in doc.get("groups", []) for r in (g.get("rules") or [])]
    except Exception as exc:
        say(f"{BAD} Couldn't read alert-exercise/my-alert.yaml ({exc})")
        return
    if not rules:
        say(f"{BAD} No alert rule found in alert-exercise/my-alert.yaml")
        return
    for rule in rules:
        expr = " ".join(str(rule.get("expr", "")).split())
        say(f"   Rule '{rule.get('alert', 'unnamed')}':  {expr}   for: {rule.get('for', '0m')}")
        if not expr:
            say(f"{BAD} This rule has no 'expr'")
        elif expr == PLACEHOLDER_EXPR:
            say(f"{BAD} This is still the placeholder rule; it hasn't been changed")
        else:
            say(f"{OK} The alert file is readable and the rule has been written")


def main():
    say("=" * 64)
    say(f" AppCreative exercise health check ({CONFIG['language']})   {dt.datetime.now():%Y-%m-%d %H:%M}")
    say("=" * 64)
    say(" Confirms your work builds and runs. It doesn't grade it.")

    down = services_down()
    if down:
        say()
        say(f"{WARN} These parts of the app aren't running: {', '.join(down)}")
        say("   Run 'bash start.sh' first for a complete check. Checking what I can...")

    check_part1(not down)
    check_part2(not down)
    check_part3()

    say()
    say("This only checks that things run. After you submit, we review your code,")
    say("recording, AI chat and written answers.")
    say()
    REPORT_FILE.write_text("\n".join(lines) + "\n")
    print(f"Saved this report to {REPORT_FILE.name}")


if __name__ == "__main__":
    main()
