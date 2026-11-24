"""Member 5: Business Advisor.

Reads sales data from the demo CSV (default) or from the SakhiMart SQLite
database, then produces summaries, warnings and recommendations.
"""
import math
import sqlite3
from contextlib import closing
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DATA_FILE = ROOT / "data" / "sales_extended.csv"
DB_FILE = ROOT / "instance" / "sakhimart.db"   # ASSUMPTION: confirm name with Member 2

REQUIRED = {"order_id", "date", "product", "quantity_sold",
            "unit_price", "cost_price", "stock"}
NUMERIC = ["quantity_sold", "unit_price", "cost_price", "stock"]

LOW_STOCK_LIMIT = 10   # stock at or below this counts as low
COVER_DAYS = 14        # restock enough to cover this many days of sales
WINDOW_DAYS = 7        # length of the window used to spot declining sales
DROP_PCT = 30          # a fall of this % or more counts as declining

# ASSUMPTION: table and column names below are placeholders. Replace them with
# the real SakhiMart schema once Member 2 confirms it. The query must return
# exactly the columns listed in REQUIRED.
DB_QUERY = """
SELECT o.id AS order_id,
       o.created_at AS date,
       p.name AS product,
       oi.quantity AS quantity_sold,
       oi.unit_price AS unit_price,
       p.cost_price AS cost_price,
       p.stock AS stock
FROM orders o
JOIN order_items oi ON oi.order_id = o.id
JOIN products p ON p.id = oi.product_id
WHERE o.status != 'Cancelled'
"""


def _prepare(df):
    """Validate the data and add revenue and profit columns."""
    if df.empty:
        raise ValueError("The sales data is empty.")
    missing = REQUIRED - set(df.columns)
    if missing:
        raise ValueError(f"Data is missing columns: {sorted(missing)}")
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"])
    for col in NUMERIC:
        df[col] = pd.to_numeric(df[col], errors="raise")
    if (df[NUMERIC] < 0).any().any():
        raise ValueError("Quantity, prices and stock cannot be negative.")
    df["revenue"] = df["quantity_sold"] * df["unit_price"]
    df["profit"] = df["quantity_sold"] * (df["unit_price"] - df["cost_price"])
    return df


def load_data(path=DATA_FILE):
    """Read the csv, check it, and add revenue and profit columns."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Sales file not found: {path}")
    return _prepare(pd.read_csv(path))


def load_data_from_db(db_path=DB_FILE, query=DB_QUERY):
    """Read sales from a SQLite database using the given query."""
    db_path = Path(db_path)
    if not db_path.exists():
        raise FileNotFoundError(f"Database not found: {db_path}")
    with closing(sqlite3.connect(db_path)) as conn:
        df = pd.read_sql_query(query, conn)
    return _prepare(df)


def revenue_summary(df):
    """Total revenue, number of orders, average order value, total profit."""
    total_revenue = df["revenue"].sum()
    orders = df["order_id"].nunique()
    return {
        "total_revenue": total_revenue,
        "orders": orders,
        "avg_order_value": total_revenue / orders,
        "total_profit": df["profit"].sum(),
    }


def product_performance(df):
    """Units sold, revenue and profit for each product, best seller first."""
    table = df.groupby("product").agg(
        units_sold=("quantity_sold", "sum"),
        revenue=("revenue", "sum"),
        profit=("profit", "sum"),
    )
    return table.sort_values("units_sold", ascending=False)


def latest_stock(df):
    """Stock value from the most recent row of each product."""
    latest = df.sort_values("date", kind="stable").groupby("product").tail(1)
    return latest.set_index("product")["stock"]


def low_stock(df, limit=LOW_STOCK_LIMIT):
    """Products whose current stock is at or below the limit."""
    stock = latest_stock(df)
    return stock[stock <= limit].sort_values().to_frame("stock")


def restock_suggestions(df, limit=LOW_STOCK_LIMIT, cover_days=COVER_DAYS):
    """For each low-stock product, suggest how many units to add."""
    days = (df["date"].max() - df["date"].min()).days + 1
    units = df.groupby("product")["quantity_sold"].sum()
    rows = []
    for product, stock in latest_stock(df).items():
        if stock <= limit:
            daily = units[product] / days
            needed = math.ceil(round(daily * cover_days, 6)) - stock
            rows.append({
                "product": product,
                "stock": int(stock),
                "avg_daily_sales": round(daily, 2),
                "suggested_restock": int(max(needed, 0)),
            })
    return pd.DataFrame(
        rows,
        columns=["product", "stock", "avg_daily_sales", "suggested_restock"],
    )


def _summary(df, rule, index_name):
    out = df.set_index("date").resample(rule).agg(
        orders=("order_id", "nunique"),
        units_sold=("quantity_sold", "sum"),
        revenue=("revenue", "sum"),
        profit=("profit", "sum"),
    )
    out.index.name = index_name
    return out


def daily_summary(df):
    """Orders, units, revenue and profit for each day."""
    return _summary(df, "D", "date")


def weekly_summary(df):
    """Orders, units, revenue and profit for each week (weeks end on Sunday)."""
    return _summary(df, "W", "week_ending")


def monthly_summary(df):
    """Orders, units, revenue and profit for each calendar month."""
    return _summary(df, "MS", "month_starting")


def declining_products(df, window_days=WINDOW_DAYS, drop_pct=DROP_PCT):
    """Products whose units sold fell by drop_pct% or more versus the
    previous window. Needs at least two windows of data to compare."""
    end = df["date"].max().normalize()
    recent_start = end - pd.Timedelta(days=window_days - 1)
    prev_start = recent_start - pd.Timedelta(days=window_days)
    recent = (df[df["date"] >= recent_start]
              .groupby("product")["quantity_sold"].sum())
    prev = (df[(df["date"] >= prev_start) & (df["date"] < recent_start)]
            .groupby("product")["quantity_sold"].sum())
    rows = []
    for product, before in prev.items():
        if before <= 0:
            continue
        after = recent.get(product, 0)
        change = (after - before) / before * 100
        if change <= -drop_pct:
            rows.append({
                "product": product,
                "previous_units": int(before),
                "recent_units": int(after),
                "change_pct": round(float(change), 1),
            })
    return pd.DataFrame(
        rows,
        columns=["product", "previous_units", "recent_units", "change_pct"],
    )


def recommendations(df):
    """Plain-language advice. Every line is built from numbers in the data."""
    tips = []
    perf = product_performance(df)

    tips.append(f"{perf.index[0]} is your best seller "
                f"({int(perf.iloc[0]['units_sold'])} units sold). "
                "Keep it well stocked.")

    margin = ((perf["profit"] / perf["revenue"] * 100)
              .replace([float("inf"), float("-inf")], float("nan")).dropna())
    if not margin.empty:
        top = margin.idxmax()
        tips.append(f"{top} has the highest profit margin ({margin[top]:.0f}%). "
                    "Consider promoting it more.")

    if len(perf) > 1:
        tips.append(f"{perf.index[-1]} is selling slowest "
                    f"({int(perf.iloc[-1]['units_sold'])} units). Consider a "
                    "discount or bundle offer before restocking it.")

    for product in perf.index[perf["profit"] < 0]:
        tips.append(f"{product} is selling below cost price. Review its price.")

    for _, r in restock_suggestions(df).iterrows():
        if r["suggested_restock"] > 0:
            tips.append(f"Restock {r['product']}: only {r['stock']} left, selling "
                        f"about {r['avg_daily_sales']} per day. Add about "
                        f"{r['suggested_restock']} units.")
        else:
            tips.append(f"Watch {r['product']}: stock is low ({r['stock']}) but "
                        f"covers the next {COVER_DAYS} days at the current rate.")

    for _, r in declining_products(df).iterrows():
        tips.append(f"Sales of {r['product']} fell {abs(r['change_pct']):.0f}% "
                    f"(from {r['previous_units']} to {r['recent_units']} units) "
                    f"compared with the previous {WINDOW_DAYS} days. "
                    "Check price, quality or visibility.")
    return tips


def main():
    df = load_data()
    s = revenue_summary(df)
    print("SAKHIMART - BUSINESS ADVISOR")
    print(f"Total revenue: Rs {s['total_revenue']:.2f}")
    print(f"Number of orders: {s['orders']}")
    print(f"Average order value: Rs {s['avg_order_value']:.2f}")
    print(f"Estimated profit: Rs {s['total_profit']:.2f}")

    print("\nProduct performance (sorted by units sold):")
    print(product_performance(df).to_string())

    print("\nMonthly summary:")
    print(monthly_summary(df).to_string())
    print("\nWeekly summary:")
    print(weekly_summary(df).to_string())

    print("\nWARNINGS")
    low = low_stock(df)
    print("Low stock:", ", ".join(low.index) if not low.empty else "none")
    dec = declining_products(df)
    print("Declining sales:",
          ", ".join(dec["product"]) if not dec.empty else "none")

    print("\nRECOMMENDATIONS")
    for i, tip in enumerate(recommendations(df), 1):
        print(f"{i}. {tip}")
    print("\nNote: Results use fictional demonstration data.")


if __name__ == "__main__":
    main()