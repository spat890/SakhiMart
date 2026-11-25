
import pandas as pd

df = pd.read_csv("sample_transactions.csv")

balances = {}
seen_transactions = set()
alerts = []

print("\n===== SHG TRANSACTION MONITOR =====")

for _, row in df.iterrows():
    tid = row["transaction_id"]
    uid = row["user_id"]
    amount = float(row["amount"])
    ttype = row["type"].lower()

    # Duplicate detection
    if tid in seen_transactions:
        alerts.append({
            "transaction_id": tid,
            "user_id": uid,
            "issue": "Duplicate Transaction"
        })
        continue

    seen_transactions.add(tid)

    if uid not in balances:
        balances[uid] = 0

    if ttype == "deposit":
        balances[uid] += amount
    elif ttype == "withdrawal":
        balances[uid] -= amount
    else:
        print("Unknown transaction type:", ttype)
        continue

    # Negative balance detection
    if balances[uid] < 0:
        alerts.append({
            "transaction_id": tid,
            "user_id": uid,
            "issue": "Negative Balance",
            "balance": balances[uid]
        })

print("\n===== DISCREPANCY REPORT =====")

for alert in alerts:
    print("\nTransaction:", alert["transaction_id"])
    print("User:", alert["user_id"])
    print("Issue:", alert["issue"])

    if "balance" in alert:
        print("Balance:", alert["balance"])

print("\n===== ADMIN FEEDBACK =====")

feedback = []

for alert in alerts:
    print("\nTransaction:", alert["transaction_id"])
    print("Issue:", alert["issue"])

    while True:
        decision = input("Admin decision (Approve/Flag): ").strip().lower()

        if decision in ["approve", "flag"]:
            break

        print("Enter Approve or Flag.")

    feedback.append((alert["transaction_id"], decision.upper()))

print("\n===== FINAL REPORT =====")

for tid, decision in feedback:
    print(tid, "| Admin:", decision)

print("\nFinal Balances:")

for user, balance in balances.items():
    print(user, ":", balance)

print("\nMonitoring completed successfully!")
