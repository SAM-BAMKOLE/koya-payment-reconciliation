#!/usr/bin/env python3
"""Payment reconciliation.

Reads payments.jsonl and works out how much money we actually collected.
Run:  python reconcile.py

Rules (per README):
  - Each line is one event. Ignore lines that can't be read (malformed JSON).
  - Ignore events without a txn_id.
  - A payment can be attempted more than once (same txn_id). Only the latest
    attempt for each txn_id counts (latest by ts).
  - A payment counts as collected only if its latest attempt is success.
  - Amounts may arrive as comma-formatted strings (e.g. "55,707.77").
"""
import json
from collections import defaultdict


def parse_amount(amount):
    """Convert an amount (float or comma-string) to a float."""
    if isinstance(amount, (int, float)):
        return float(amount)
    if isinstance(amount, str):
        return float(amount.replace(",", ""))
    return float(amount)


def main():
    # latest_attempt[txn_id] = event with the greatest ts seen so far
    latest_attempt = {}

    with open("payments.jsonl") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            # Ignore lines that can't be read.
            try:
                event = json.loads(line)
            except (ValueError, TypeError):
                continue
            # Ignore events without a txn_id.
            txn_id = event.get("txn_id")
            if not txn_id:
                continue
            ts = event.get("ts", "")
            current = latest_attempt.get(txn_id)
            if current is None or ts > current.get("ts", ""):
                latest_attempt[txn_id] = event

    total = 0.0
    count = 0
    for txn_id, event in latest_attempt.items():
        if event.get("status") == "success":
            count += 1
            total += parse_amount(event.get("amount", 0))

    with open("expected.txt") as f:
        expected = int(f.read().strip())

    if count != expected:
        print(f"Check failed: counted {count} successful payments, expected {expected}.")
        print("Something in the data isn't being handled the way the README describes.")
    else:
        print(f"Check passed: {count} successful payments.")
        print(f"Your code: KOYA-{round(total)}")


if __name__ == "__main__":
    main()
