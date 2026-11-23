# SakhiMart – Progress Report (MVP Demonstration)

**Project title:** SakhiMart: An AI-Assisted, Cybersecure Community Commerce and Financial Intelligence Platform for Rural Self-Help Groups  
**Submission date:** 23 November 2026  
**Project stage:** Prototype / progress milestone

## 1. Problem statement

Women-led Self-Help Groups may face barriers in reaching customers directly and maintaining clear records of savings and withdrawals. Paper-based records can be difficult to reconcile, while digital tools may not always be designed for low-friction community use.

## 2. Proposed solution

SakhiMart is a prototype that combines a small community marketplace, a basic SHG savings ledger, and supporting AI-assisted and cybersecurity demonstrations.

## 3. Current implementation

| Component | Implemented prototype | Evidence to capture |
|---|---|---|
| Core application | Flask application with SQLite | App running in browser |
| Authentication | Password hashing and login/register | Successful login; hash demo |
| Marketplace | Add and view products | Product visible in listing |
| Savings | Deposit/withdrawal and calculated balance | Transaction and updated balance |
| Ledger integrity | SHA-256 linked sample records | Valid chain and edited-record alert |
| Product intelligence | OpenCV blur/brightness check; pricing calculator | Script output |
| Hindi voice | Browser speech-to-text with manual fallback | Browser page output |
| Business advisor | Pandas revenue, top product and low-stock report | Terminal output |
| Monitoring | Duplicate and negative-balance checks | Terminal alerts |

**Important:** Mark a row as completed only after your team has run and verified it. If a module is only generated but not executed, mark it as “code prepared / testing pending”.

## 4. System architecture

```text
                    SAKHIMART USER
                          |
                  Flask Web Application
                          |
             +------------+-------------+
             |                          |
       Authentication              Marketplace
             |                          |
             +------------+-------------+
                          |
                    SQLite Database
                          |
                Savings Transactions
                          |
             +------------+-------------+
             |            |              |
         Security      AI Support     Monitoring
        Hash chain    Image / Voice   Duplicate and
        Passwords     Sales insights  balance checks
```

## 5. Member-wise contribution

1. **Cybersecurity:** password hashing and SHA-256 hash-chain integrity demonstration.
2. **Core CS:** Flask application, SQLite database, marketplace and savings routes.
3. **AI Product Intelligence:** image quality checks and cost-plus pricing calculator.
4. **Hindi Voice Assistant:** Hindi browser speech recognition and basic command extraction.
5. **Business Advisor:** sales summary, top-selling item and low-stock identification.
6. **Monitoring and Feedback:** duplicate transaction and negative-balance alerts.

## 6. Limitations

The current version is a prototype. It does not yet include checkout/payment integration, loan and repayment management, complete role-based permissions, persistent voice-to-ledger integration, production deployment, or trained machine-learning models. The hash-chain is a tamper-evidence demonstration and is not a substitute for a secured production audit system.

## 7. Next steps

- Connect standalone modules to the shared application and database.
- Add product ordering and order status.
- Add SHG loan and repayment records.
- Add role-based access and audit logging.
- Improve accessibility, localization and mobile layout.
- Perform functional, security and usability testing.

## 8. Conclusion

The MVP establishes the initial application foundation and demonstrates the feasibility of combining community product listings, basic savings records, and separate AI-assisted and cybersecurity modules. Further integration and testing are required before the system can be considered a complete application.
