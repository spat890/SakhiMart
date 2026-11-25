import unittest

from security.ledger import create_ledger, verify_ledger
from ai.feedback_monitor.discrepancy_detector import detect_issues


class ModuleTests(unittest.TestCase):
    def test_hash_chain_valid_and_tamper_detected(self):
        chain = create_ledger([{"member": "Asha", "type": "Deposit", "amount": 10}])
        self.assertTrue(verify_ledger(chain))
        chain[0]["amount"] = 99
        self.assertFalse(verify_ledger(chain))

    def test_duplicate_detected(self):
        tx = [
            {"id": "1", "member": "A", "kind": "deposit", "amount": 10, "reference": "R1"},
            {"id": "2", "member": "A", "kind": "deposit", "amount": 10, "reference": "R1"},
        ]
        _, issues = detect_issues(tx)
        self.assertTrue(any("duplicate" in issue.lower() for issue in issues))

    def test_negative_balance_detected(self):
        tx = [{"id": "1", "member": "A", "kind": "withdrawal", "amount": 10}]
        balances, issues = detect_issues(tx)
        self.assertEqual(balances["A"], -10)
        self.assertTrue(any("negative balance" in issue.lower() for issue in issues))


if __name__ == "__main__":
    unittest.main()
