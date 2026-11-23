"""Member 6: Flags duplicate sample transactions and negative running balances."""
from collections import defaultdict

SAMPLE_TRANSACTIONS = [
    {"id": "T001", "member": "Asha", "kind": "deposit", "amount": 500, "reference": "UPI100"},
    {"id": "T002", "member": "Asha", "kind": "withdrawal", "amount": 200, "reference": "CASH201"},
    {"id": "T003", "member": "Meena", "kind": "withdrawal", "amount": 100, "reference": "CASH301"},
    {"id": "T004", "member": "Asha", "kind": "deposit", "amount": 500, "reference": "UPI100"},
]

def detect_issues(transactions):
    seen = set()
    balances = defaultdict(float)
    issues = []
    for tx in transactions:
        duplicate_key = (tx["member"], tx["kind"], tx["amount"], tx["reference"])
        if duplicate_key in seen:
            issues.append(f"Possible duplicate transaction: {tx['id']} ({tx['reference']})")
        seen.add(duplicate_key)
        if tx["kind"] not in ("deposit", "withdrawal") or tx["amount"] <= 0:
            issues.append(f"Invalid transaction data: {tx['id']}")
            continue
        delta = tx["amount"] if tx["kind"] == "deposit" else -tx["amount"]
        balances[tx["member"]] += delta
        if balances[tx["member"]] < 0:
            issues.append(f"Negative running balance for {tx['member']} at {tx['id']}")
    return dict(balances), issues

def main():
    balances, issues = detect_issues(SAMPLE_TRANSACTIONS)
    print("SAKHIMART – TRANSACTION MONITOR")
    print("Calculated balances:")
    for member, balance in balances.items():
        print(f"  {member}: ₹{balance:.2f}")
    print("Alerts:")
    for issue in issues:
        print("  FLAG:", issue)
    if not issues:
        print("  No issues found.")
    decision = input("Admin review (A=approve sample / F=flag sample): ").strip().upper()
    print("Review recorded for demonstration:", "APPROVE" if decision == "A" else "FLAG" if decision == "F" else "NO VALID SELECTION")
    print("Alerts are decision-support warnings; a human must review them.")

if __name__ == "__main__":
    main()
