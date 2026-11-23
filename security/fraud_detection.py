
"""
SakhiMart - Fraud and Suspicious Transaction Detection
Member 1 Cybersecurity Module

Features:
1. Large withdrawal detection
2. Repeated withdrawal detection
3. Duplicate transaction detection
4. Unusual transaction frequency detection
"""

from datetime import datetime, timedelta


# ---------------------------------
# FRAUD DETECTION CONFIGURATION
# ---------------------------------

LARGE_WITHDRAWAL_LIMIT = 5000
MAX_WITHDRAWALS = 3
ACTIVITY_WINDOW_MINUTES = 5
MAX_TRANSACTIONS_IN_WINDOW = 4


# ---------------------------------
# 1. LARGE WITHDRAWAL DETECTION
# ---------------------------------

def detect_large_withdrawals(transactions):

    alerts = []

    for transaction in transactions:

        if (
            transaction["type"] == "Withdrawal"
            and transaction["amount"] > LARGE_WITHDRAWAL_LIMIT
        ):

            alerts.append({
                "member": transaction["member"],
                "reason": "Large withdrawal detected",
                "amount": transaction["amount"]
            })

    return alerts


# ---------------------------------
# 2. REPEATED WITHDRAWAL DETECTION
# ---------------------------------

def detect_repeated_withdrawals(transactions):

    withdrawal_counts = {}
    alerts = []

    for transaction in transactions:

        if transaction["type"] == "Withdrawal":

            member = transaction["member"]

            withdrawal_counts[member] = (
                withdrawal_counts.get(member, 0) + 1
            )

    for member, count in withdrawal_counts.items():

        if count >= MAX_WITHDRAWALS:

            alerts.append({
                "member": member,
                "reason": "Repeated withdrawals detected",
                "count": count
            })

    return alerts


# ---------------------------------
# 3. DUPLICATE TRANSACTION DETECTION
# ---------------------------------

def detect_duplicate_transactions(transactions):

    seen = set()
    alerts = []

    for transaction in transactions:

        key = (
            transaction["member"],
            transaction["type"],
            transaction["amount"]
        )

        if key in seen:

            alerts.append({
                "member": transaction["member"],
                "reason": "Possible duplicate transaction",
                "amount": transaction["amount"]
            })

        else:
            seen.add(key)

    return alerts


# ---------------------------------
# 4. UNUSUAL ACTIVITY DETECTION
# ---------------------------------

def detect_unusual_activity(transactions):

    alerts = []

    member_transactions = {}

    for transaction in transactions:

        timestamp = transaction.get("timestamp")

        if not timestamp:
            continue

        try:
            transaction_time = datetime.fromisoformat(timestamp)

            member = transaction["member"]

            member_transactions.setdefault(
                member, []
            ).append(transaction_time)

        except (ValueError, TypeError):
            continue

    for member, times in member_transactions.items():

        times.sort()

        for start in range(len(times)):

            window_end = (
                times[start] +
                timedelta(minutes=ACTIVITY_WINDOW_MINUTES)
            )

            count = sum(
                1 for time in times
                if times[start] <= time <= window_end
            )

            if count > MAX_TRANSACTIONS_IN_WINDOW:

                alerts.append({
                    "member": member,
                    "reason": "Unusual transaction frequency",
                    "count": count
                })

                break

    return alerts


# ---------------------------------
# 5. COMBINED FRAUD MONITOR
# ---------------------------------

def analyse_transactions(transactions):

    alerts = []

    alerts.extend(detect_large_withdrawals(transactions))
    alerts.extend(detect_repeated_withdrawals(transactions))
    alerts.extend(detect_duplicate_transactions(transactions))
    alerts.extend(detect_unusual_activity(transactions))

    return alerts


# ---------------------------------
# 6. DEMONSTRATION
# ---------------------------------

def main():

    print("=" * 55)
    print(" SAKHIMART FRAUD DETECTION SYSTEM")
    print("=" * 55)

    transactions = [
        {
            "member": "Asha",
            "type": "Deposit",
            "amount": 500,
            "timestamp": "2026-11-23T10:00:00"
        },
        {
            "member": "Asha",
            "type": "Withdrawal",
            "amount": 7000,
            "timestamp": "2026-11-23T10:01:00"
        },
        {
            "member": "Asha",
            "type": "Withdrawal",
            "amount": 7000,
            "timestamp": "2026-11-23T10:02:00"
        },
        {
            "member": "Asha",
            "type": "Withdrawal",
            "amount": 600,
            "timestamp": "2026-11-23T10:03:00"
        },
        {
            "member": "Asha",
            "type": "Withdrawal",
            "amount": 400,
            "timestamp": "2026-11-23T10:04:00"
        },
        {
            "member": "Meena",
            "type": "Deposit",
            "amount": 1000,
            "timestamp": "2026-11-23T10:05:00"
        }
    ]

    print("\n[1] ANALYSING TRANSACTIONS")

    print("Total transactions:", len(transactions))

    alerts = analyse_transactions(transactions)

    print("\n[2] SECURITY ALERTS")

    if not alerts:

        print("No suspicious patterns detected.")

    else:

        for index, alert in enumerate(alerts, start=1):

            print(f"\nAlert {index}")
            print("Member:", alert["member"])
            print("Reason:", alert["reason"])

            if "amount" in alert:
                print("Amount: Rs.", alert["amount"])

            if "count" in alert:
                print("Count:", alert["count"])

    print("\n[3] ADMIN REVIEW")

    if alerts:
        print("WARNING: Transactions require administrator review.")
    else:
        print("No alerts require review.")

    print("\nFraud monitoring demonstration completed.")


if __name__ == "__main__":
    main()
