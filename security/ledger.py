
"""
SakhiMart - Secure Financial Transaction Ledger
Member 1 Cybersecurity Module

Features:
1. Unique transaction IDs
2. Automatic timestamps
3. Transaction validation
4. SHA-256 hash chaining
5. Modification detection
6. Deletion and reordering detection
"""

import hashlib
import json
import uuid
from datetime import datetime, timezone
from copy import deepcopy


# --------------------------------
# 1. TRANSACTION VALIDATION
# --------------------------------

def validate_transaction(transaction):

    if not isinstance(transaction, dict):
        raise ValueError("Transaction must be a dictionary.")

    required_fields = ["member", "type", "amount"]

    for field in required_fields:
        if field not in transaction:
            raise ValueError(f"Missing field: {field}")

    if not isinstance(transaction["member"], str) or not transaction["member"].strip():
        raise ValueError("Member name cannot be empty.")

    if transaction["type"] not in ["Deposit", "Withdrawal"]:
        raise ValueError("Invalid transaction type.")

    amount = transaction["amount"]

    if isinstance(amount, bool) or not isinstance(amount, (int, float)):
        raise ValueError("Amount must be numeric.")

    if amount <= 0:
        raise ValueError("Transaction amount must be positive.")


# --------------------------------
# 2. HASH GENERATION
# --------------------------------

def calculate_hash(record):

    transaction_data = json.dumps(
        record,
        sort_keys=True,
        separators=(",", ":")
    )

    return hashlib.sha256(
        transaction_data.encode("utf-8")
    ).hexdigest()


# --------------------------------
# 3. CREATE SECURE LEDGER
# --------------------------------

def create_ledger(transactions):

    ledger = []
    previous_hash = "GENESIS"

    for index, transaction in enumerate(transactions, start=1):

        validate_transaction(transaction)

        record = {
            "id": index,
            "transaction_id": str(uuid.uuid4()),
            "member": transaction["member"],
            "type": transaction["type"],
            "amount": transaction["amount"],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "previous_hash": previous_hash
        }

        current_hash = calculate_hash(record)

        record["hash"] = current_hash

        ledger.append(record)

        previous_hash = current_hash

    return ledger


# --------------------------------
# 4. VERIFY LEDGER INTEGRITY
# --------------------------------

def verify_ledger(ledger):

    previous_hash = "GENESIS"
    transaction_ids = set()

    for index, record in enumerate(ledger, start=1):

        # Check transaction order
        if record.get("id") != index:
            return False

        # Check unique transaction IDs
        transaction_id = record.get("transaction_id")

        if not transaction_id or transaction_id in transaction_ids:
            return False

        transaction_ids.add(transaction_id)

        # Check required fields
        required = [
            "member", "type", "amount",
            "timestamp", "previous_hash", "hash"
        ]

        if any(field not in record for field in required):
            return False

        # Check transaction data
        try:
            validate_transaction(record)
        except (ValueError, TypeError):
            return False

        # Check previous transaction link
        if record["previous_hash"] != previous_hash:
            return False

        # Recalculate current hash
        record_without_hash = {
            key: value
            for key, value in record.items()
            if key != "hash"
        }

        calculated_hash = calculate_hash(record_without_hash)

        if record["hash"] != calculated_hash:
            return False

        previous_hash = record["hash"]

    return True


# --------------------------------
# 5. DISPLAY LEDGER
# --------------------------------

def display_ledger(ledger):

    for record in ledger:

        print(
            f"\nTransaction ID: {record['transaction_id']}"
        )

        print(f"Member: {record['member']}")
        print(f"Type: {record['type']}")
        print(f"Amount: Rs.{record['amount']}")
        print(f"Timestamp: {record['timestamp']}")
        print(f"Hash: {record['hash'][:20]}...")


# --------------------------------
# 6. SECURITY DEMONSTRATION
# --------------------------------

def main():

    print("=" * 55)
    print(" SAKHIMART SECURE FINANCIAL LEDGER")
    print("=" * 55)

    transactions = [
        {"member": "Member A", "type": "Deposit", "amount": 500},
        {"member": "Member B", "type": "Deposit", "amount": 300},
        {"member": "Member C", "type": "Withdrawal", "amount": 100},
        {"member": "Member A", "type": "Deposit", "amount": 200}
    ]

    ledger = create_ledger(transactions)

    print("\n[1] ORIGINAL TRANSACTION LEDGER")
    display_ledger(ledger)

    print("\n[2] ORIGINAL INTEGRITY VERIFICATION")
    print("Ledger valid:", verify_ledger(ledger))

    # Test modification
    print("\n[3] MODIFICATION DETECTION")

    modified_ledger = deepcopy(ledger)
    modified_ledger[1]["amount"] = 3000

    print("Transaction amount changed to Rs.3000")
    print("Ledger valid:", verify_ledger(modified_ledger))

    # Test deletion
    print("\n[4] DELETION DETECTION")

    deleted_ledger = deepcopy(ledger)
    deleted_ledger.pop(1)

    print("Transaction 2 deleted.")
    print("Ledger valid:", verify_ledger(deleted_ledger))

    # Test reordering
    print("\n[5] REORDERING DETECTION")

    reordered_ledger = deepcopy(ledger)
    reordered_ledger[0], reordered_ledger[1] = (
        reordered_ledger[1],
        reordered_ledger[0]
    )

    print("Transaction order changed.")
    print("Ledger valid:", verify_ledger(reordered_ledger))

    # Test invalid transaction
    print("\n[6] INVALID TRANSACTION VALIDATION")

    try:
        create_ledger([
            {"member": "Member D", "type": "Deposit", "amount": -500}
        ])
    except ValueError as error:
        print("Invalid transaction rejected:", error)

    print("\nSecure ledger demonstration completed.")


if __name__ == "__main__":
    main()
