
"""
SakhiMart - Role Based Access Control
Member 1 Cybersecurity Module
"""

from functools import wraps

# Define system roles and permissions

ROLE_PERMISSIONS = {
    "admin": [
        "view_all_transactions",
        "manage_users",
        "manage_products",
        "review_fraud_alerts",
        "view_reports"
    ],

    "member": [
        "view_own_savings",
        "add_deposit",
        "view_own_transactions"
    ],

    "seller": [
        "add_product",
        "update_own_product",
        "view_own_orders"
    ]
}


def has_permission(role, permission):
    """Check whether a role has a particular permission."""

    permissions = ROLE_PERMISSIONS.get(role, [])

    return permission in permissions


def require_permission(permission):
    """Decorator to protect functions using role permissions."""

    def decorator(function):

        @wraps(function)
        def wrapper(role, *args, **kwargs):

            if not has_permission(role, permission):
                print(
                    f"ACCESS DENIED: Role '{role}' "
                    f"cannot perform '{permission}'."
                )
                return False

            print(
                f"ACCESS GRANTED: Role '{role}' "
                f"can perform '{permission}'."
            )

            return function(role, *args, **kwargs)

        return wrapper

    return decorator


# Protected operations

@require_permission("view_all_transactions")
def view_transactions(role):
    print("Displaying all financial transactions.")
    return True


@require_permission("add_deposit")
def add_deposit(role):
    print("Savings deposit recorded successfully.")
    return True


@require_permission("add_product")
def add_product(role):
    print("Product added successfully.")
    return True


@require_permission("review_fraud_alerts")
def review_fraud(role):
    print("Fraud alerts displayed for administrator review.")
    return True


# Demonstration

def main():

    print("=" * 50)
    print(" SAKHIMART ROLE-BASED ACCESS CONTROL")
    print("=" * 50)

    print("\n[1] ADMIN ACCESS")
    view_transactions("admin")
    review_fraud("admin")

    print("\n[2] MEMBER ACCESS")
    add_deposit("member")
    view_transactions("member")

    print("\n[3] SELLER ACCESS")
    add_product("seller")

    print("\n[4] UNAUTHORIZED ACCESS TEST")
    view_transactions("seller")
    review_fraud("member")

    print("\nAccess control demonstration completed.")


if __name__ == "__main__":
    main()
