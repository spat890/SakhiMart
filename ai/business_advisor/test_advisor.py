import sqlite3

import pytest

try:
    from .advisor import (load_data, load_data_from_db, revenue_summary,
                          product_performance, low_stock, restock_suggestions,
                          daily_summary, monthly_summary, declining_products,
                          recommendations)
except ImportError:
    from advisor import (load_data, load_data_from_db, revenue_summary,
                         product_performance, low_stock, restock_suggestions,
                         daily_summary, monthly_summary, declining_products,
                         recommendations)

HEADER = "order_id,date,product,quantity_sold,unit_price,cost_price,stock\n"
CSV = HEADER + """1,2026-11-01,Pickle,6,100,60,30
2,2026-11-03,Pickle,4,100,60,26
3,2026-11-09,Pickle,2,100,60,24
4,2026-11-02,Papad,4,50,28,40
5,2026-11-10,Papad,6,50,28,34
6,2026-11-05,Candle,1,80,90,8
7,2026-11-14,Candle,1,80,90,3
"""


@pytest.fixture
def df(tmp_path):
    f = tmp_path / "sales.csv"
    f.write_text(CSV)
    return load_data(f)


def test_revenue_summary(df):
    s = revenue_summary(df)
    assert s["total_revenue"] == 1860
    assert s["orders"] == 7
    assert s["avg_order_value"] == pytest.approx(1860 / 7)
    assert s["total_profit"] == 680


def test_best_and_lowest_product(df):
    perf = product_performance(df)
    assert perf.index[0] == "Pickle"
    assert perf.index[-1] == "Candle"


def test_low_stock_uses_latest_row(df):
    assert list(low_stock(df).index) == ["Candle"]


def test_restock_suggestion_values(df):
    sug = restock_suggestions(df)
    assert list(sug["product"]) == ["Candle"]
    assert sug["suggested_restock"].iloc[0] == 0   # 3 in stock covers 14 days


def test_daily_has_one_row_per_day(df):
    assert len(daily_summary(df)) == 14


def test_monthly_totals_match(df):
    m = monthly_summary(df)
    assert len(m) == 1
    assert m["revenue"].iloc[0] == 1860


def test_declining_detects_pickle_only(df):
    d = declining_products(df)
    assert list(d["product"]) == ["Pickle"]
    assert d["change_pct"].iloc[0] == -80.0


def test_recommendations_come_from_data(df):
    tips = recommendations(df)
    assert any("Pickle" in t and "best seller" in t for t in tips)
    assert any("Papad" in t and "margin" in t for t in tips)
    assert any("Candle" in t and "below cost" in t for t in tips)
    assert any("Candle" in t and "Watch" in t for t in tips)
    assert any("Pickle" in t and "80%" in t for t in tips)


def test_missing_column_raises(tmp_path):
    f = tmp_path / "bad.csv"
    f.write_text("order_id,date\n1,2026-11-01\n")
    with pytest.raises(ValueError):
        load_data(f)


def test_empty_file_raises(tmp_path):
    f = tmp_path / "empty.csv"
    f.write_text(HEADER)
    with pytest.raises(ValueError):
        load_data(f)


def test_negative_values_raise(tmp_path):
    f = tmp_path / "neg.csv"
    f.write_text(HEADER + "1,2026-11-01,Pickle,-2,100,60,30\n")
    with pytest.raises(ValueError):
        load_data(f)


def test_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_data(tmp_path / "nope.csv")


def test_load_from_sqlite_with_custom_query(tmp_path):
    """Checks the loader mechanics only. It does NOT confirm the real
    SakhiMart schema, which Member 2 still has to provide."""
    db = tmp_path / "test.db"
    with sqlite3.connect(db) as conn:
        conn.execute("CREATE TABLE sales (order_id INT, date TEXT, product TEXT,"
                     " quantity_sold INT, unit_price REAL, cost_price REAL,"
                     " stock INT)")
        conn.execute("INSERT INTO sales VALUES "
                     "(1,'2026-11-01','Pickle',3,100,60,20)")
    conn.close()
    data = load_data_from_db(db, query="SELECT * FROM sales")
    assert revenue_summary(data)["total_revenue"] == 300


def test_dashboard_page_renders(df, monkeypatch):
    pytest.importorskip("flask")
    pytest.importorskip("matplotlib")
    try:
        from . import dashboard
    except ImportError:
        import dashboard
    from flask import Flask
    monkeypatch.setattr(dashboard, "load_data", lambda: df)
    app = Flask(__name__)
    app.register_blueprint(dashboard.advisor_bp)
    resp = app.test_client().get("/advisor/")
    assert resp.status_code == 200
    assert b"Pickle" in resp.data
    assert b"data:image/png;base64" in resp.data