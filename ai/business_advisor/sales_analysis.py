"""Member 5: Pandas summary from the included fictional sales CSV."""
from pathlib import Path
import pandas as pd

DATA_FILE = Path(__file__).resolve().parents[2] / "data" / "sales.csv"

def analyze_sales(path=DATA_FILE):
    df = pd.read_csv(path)
    required = {"product", "quantity_sold", "unit_price", "stock"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"CSV is missing columns: {sorted(missing)}")
    df["revenue"] = df["quantity_sold"] * df["unit_price"]
    total_revenue = df["revenue"].sum()
    top_product = df.groupby("product")["quantity_sold"].sum().idxmax()
    low_stock = df.loc[df["stock"] < 5, ["product", "stock"]]
    return total_revenue, top_product, low_stock

def main():
    total, top, low = analyze_sales()
    print("SAKHIMART – BUSINESS ADVISOR")
    print(f"Total sample revenue: ₹{total:.2f}")
    print(f"Top-selling product: {top}")
    print("Low-stock products (fewer than 5 units):")
    if low.empty:
        print("None")
    else:
        print(low.to_string(index=False))
    print("Note: Results use fictional demonstration data.")

if __name__ == "__main__":
    main()
