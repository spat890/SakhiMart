# SakhiMart –  (40% Progress Demonstrator)

SakhiMart is a prototype community marketplace and basic SHG savings ledger for Self-Help Groups. This MVP is designed for a college progress demonstration. It contains a working Flask + SQLite core and six independently runnable member modules.

## Features included

- Register and log in with Werkzeug password hashing.
- Add and view handmade products.
- Record savings contributions/withdrawals and calculate member balances.
- SHA-256 hash-chain demonstration for tamper-evident sample transactions.
- OpenCV image blur and brightness checks.
- Simple pricing calculator.
- Browser Hindi speech-to-text demo (`hi-IN`) with manual fallback.
- Pandas sales summary and low-stock alerts.
- Duplicate transaction and negative-balance checks.

## Important prototype limitations

- This is an educational MVP, not a production financial service.
- The hash-chain script demonstrates tamper detection; it is not blockchain and does not guarantee immutability if an attacker can rewrite the whole chain and its trusted checkpoint.
- Fraud and discrepancy checks are warning mechanisms, not guarantees.
- Browser speech recognition support varies by browser and may require an internet connection.
- Sample data is fictional. Do not enter real Aadhaar, bank credentials, or sensitive personal information.

## 1. Setup in Windows / VS Code

Open the extracted `SakhiMart` folder in VS Code. In the VS Code terminal (PowerShell):

```powershell
python --version
python -m venv venv
.\venv\Scripts\Activate.ps1
```

If PowerShell blocks activation:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
```

Install packages:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If `python` is not recognized, try `py` instead of `python`.

## 2. Run the main application

```powershell
python app.py
```

Open the URL printed in the terminal (normally http://127.0.0.1:5000).

Register a user, log in, add a product, and record a savings transaction. The SQLite database is created automatically at `instance/sakhimart.db`.

## 3. Run each member module

Run these from the project root. Some scripts use sample data included in `data/`.

### Member 1 – Cybersecurity

```powershell
python security/ledger.py
python security/authentication_demo.py
```

### Member 2 – Core CS

```powershell
python app.py
```

### Member 3 – AI Product Intelligence

```powershell
python ai/product_intelligence/image_validation.py --image sample_product.jpg
python ai/product_intelligence/pricing_assistant.py
```

To test image validation with your own product photo, replace `sample_product.jpg` with an image path.

### Member 4 – Hindi Voice Assistant

Open `ai/voice_assistant/index.html` in Chrome or Edge. Allow microphone access and click **Start listening**. If speech recognition is unavailable, type a Hindi/English transaction phrase in the manual box.

### Member 5 – Business Advisor

```powershell
python ai/business_advisor/sales_analysis.py
```

### Member 6 – Monitoring and Feedback

```powershell
python ai/feedback_monitor/discrepancy_detector.py
```

## 4. Screenshots for the progress submission

Capture real screenshots after running the project:

1. Homepage / login page.
2. Product successfully added and visible in marketplace.
3. Savings transaction and updated balance.
4. `security/ledger.py` showing valid chain and tampering detection.
5. OpenCV image validation output.
6. Hindi voice assistant page showing recognized or manually entered text.
7. Pandas sales summary.
8. Monitoring script showing duplicate/negative-balance warnings.

Save them in `documentation/screenshots/`. Do not use mock screenshots as evidence of execution.

## 5. Member-wise ownership

| Member | Files | Demonstration |
|---|---|---|
| 1 – Cybersecurity | `security/` | Password hashing and hash-chain tamper check |
| 2 – Core CS | `app.py`, `backend/` | Flask app, products, savings ledger |
| 3 – AI Product Intelligence | `ai/product_intelligence/` | Image quality and pricing |
| 4 – Hindi Voice | `ai/voice_assistant/` | Hindi speech-to-text and amount extraction |
| 5 – Business Advisor | `ai/business_advisor/`, `data/sales.csv` | Revenue, top product, low stock |
| 6 – Monitoring & Feedback | `ai/feedback_monitor/` | Duplicate and balance checks |

## 6. What is not implemented yet

For the next development phase: product ordering and checkout, loan/repayment workflows, full role-based authorization, persistent voice transaction entry, production deployment, audit-log administration, model training, and comprehensive security testing.

