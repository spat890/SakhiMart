# SakhiMart – Cybersecurity Module

## 1. Objective

To implement essential cybersecurity features for SakhiMart, an AI-driven community commerce and financial platform for rural Self-Help Groups (SHGs). The module focuses on secure authentication, access control, transaction integrity, fraud monitoring, and security event logging.

## 2. Technologies Used

- Python 3.13
- Werkzeug
- SHA-256
- JSON
- Hashlib
- Python Logging
- Unittest

## 3. Implemented Features

### 3.1 Password Authentication
- Generates secure password hashes using Werkzeug.
- Verifies user-entered passwords.
- Validates password strength.
- Rejects incorrect or weak passwords.
- Demonstrates temporary account lockout after repeated failed login attempts.

### 3.2 Role-Based Access Control
- Defines three user roles: Admin, Member, and Seller.
- Assigns permissions according to user roles.
- Restricts unauthorised access to sensitive operations.
- Demonstrates permission checking through access-control functions.

### 3.3 SHA-256 Transaction Integrity
- Creates a chain of linked financial transactions.
- Assigns a unique ID and hash to each transaction.
- Links transactions using previous hashes.
- Verifies transaction integrity.
- Detects modification, deletion, and reordering of transactions.
- Rejects invalid transaction amounts.

### 3.4 Rule-Based Fraud Detection
- Detects large withdrawals.
- Identifies repeated withdrawals by the same member.
- Detects duplicate transaction patterns.
- Identifies unusual transaction frequency.
- Generates alerts for administrative review.

### 3.5 Security Audit Logging
- Records security-related events.
- Logs successful and failed login attempts.
- Records account lockouts and unauthorised access.
- Logs fraud alerts.
- Stores events in `security_audit.log`.

### 3.6 Automated Security Testing
- Tests password strength and verification.
- Tests account lockout behaviour.
- Tests role permissions.
- Tests transaction integrity and tampering detection.
- Tests fraud detection rules.
- All 17 automated test cases passed successfully.

## 4. Project File Structure

```text
security/
├── __init__.py
├── authentication_demo.py
├── access_control.py
├── ledger.py
├── fraud_detection.py
├── audit_logger.py
├── security_audit.log
├── test_security.py
└── README.md
```

## 5. How to Run

Open the terminal from the main SakhiMart project folder and execute:

```powershell
py security/authentication_demo.py
py security/access_control.py
py security/ledger.py
py security/fraud_detection.py
py security/audit_logger.py
```

To execute the automated test suite:

```powershell
py -m unittest security.test_security -v
```

## 6. Testing Results

The cybersecurity modules were executed successfully.

The automated test suite verified:
- Password authentication and validation.
- Login lockout after repeated failed attempts.
- Role-based permission restrictions.
- Valid transaction ledger verification.
- Detection of modified, deleted, and reordered transactions.
- Rejection of invalid transaction amounts.
- Fraud detection rules.

**Result: 17 automated test cases passed.**

## 7. Limitations

- Login lockout is currently maintained in memory and resets when the program restarts.
- Role-based access control is currently demonstrated separately and requires integration with authenticated Flask sessions and database roles.
- Hash-chain verification detects tampering but does not make the ledger permanently immutable.
- Fraud detection generates warning alerts and requires human review.
- Audit logs are stored locally and are not tamper-proof.

## 8. Conclusion

The SakhiMart cybersecurity module demonstrates multiple security mechanisms designed to protect user authentication, control access to sensitive operations, maintain financial transaction integrity, identify suspicious activity, and record security events. These implementations provide a foundation for improving the reliability and security of the SakhiMart platform.