"""Sample-data transaction discrepancy checker.

Import-safe: analysis functions do not read files or prompt for input.
Run from any working directory with:
    python ai/feedback_monitor/discrepancy_detector.py
"""
from pathlib import Path
import pandas as pd

DATA_FILE = Path(__file__).resolve().with_name("sample_transactions.csv")


def detect_issues(transactions):
    """Return (balances, issues) for a list of transaction dictionaries.

    Accepted aliases support both the CSV schema (transaction_id/user_id/type)
    and the small test/demo schema (id/member/kind).
    """
    balances = {}
    seen = set()
    issues = []

    for tx in transactions:
        tid = str(tx.get("transaction_id", tx.get("id", "")))
        user = str(tx.get("user_id", tx.get("member", "Unknown")))
        kind = str(tx.get("type", tx.get("kind", ""))).strip().lower()
        try:
            amount = float(tx.get("amount", 0))
        except (TypeError, ValueError):
            issues.append(f"Invalid amount for transaction {tid}")
            continue

        reference = tx.get("reference")
        duplicate_key = ("reference", str(reference)) if reference else ("id", tid)
        if duplicate_key[1] and duplicate_key in seen:
            issues.append(f"Duplicate transaction detected: {tid}")
            continue
        if duplicate_key[1]:
            seen.add(duplicate_key)

        if amount <= 0:
            issues.append(f"Invalid non-positive amount in transaction {tid}")
            continue
        balances.setdefault(user, 0.0)
        if kind == "deposit":
            balances[user] += amount
        elif kind == "withdrawal":
            balances[user] -= amount
        else:
            issues.append(f"Unknown transaction type in transaction {tid}: {kind}")
            continue
        if balances[user] < 0:
            issues.append(f"Negative balance for {user} after transaction {tid}")

    return balances, issues


def load_transactions(path=DATA_FILE):
    frame = pd.read_csv(path)
    required = {"transaction_id", "user_id", "amount", "type"}
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError("Missing CSV columns: " + ", ".join(sorted(missing)))
    return frame.to_dict(orient="records")


def main():
    transactions = load_transactions()
    balances, issues = detect_issues(transactions)

    print("\n===== SHG TRANSACTION MONITOR =====")
    print("\n===== DISCREPANCY REPORT =====")
    if issues:
        for issue in issues:
            print("-", issue)
    else:
        print("No discrepancies found.")

    if issues:
        print("\n===== ADMIN FEEDBACK =====")
        decisions = []
        for issue in issues:
            while True:
                decision = input(f"{issue}\nAdmin decision (Approve/Flag): ").strip().lower()
                if decision in ("approve", "flag"):
                    decisions.append((issue, decision.upper()))
                    break
                print("Enter Approve or Flag.")
        print("\n===== FINAL REPORT =====")
        for issue, decision in decisions:
            print(f"{issue} | Admin: {decision}")

    print("\nFinal Balances:")
    for user, balance in balances.items():
        print(f"{user}: {balance:.2f}")
    print("\nMonitoring completed successfully!")


if __name__ == "__main__":
    main()
