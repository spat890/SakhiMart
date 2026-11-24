"""Member 5: Sales charts for the Business Advisor."""
import base64
import io
from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # draw to files/memory, no pop-up window needed
import matplotlib.dates as mdates
import matplotlib.pyplot as plt

try:
    from .advisor import (load_data, daily_summary, weekly_summary,
                          product_performance)
except ImportError:  # running as a plain script
    from advisor import (load_data, daily_summary, weekly_summary,
                         product_performance)

OUT_FILE = (Path(__file__).resolve().parents[2]
            / "documentation" / "screenshots" / "05_sales_charts.png")


def build_figure(df):
    """Daily trend, weekly revenue/profit and units per product."""
    daily = daily_summary(df)
    weekly = weekly_summary(df)
    products = product_performance(df)

    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(18, 5))

    # Chart 1: daily trend
    ax1.plot(daily.index, daily["revenue"], marker="o", label="Revenue")
    ax1.plot(daily.index, daily["profit"], marker="o", label="Profit")
    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))
    ax1.tick_params(axis="x", rotation=30)
    ax1.set_title("Daily revenue and profit")
    ax1.set_ylabel("Rupees")
    ax1.legend()

    # Chart 2: weekly revenue and profit
    labels = [d.strftime("%d %b") for d in weekly.index]
    x = list(range(len(weekly)))
    w = 0.4
    ax2.bar([i - w / 2 for i in x], weekly["revenue"], w, label="Revenue")
    ax2.bar([i + w / 2 for i in x], weekly["profit"], w, label="Profit")
    ax2.set_xticks(x)
    ax2.set_xticklabels(labels)
    ax2.set_title("Weekly revenue and profit (week ending)")
    ax2.set_ylabel("Rupees")
    ax2.legend()

    # Chart 3: units sold per product
    ax3.bar(products.index, products["units_sold"], color="tab:green")
    ax3.set_title("Units sold per product")
    ax3.set_ylabel("Units")
    ax3.tick_params(axis="x", rotation=15)

    fig.suptitle("SakhiMart Business Advisor (fictional demonstration data)")
    fig.tight_layout()
    return fig


def make_charts(df, out_path=OUT_FILE):
    """Save the charts as a PNG file and return its path."""
    fig = build_figure(df)
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=120)
    plt.close(fig)
    return out_path


def charts_as_base64(df):
    """Return the charts as a base64 PNG string for embedding in a web page."""
    fig = build_figure(df)
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=100)
    plt.close(fig)
    return base64.b64encode(buf.getvalue()).decode("ascii")


if __name__ == "__main__":
    saved = make_charts(load_data())
    print(f"Chart saved to: {saved}")