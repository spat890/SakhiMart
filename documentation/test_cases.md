# SakhiMart MVP – Test Cases

Run each test and record the actual result. Do not mark a test as passed until it has been executed.

## Core application
1. Register with valid name, username and password of 8+ characters. Expected: account created.
2. Register again with the same username. Expected: duplicate username message.
3. Log in with correct password, then incorrect password. Expected: success, then rejection.
4. Add a product with a valid name, price and stock. Expected: product appears in marketplace.
5. Try a negative product price or stock. Expected: validation message.
6. Record a deposit of ₹500. Expected: balance increases by ₹500.
7. Attempt a withdrawal larger than the balance. Expected: rejected; balance unchanged.

## Member 1 – Security
1. Run `python security/authentication_demo.py`. Expected: correct password accepted and wrong password rejected.
2. Run `python security/ledger.py`. Expected: original chain verifies.
3. Same script should detect the edited transaction record.

## Member 3 – Image / pricing
1. Run image validation with a clear, well-lit product photo. Expected: acceptable or useful measurements.
2. Run with a blurred or dark photo. Expected: improvement warning.
3. Run pricing assistant with positive values. Expected: total cost and suggested price.
4. Enter a negative value. Expected: invalid input message.

## Member 4 – Voice
1. Open the page in Chrome or Edge and grant microphone permission.
2. Speak “500 जमा”. Expected: text is captured, amount 500 and deposit intent detected.
3. If recognition is unsupported, type “500 जमा” and use Analyze text. Expected: same extracted result.
4. Speak a Hindi number word without digits. Expected: amount not detected (known MVP limitation).

## Member 5 – Business advisor
1. Run `python ai/business_advisor/sales_analysis.py`. Expected: revenue, top product and low-stock list.
2. Inspect `data/sales.csv`; expected low-stock items have stock below 5.
3. Temporarily rename a required CSV column. Expected: clear missing-column error.

## Member 6 – Monitoring
1. Run `python ai/feedback_monitor/discrepancy_detector.py`. Expected: duplicate reference alert.
2. Expected: negative running balance alert for Meena.
3. Change a transaction to a positive balanced transaction and rerun. Expected: corresponding alert changes.
