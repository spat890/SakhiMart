import os
import sqlite3

from flask import (
    Blueprint,
    Flask,
    current_app,
    flash,
    g,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.security import check_password_hash, generate_password_hash

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
SCHEMA_PATH = os.path.join(BASE_DIR, "schema.sql")
DB_PATH = os.path.join(BASE_DIR, "instance", "sakhimart.db")
DEMO_PHONE = "9000000000"
DEMO_PASSWORD = "sakhi123"
MIN_PASSWORD_LENGTH = 6

main = Blueprint("main", __name__)


def create_app(db_path=None):
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ.get("SAKHIMART_SECRET", "dev-only-secret")
    app.config["DATABASE"] = db_path or DB_PATH
    app.teardown_appcontext(close_db)
    with app.app_context():
        init_db()
    app.register_blueprint(main)
    return app


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(_error=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db_path = current_app.config["DATABASE"]
    os.makedirs(os.path.dirname(db_path) or ".", exist_ok=True)
    db = get_db()
    with open(SCHEMA_PATH, encoding="utf-8") as schema:
        db.executescript(schema.read())
    db.execute(
        "INSERT OR IGNORE INTO users (id, name, phone, password_hash, role) VALUES (?, ?, ?, ?, ?)",
        (1, "Demo Seller", DEMO_PHONE, generate_password_hash(DEMO_PASSWORD), "seller"),
    )
    db.commit()


def balance_for(user_id):
    row = get_db().execute(
        "SELECT COALESCE(SUM(CASE WHEN kind = 'deposit' THEN amount ELSE -amount END), 0) AS balance "
        "FROM transactions WHERE user_id = ?",
        (user_id,),
    ).fetchone()
    return float(row["balance"])


def validate_product(name, price, stock):
    if not name:
        return "Product name is required."
    try:
        price_value = float(price)
        stock_value = int(stock)
    except ValueError:
        return "Price must be a number and stock must be a whole number."
    if price_value <= 0:
        return "Price must be greater than zero."
    if stock_value < 0:
        return "Stock cannot be negative."
    return None


def validate_transaction(kind, amount, user_id):
    if kind not in ("deposit", "withdraw"):
        return "Choose deposit or withdraw."
    try:
        value = float(amount)
    except ValueError:
        return "Amount must be a number."
    if value <= 0:
        return "Amount must be greater than zero."
    if kind == "withdraw":
        balance = balance_for(user_id)
        if value > balance:
            return f"Withdrawal exceeds available balance of Rs {balance:.2f}."
    return None


@main.get("/")
def index():
    db = get_db()
    user_id = session.get("user_id")
    user = None
    balance = None
    if user_id:
        user = db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        balance = balance_for(user_id)
    return render_template(
        "index.html",
        user=user,
        balance=balance,
        product_count=db.execute("SELECT COUNT(*) FROM products").fetchone()[0],
        transaction_count=db.execute("SELECT COUNT(*) FROM transactions").fetchone()[0],
        demo_phone=DEMO_PHONE,
        demo_password=DEMO_PASSWORD,
    )


@main.get("/health")
def health():
    get_db().execute("SELECT 1").fetchone()
    return jsonify(status="ok")


@main.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        phone = request.form.get("phone", "").strip()
        password = request.form.get("password", "")
        if not name or not phone.isdigit() or len(phone) != 10:
            flash("Enter a name and a 10 digit phone number.", "error")
            return render_template("register.html", name=name, phone=phone), 400
        if len(password) < MIN_PASSWORD_LENGTH:
            flash(f"Password must be at least {MIN_PASSWORD_LENGTH} characters.", "error")
            return render_template("register.html", name=name, phone=phone), 400
        db = get_db()
        if db.execute("SELECT 1 FROM users WHERE phone = ?", (phone,)).fetchone():
            flash("That phone number is already registered.", "error")
            return render_template("register.html", name=name, phone=phone), 400
        db.execute(
            "INSERT INTO users (name, phone, password_hash, role) VALUES (?, ?, ?, ?)",
            (name, phone, generate_password_hash(password), "seller"),
        )
        db.commit()
        flash("Account created. Please login.", "success")
        return redirect(url_for("main.login"))
    return render_template("register.html", name="", phone="")


@main.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        phone = request.form.get("phone", "").strip()
        password = request.form.get("password", "")
        user = get_db().execute("SELECT * FROM users WHERE phone = ?", (phone,)).fetchone()
        if user is None or not check_password_hash(user["password_hash"], password):
            current_app.logger.warning("login failed phone=%s", phone)
            flash("Invalid phone number or password.", "error")
            return render_template("login.html", phone=phone), 401
        session.clear()
        session["user_id"] = user["id"]
        current_app.logger.info("login success user_id=%s", user["id"])
        return redirect(url_for("main.index"))
    return render_template("login.html", phone="")


@main.post("/logout")
def logout():
    session.clear()
    flash("Logged out.", "success")
    return redirect(url_for("main.index"))


@main.route("/products", methods=["GET", "POST"])
def products():
    db = get_db()
    if request.method == "POST":
        if not session.get("user_id"):
            flash("Login required to add a product.", "error")
            return redirect(url_for("main.login"))
        name = request.form.get("name", "").strip()
        price = request.form.get("price", "").strip()
        stock = request.form.get("stock", "").strip()
        error = validate_product(name, price, stock)
        if error:
            flash(error, "error")
        else:
            db.execute(
                "INSERT INTO products (seller_id, name, price, stock) VALUES (?, ?, ?, ?)",
                (session["user_id"], name, float(price), int(stock)),
            )
            db.commit()
            flash("Product saved.", "success")
        return redirect(url_for("main.products"))
    rows = db.execute(
        "SELECT p.*, u.name AS seller_name FROM products p JOIN users u ON u.id = p.seller_id ORDER BY p.id DESC"
    ).fetchall()
    return render_template("products.html", products=rows)


@main.route("/transactions", methods=["GET", "POST"])
def transactions():
    db = get_db()
    user_id = session.get("user_id")
    if request.method == "POST":
        if not user_id:
            flash("Login required to record a transaction.", "error")
            return redirect(url_for("main.login"))
        kind = request.form.get("kind", "").strip()
        amount = request.form.get("amount", "").strip()
        note = request.form.get("note", "").strip()
        error = validate_transaction(kind, amount, user_id)
        if error:
            flash(error, "error")
        else:
            db.execute(
                "INSERT INTO transactions (user_id, kind, amount, note) VALUES (?, ?, ?, ?)",
                (user_id, kind, float(amount), note),
            )
            db.commit()
            flash(f"{kind.title()} recorded.", "success")
        return redirect(url_for("main.transactions"))
    rows = []
    if user_id:
        rows = db.execute(
            "SELECT * FROM transactions WHERE user_id = ? ORDER BY id DESC", (user_id,)
        ).fetchall()
    return render_template(
        "transactions.html",
        transactions=rows,
        balance=balance_for(user_id) if user_id else None,
    )


if __name__ == "__main__":
    create_app().run(debug=True)
