import unittest
from security.ledger import build_chain, verify_chain
from ai.feedback_monitor.discrepancy_detector import detect_issues

class ModuleTests(unittest.TestCase):
    def test_hash_chain_valid_and_tamper_detected(self):
        chain = build_chain([{"member": "Asha", "type": "deposit", "amount": 10}])
        self.assertTrue(verify_chain(chain)[0])
        chain[0]["amount"] = 99
        self.assertFalse(verify_chain(chain)[0])

    def test_duplicate_detected(self):
        tx = [
            {"id":"1","member":"A","kind":"deposit","amount":10,"reference":"R1"},
            {"id":"2","member":"A","kind":"deposit","amount":10,"reference":"R1"},
        ]
        _, issues = detect_issues(tx)
        self.assertTrue(any("duplicate" in issue.lower() for issue in issues))

if __name__ == "__main__":
    unittest.main()
