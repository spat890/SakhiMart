# SakhiMart

**A community marketplace and Self-Help Group (SHG) savings management prototype**

SakhiMart is a college project prototype designed to demonstrate how digital tools can support local artisans and Self-Help Groups (SHGs). It combines a Flask web application, an SQLite database, cybersecurity demonstrations, and supporting AI and data-analysis modules.

> **Project status:** Educational MVP / demonstration prototype. Some modules currently run independently and are not yet connected to the main application. Do not use this project to manage real money or sensitive personal information.

---

## Table of contents

- Project overview
- Current features
- Technology stack
- Project structure
- Getting started
- Running the modules
- Security components
- Testing
- Current limitations
- Planned improvements
- Module ownership

## Project overview

The project aims to:
- Provide a simple digital space to list and view handmade products.
- Demonstrate SHG savings contribution and withdrawal tracking.
- Explore cybersecurity practices for a community-commerce application.
- Demonstrate product-image checks, pricing assistance, Hindi voice input, and sales analysis.
- Establish a foundation for a more complete marketplace.

## Current features

### Main Flask application
- User registration and login.
- Password hashing and verification using Werkzeug.
- Product creation and marketplace listing.
- Savings deposits and withdrawals.
- Member balance calculation and recent transaction display.
- SQLite-based data storage.

### Supporting modules
- **Cybersecurity:** authentication demonstration, role-permission mapping, audit logging, fraud checks, and a SHA-256 hash-chain demonstration.
- **Product intelligence:** OpenCV-based image quality checks and a rule-based pricing assistant.
- **Hindi voice assistant:** browser-based Hindi (hi-IN) speech recognition demonstration with a manual text fallback.
- **Business advisor:** sales-data analysis, charts/dashboard components, and rule-based business recommendations.
- **Feedback monitoring:** sample-data checks for transaction discrepancies such as duplicates and negative balances.

These supporting scripts demonstrate individual capabilities. They should not be assumed to run automatically as part of every marketplace action.

## Technology stack

| Area | Technologies |
|---|---|
| Backend | Python, Flask |
| Database | SQLite |
| Authentication | Werkzeug password utilities |
| Frontend | HTML, CSS, JavaScript |
| Image processing | OpenCV |
| Data analysis | Pandas |
| Charts / dashboard | Python charting and dashboard libraries |
| Voice input | Browser Web Speech API |

## Project structure

    SakhiMart/
    ├── app.py
    ├── backend/
    │   └── database.py
    ├── security/
    │   ├── access_control.py
    │   ├── audit_logger.py
    │   ├── authentication_demo.py
    │   ├── fraud_detection.py
    │   ├── ledger.py
    │   └── test_security.py
    ├── ai/
    │   ├── business_advisor/
    │   ├── feedback_monitor/
    │   ├── product_intelligence/
    │   └── voice_assistant/
    ├── data/
    ├── documentation/
    │   ├── member_assignment.md
    │   ├── progress_report.md
    │   ├── test_cases.md
    │   └── screenshots/
    ├── static/
    ├── templates/
    ├── tests/
    ├── uploads/
    ├── requirements.txt
    └── README.md

## Getting started

### Prerequisites
- Python 3.
- Git (optional, for cloning).
- VS Code or another Python editor.
- Chrome or Edge for the browser voice-assistant demonstration.

### 1. Clone the repository

    git clone https://github.com/spat890/SakhiMart.git
    cd SakhiMart

Alternatively, download the repository as a ZIP file and open the extracted SakhiMart folder.

### 2. Create and activate a virtual environment

**Windows PowerShell**

    py -m venv venv
    .\venv\Scripts\Activate.ps1

If PowerShell blocks activation:

    Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
    .\venv\Scripts\Activate.ps1

**macOS / Linux**

    python3 -m venv venv
    source venv/bin/activate

### 3. Install dependencies

    python -m pip install --upgrade pip
    pip install -r requirements.txt

If the python command is not recognised on Windows, use py instead.

### 4. Start the main application

From the project root:

    python app.py

Open the local address printed in the terminal (usually http://127.0.0.1:5000). Register an account and sign in to explore the marketplace and savings features. The application uses a local SQLite database.

## Running the modules

Run commands from the repository root unless a module's own instructions say otherwise.

### Cybersecurity

    python security/authentication_demo.py
    python security/ledger.py
    python security/audit_logger.py
    python security/fraud_detection.py

The access-control module contains permission-mapping logic intended for use by application routes. The supporting security scripts are demonstrations; their presence does not mean all protections are enforced by the main Flask application.

### Product intelligence

    python ai/product_intelligence/pricing_assistant.py

The image-validation module uses OpenCV to assess image properties such as blur and brightness. Use the input format and image path expected by that script when testing it.

### Hindi voice assistant

Open ai/voice_assistant/index.html in Chrome or Edge, allow microphone access, and try the speech-recognition interface. Browser support and microphone permissions may affect the demonstration. A manual text-entry option is also provided.

### Business advisor

Explore the scripts and instructions in ai/business_advisor/. The module includes sales-analysis and dashboard-related components that use the project's sample sales data.

### Feedback monitoring

Explore ai/feedback_monitor/ and its README for the discrepancy-monitoring demonstration. It uses sample transaction data; it is not yet a live monitor of transactions created in the main application.

## Security components

| Component | Purpose |
|---|---|
| authentication_demo.py | Demonstrates password validation, hashing, verification, and temporary lockout logic. |
| access_control.py | Defines example permissions for roles such as admin, seller, and member. |
| audit_logger.py | Records example security events in an audit log. |
| fraud_detection.py | Demonstrates rule-based checks for suspicious transaction patterns. |
| ledger.py | Demonstrates a SHA-256 hash chain and verification of sample records. |

**Important:** These components are not all integrated with the main Flask login, product, or savings routes yet. The hash-chain demonstration is tamper-evident under its assumptions; it is not a blockchain and does not by itself make records immutable.

## Testing

The repository contains test files under tests/, security/, and the individual AI modules. Test coverage and integration are still being developed.

Run tests after installing the project dependencies:

    python -m pytest

If a test fails, check its imports, expected function names, sample-data paths, and dependencies. A test file being present does not mean the complete test suite currently passes.

## Current limitations

- This is an educational prototype, not a production-ready e-commerce or financial platform.
- Supporting security and AI modules are partly standalone and are not all connected to the main Flask application.
- Role-permission mapping is not yet enforced consistently across application routes.
- The authentication lockout demonstration is not the same as persistent rate limiting on the main login route.
- Audit logging and fraud checks are not automatically triggered by every live application event.
- The hash-chain example does not provide independent, tamper-proof storage.
- The voice assistant is a browser demonstration and does not currently submit verified transactions directly to the backend.
- Business and monitoring modules use sample data in places rather than complete live integration with marketplace orders.
- Additional security hardening, validation, and testing are required before real-world deployment.

Do not enter real bank details, Aadhaar numbers, passwords used elsewhere, or other sensitive personal information.

## Planned improvements

1. Move application secrets into environment variables and disable debug mode outside local development.
2. Add CSRF protection, stronger input validation, and secure session settings.
3. Enforce role-based access control on server-side routes.
4. Connect audit logging, fraud checks, and the hash-chain ledger to actual application events.
5. Make savings operations atomic and use precise monetary representation (for example, integer paise).
6. Integrate product-image validation and pricing assistance into product creation.
7. Connect sales dashboards and discrepancy monitoring to actual marketplace data.
8. Extend the marketplace with cart, order placement, stock management, and order history.
9. Repair and expand automated tests, then test the complete user workflow.
10. Prepare a secure deployment configuration.

## Module ownership

Update this table if the team's final allocation changes.

| Work area | Main folders / files | Focus |
|---|---|---|
| Cybersecurity | security/ | Authentication demonstrations, permissions, audit logging, fraud checks, and hash-chain verification |
| Core application | app.py, backend/, templates/ | Flask routes, database operations, user interface, products, and savings |
| Product intelligence | ai/product_intelligence/ | Image quality validation and pricing assistance |
| Hindi voice assistant | ai/voice_assistant/ | Browser-based Hindi speech input |
| Business advisor | ai/business_advisor/, data/ | Sales analysis, charts, and business insights |
| Feedback monitoring | ai/feedback_monitor/ | Sample transaction discrepancy checks |

---

**SakhiMart — Supporting local makers through accessible digital tools.**
