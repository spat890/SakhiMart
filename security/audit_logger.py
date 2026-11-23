
"""
SakhiMart - Security Audit Logging System
Member 1 Cybersecurity Module
"""

import logging
from pathlib import Path
from datetime import datetime, timezone


# Store logs inside the security folder
LOG_FILE = Path(__file__).resolve().parent / "security_audit.log"

logging.basicConfig(
    filename=str(LOG_FILE),
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    encoding="utf-8"
)

logger = logging.getLogger("SakhiMartSecurity")


def log_event(event, username="SYSTEM", details=""):

    logger.info(
        "Event: %s | User: %s | Details: %s",
        event,
        username,
        details
    )


def log_login_success(username):
    log_event(
        "LOGIN_SUCCESS",
        username,
        "User authenticated successfully"
    )


def log_login_failure(username):
    log_event(
        "LOGIN_FAILURE",
        username,
        "Incorrect password entered"
    )


def log_account_lockout(username):
    log_event(
        "ACCOUNT_LOCKOUT",
        username,
        "Account temporarily locked after repeated failures"
    )


def log_access_denied(username, permission):
    log_event(
        "ACCESS_DENIED",
        username,
        f"Unauthorized permission request: {permission}"
    )


def log_fraud_alert(username, reason):
    log_event(
        "FRAUD_ALERT",
        username,
        reason
    )


def main():

    print("=" * 50)
    print(" SAKHIMART SECURITY AUDIT LOGGER")
    print("=" * 50)

    log_login_success("asha")
    log_login_failure("asha")
    log_account_lockout("asha")
    log_access_denied("meena", "view_all_transactions")
    log_fraud_alert("asha", "Unusually large withdrawal")

    print("\nFive security events recorded successfully.")

    print("\nAudit log location:")
    print(LOG_FILE)

    print("\nAudit logging demonstration completed.")


if __name__ == "__main__":
    main()
