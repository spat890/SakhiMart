"""Member 5: Flask dashboard for the Business Advisor.

Run on its own (from the SakhiMart folder):
    python ai/business_advisor/dashboard.py
then open http://127.0.0.1:5005/advisor/

To plug into the main app, add these two lines to app.py:
    from ai.business_advisor.dashboard import advisor_bp
    app.register_blueprint(advisor_bp)
"""
from flask import Blueprint, Flask, redirect, render_template_string

try:
    from .advisor import (load_data, revenue_summary, product_performance,
                          low_stock, restock_suggestions, declining_products,
                          weekly_summary, monthly_summary, recommendations)
    from .chart import charts_as_base64
except ImportError:  # running as a plain script
    from advisor import (load_data, revenue_summary, product_performance,
                         low_stock, restock_suggestions, declining_products,
                         weekly_summary, monthly_summary, recommendations)
    from chart import charts_as_base64

advisor_bp = Blueprint("advisor", __name__, url_prefix="/advisor")

TEMPLATE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>SakhiMart Business Advisor</title>
<style>
 body{font-family:Segoe UI,Arial,sans-serif;margin:0;background:#faf6f0;color:#2b2b2b}
 header{background:#8a3b12;color:#fff;padding:16px 24px}
 header h1{margin:0;font-size:1.4em}
 main{max-width:1100px;margin:auto;padding:16px}
 .cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px}
 .card{background:#fff;border-radius:10px;padding:14px;box-shadow:0 1px 4px rgba(0,0,0,.15)}
 .card b{display:block;font-size:1.5em;margin-top:4px}
 h2{margin-top:28px;color:#8a3b12}
 .tips li{margin:6px 0}
 .warn{background:#fff3cd;border-left:5px solid #e0a800;padding:10px 14px;border-radius:6px;margin:6px 0}
 .ok{background:#e6f4ea;border-left:5px solid #2e7d32;padding:10px 14px;border-radius:6px;margin:6px 0}
 table.tbl{border-collapse:collapse;width:100%;background:#fff}
 .tbl th,.tbl td{padding:6px 10px;border-bottom:1px solid #eee;text-align:right}
 .tbl th:first-child,.tbl td:first-child{text-align:left}
 .scroll{overflow-x:auto}
 img{max-width:100%}
 footer{color:#777;font-size:.85em;padding:16px 0}
</style></head><body>
<header><h1>SakhiMart Business Advisor</h1>
<small>Insights for SHG sellers (fictional demonstration data)</small></header>
<main>
{% if error %}
 <div class="warn">{{ error }}</div>
{% else %}
 <div class="cards">
  <div class="card">Total revenue<b>Rs {{ s.total_revenue }}</b></div>
  <div class="card">Orders<b>{{ s.orders }}</b></div>
  <div class="card">Average order value<b>Rs {{ s.avg_order_value }}</b></div>
  <div class="card">Estimated profit<b>Rs {{ s.total_profit }}</b></div>
 </div>

 <h2>Warnings</h2>
 {% for w in warnings %}<div class="warn">{{ w }}</div>{% endfor %}
 {% if not warnings %}<div class="ok">No low-stock or declining-sales warnings.</div>{% endif %}

 <h2>Recommendations</h2>
 <ul class="tips">{% for t in tips %}<li>{{ t }}</li>{% endfor %}</ul>

 <h2>Sales charts</h2>
 <img alt="Sales charts" src="data:image/png;base64,{{ chart }}">

 <h2>Product performance</h2><div class="scroll">{{ products|safe }}</div>
 <h2>Restock suggestions</h2><div class="scroll">{{ restock|safe }}</div>
 <h2>Monthly summary</h2><div class="scroll">{{ monthly|safe }}</div>
 <h2>Weekly summary</h2><div class="scroll">{{ weekly|safe }}</div>
{% endif %}
<footer>Recommendations are calculated from the sales data shown, not predictions.</footer>
</main></body></html>"""


@advisor_bp.route("/")
def dashboard():
    try:
        df = load_data()
    except (FileNotFoundError, ValueError) as exc:
        return render_template_string(TEMPLATE, error=str(exc)), 500

    s = revenue_summary(df)
    summary = {
        "total_revenue": f"{s['total_revenue']:,.2f}",
        "orders": s["orders"],
        "avg_order_value": f"{s['avg_order_value']:,.2f}",
        "total_profit": f"{s['total_profit']:,.2f}",
    }

    warnings = []
    for product, row in low_stock(df).iterrows():
        warnings.append(f"Low stock: {product} has only {int(row['stock'])} left.")
    for _, r in declining_products(df).iterrows():
        warnings.append(f"Declining sales: {r['product']} fell "
                        f"{abs(r['change_pct']):.0f}% "
                        f"({r['previous_units']} to {r['recent_units']} units).")

    weekly = weekly_summary(df)
    weekly.index = weekly.index.strftime("%d %b %Y")
    monthly = monthly_summary(df)
    monthly.index = monthly.index.strftime("%b %Y")
    restock = restock_suggestions(df)

    return render_template_string(
        TEMPLATE,
        error=None,
        s=summary,
        warnings=warnings,
        tips=recommendations(df),
        chart=charts_as_base64(df),
        products=product_performance(df).round(2).to_html(classes="tbl", border=0),
        restock=(restock.to_html(classes="tbl", border=0, index=False)
                 if not restock.empty else "<p>Nothing to restock.</p>"),
        monthly=monthly.round(2).to_html(classes="tbl", border=0),
        weekly=weekly.round(2).to_html(classes="tbl", border=0),
    )


if __name__ == "__main__":
    app = Flask(__name__)
    app.register_blueprint(advisor_bp)
    app.add_url_rule("/", "home", lambda: redirect("/advisor/"))
    app.run(port=5005, debug=True)