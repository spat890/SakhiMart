
"""
SakhiMart - Member 1 Cybersecurity Module
Features:
1. Password strength validation
2. Secure password hashing using Werkzeug
3. Password verification
4. Login attempt monitoring
5. Temporary account lockout
"""

import time
from werkzeug.security import generate_password_hash, check_password_hash


# -------------------------------
# 1. PASSWORD STRENGTH VALIDATION
# -------------------------------

def validate_password(password):
    errors = []

    if len(password) < 10:
        errors.append("At least 10 characters required.")

    if not any(char.isupper() for char in password):
        errors.append("At least one uppercase letter required.")

    if not any(char.islower() for char in password):
        errors.append("At least one lowercase letter required.")

    if not any(char.isdigit() for char in password):
        errors.append("At least one number required.")

    if not any(not char.isalnum() for char in password):
        errors.append("At least one special character required.")

    return len(errors) == 0, errors


# -------------------------------
# 2. SECURE PASSWORD HASHING
# -------------------------------

def register_user(password):
    valid, errors = validate_password(password)

    if not valid:
        raise ValueError("Weak password: " + " ".join(errors))

    return generate_password_hash(password)


def verify_user_password(password, stored_hash):
    return check_password_hash(stored_hash, password)


# -------------------------------
# 3. LOGIN ATTEMPT PROTECTION
# -------------------------------

class LoginProtection:

    def __init__(self, max_attempts=5, lockout_seconds=60):
        self.max_attempts = max_attempts
        self.lockout_seconds = lockout_seconds
        self.failed_attempts = {}
        self.locked_until = {}

    def authenticate(self, username, password, stored_hash):

        current_time = time.time()

        # Check whether account is locked
        if current_time < self.locked_until.get(username, 0):
            remaining = int(
                self.locked_until[username] - current_time
            ) + 1

            return False, f"Account locked. Try again in {remaining} seconds."

        # Verify password
        if verify_user_password(password, stored_hash):

            self.failed_attempts[username] = 0
            self.locked_until.pop(username, None)

            return True, "Login successful."

        # Record failed attempt
        attempts = self.failed_attempts.get(username, 0) + 1
        self.failed_attempts[username] = attempts

        if attempts >= self.max_attempts:

            self.locked_until[username] = (
                current_time + self.lockout_seconds
            )

            self.failed_attempts[username] = 0

            return False, "Too many failed attempts. Account temporarily locked."

        remaining = self.max_attempts - attempts

        return False, (
            f"Incorrect password. {remaining} attempts remaining."
        )


# -------------------------------
# 4. DEMONSTRATION
# -------------------------------

def main():

    print("=" * 50)
    print(" SAKHIMART AUTHENTICATION SECURITY SYSTEM")
    print("=" * 50)

    username = "asha"

    # Demonstration password
    demo_password = "SakhiMart@2026"

    # Register user and generate secure hash
    print("\n[1] PASSWORD REGISTRATION")

    stored_hash = register_user(demo_password)

    print("Password strength: STRONG")
    print("Password successfully hashed.")
    print("Stored hash:", stored_hash)
    print("Original password is not stored.")

    # Verify password
    print("\n[2] PASSWORD VERIFICATION")

    print(
        "Correct password:",
        verify_user_password(demo_password, stored_hash)
    )

    print(
        "Incorrect password:",
        verify_user_password("wrong-password", stored_hash)
    )

    # Test weak password
    print("\n[3] PASSWORD POLICY TEST")

    valid, errors = validate_password("hello123")

    print("Weak password accepted:", valid)

    for error in errors:
        print("-", error)

    # Login protection demonstration
    print("\n[4] LOGIN ATTEMPT PROTECTION")

    security = LoginProtection(
        max_attempts=5,
        lockout_seconds=60
    )

    for attempt in range(1, 6):

        success, message = security.authenticate(
            username,
            "wrong-password",
            stored_hash
        )

        print(f"Attempt {attempt}: {message}")

    # Attempt login after account lockout
    print("\n[5] ACCOUNT LOCKOUT TEST")

    success, message = security.authenticate(
        username,
        demo_password,
        stored_hash
    )

    print("Correct password after lockout:", success)
    print("System response:", message)

    print("\nAuthentication security demonstration completed.")


if __name__ == "__main__":
    main()
