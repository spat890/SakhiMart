# Member 5: AI & Cybernetics Business Advisor

Turns SakhiMart sales data into plain-language business insights for SHG sellers.

## Features
- Revenue, order count, average order value and estimated profit
- Best-selling and slowest products
- Daily, weekly and monthly sales summaries
- Low-stock warnings and restock suggestions (covers 14 days of average sales)
- Declining-sales warnings (fall of 30% or more versus the previous 7 days)
- Recommendations generated from the actual numbers
- Charts (daily trend, weekly revenue/profit, units per product)
- Flask dashboard at /advisor/

## Files
- advisor.py: analysis functions and command-line report
- chart.py: charts (saved PNG or embedded in the dashboard)
- dashboard.py: Flask blueprint and standalone dashboard
- test_advisor.py: automated tests
- sales_analysis.py: original MVP, kept for reference (advisor.py replaces it)

## Setup (from the SakhiMart folder)
    pip install pandas matplotlib flask pytest

## Run
    python ai/business_advisor/advisor.py
    python ai/business_advisor/chart.py
    python ai/business_advisor/dashboard.py
Then open http://127.0.0.1:5005/advisor/

## Test
    python -m pytest ai/business_advisor -v

## Data format
Required columns: order_id, date, product, quantity_sold, unit_price,
cost_price, stock. Demo data: data/sales_extended.csv (fictional).

## Integration with the main application
- dashboard.py exposes `advisor_bp`. In app.py add:
      from ai.business_advisor.dashboard import advisor_bp
      app.register_blueprint(advisor_bp)
- advisor.py has `load_data_from_db()` for SQLite. Its default query uses
  placeholder table and column names and has NOT been tested against the real
  SakhiMart database. It must be adjusted to Member 2's final schema.

## Limitations
- Currently reads the demo CSV; database connection pending the final schema.
- Declining-sales detection needs at least 14 days of data.
- Restock suggestions use average past sales and do not predict future demand.
- Profit uses the cost price stored per product; it ignores other expenses.
- Demo data is fictional.