
"""
SakhiMart - Automated Cybersecurity Test Suite
Member 1
"""

import unittest
from copy import deepcopy

from security.authentication_demo import (
    validate_password,
    register_user,
    verify_user_password,
    LoginProtection
)

from security.access_control import has_permission

from security.ledger import (
    create_ledger,
    verify_ledger
)

from security.fraud_detection import (
    detect_large_withdrawals,
    detect_repeated_withdrawals,
    detect_duplicate_transactions,
    detect_unusual_activity
)


class TestSakhiMartSecurity(unittest.TestCase):

    # 1. Password security tests

    def test_strong_password(self):
        valid, errors = validate_password("SakhiMart@2026")
        self.assertTrue(valid)
        self.assertEqual(errors, [])

    def test_weak_password(self):
        valid, errors = validate_password("hello123")
        self.assertFalse(valid)
        self.assertGreater(len(errors), 0)

    def test_password_hash_verification(self):
        password = "SakhiMart@2026"
        stored_hash = register_user(password)

        self.assertNotEqual(password, stored_hash)
        self.assertTrue(verify_user_password(password, stored_hash))
        self.assertFalse(verify_user_password("wrong-password", stored_hash))

    def test_login_lockout(self):
        password_hash = register_user("SakhiMart@2026")

        protection = LoginProtection(
            max_attempts=3,
            lockout_seconds=60
        )

        for _ in range(3):
            success, message = protection.authenticate(
                "asha", "wrong-password", password_hash
            )

        self.assertFalse(success)
        self.assertIn("locked", message.lower())

        success, message = protection.authenticate(
            "asha", "SakhiMart@2026", password_hash
        )

        self.assertFalse(success)

    # 2. Role-based access tests

    def test_admin_permissions(self):
        self.assertTrue(
            has_permission("admin", "view_all_transactions")
        )

    def test_member_permissions(self):
        self.assertTrue(
            has_permission("member", "add_deposit")
        )

    def test_unauthorized_member_access(self):
        self.assertFalse(
            has_permission("member", "review_fraud_alerts")
        )

    def test_unauthorized_seller_access(self):
        self.assertFalse(
            has_permission("seller", "view_all_transactions")
        )

    # 3. Ledger integrity tests

    def setUp(self):

        self.transactions = [
            {"member": "Asha", "type": "Deposit", "amount": 500},
            {"member": "Meena", "type": "Deposit", "amount": 300},
            {"member": "Rani", "type": "Withdrawal", "amount": 100}
        ]

        self.ledger = create_ledger(self.transactions)

    def test_valid_ledger(self):
        self.assertTrue(verify_ledger(self.ledger))

    def test_modified_ledger(self):
        modified = deepcopy(self.ledger)
        modified[0]["amount"] = 9000

        self.assertFalse(verify_ledger(modified))

    def test_deleted_transaction(self):
        deleted = deepcopy(self.ledger)
        deleted.pop(1)

        self.assertFalse(verify_ledger(deleted))

    def test_reordered_transactions(self):
        reordered = deepcopy(self.ledger)
        reordered[0], reordered[1] = reordered[1], reordered[0]

        self.assertFalse(verify_ledger(reordered))

    def test_negative_amount_rejected(self):
        invalid_transaction = [
            {"member": "Asha", "type": "Deposit", "amount": -500}
        ]

        with self.assertRaises(ValueError):
            create_ledger(invalid_transaction)

    # 4. Fraud detection tests

    def test_large_withdrawal_detection(self):

        transactions = [
            {"member": "Asha", "type": "Withdrawal", "amount": 8000}
        ]

        alerts = detect_large_withdrawals(transactions)

        self.assertGreater(len(alerts), 0)

    def test_repeated_withdrawal_detection(self):

        transactions = [
            {"member": "Asha", "type": "Withdrawal", "amount": 100},
            {"member": "Asha", "type": "Withdrawal", "amount": 200},
            {"member": "Asha", "type": "Withdrawal", "amount": 300}
        ]

        alerts = detect_repeated_withdrawals(transactions)

        self.assertGreater(len(alerts), 0)

    def test_duplicate_transaction_detection(self):

        transactions = [
            {"member": "Asha", "type": "Deposit", "amount": 500},
            {"member": "Asha", "type": "Deposit", "amount": 500}
        ]

        alerts = detect_duplicate_transactions(transactions)

        self.assertGreater(len(alerts), 0)

    def test_unusual_activity_detection(self):

        transactions = [
            {
                "member": "Asha",
                "type": "Deposit",
                "amount": 100,
                "timestamp": f"2026-11-23T10:0{i}:00"
            }
            for i in range(5)
        ]

        alerts = detect_unusual_activity(transactions)

        self.assertGreater(len(alerts), 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
