"""SakhiMart Flask application.

Run locally with: python app.py
For WSGI deployments, point the server at app:app.
"""
import os
import sqlite3
from pathlib import Path

from flask import Flask, flash, g, jsonify, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from security.audit_logger import log_login_failure, log_login_success
from ai.business_advisor.dashboard import advisor_bp

BASE_DIR = Path(__file__).resolve().parent
INSTANCE_DIR = BASE_DIR / "instance"
INSTANCE_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = INSTANCE_DIR / "sakhimart.db"

app = Flask(__name__)
app.config.update(
    SECRET_KEY=os.environ.get("SAKHIMART_SECRET_KEY", "local-development-only-change-me"),
    DATABASE=os.environ.get("SAKHIMART_DATABASE", str(DB_PATH)),
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
)
app.register_blueprint(advisor_bp)


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(app.config["DATABASE"], timeout=10)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
        g.db.execute("PRAGMA busy_timeout = 10000")
    return g.db


@app.teardown_appcontext
def close_db(_error=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


_initialized_databases = set()


def init_db():
    """Create the application tables once for each configured database path."""
    database = str(Path(app.config["DATABASE"]).resolve())
    if database in _initialized_databases:
        return
    Path(database).parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(database, timeout=10)
    try:
        db.execute("PRAGMA foreign_keys = ON")
        db.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT DEFAULT '',
                price REAL NOT NULL CHECK(price >= 0),
                stock INTEGER NOT NULL DEFAULT 0 CHECK(stock >= 0),
                seller_id INTEGER,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(seller_id) REFERENCES users(id)
            );
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                kind TEXT NOT NULL CHECK(kind IN ('deposit', 'withdrawal')),
                amount REAL NOT NULL CHECK(amount > 0),
                note TEXT DEFAULT '',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id)
            );
        """)
        db.commit()
        _initialized_databases.add(database)
    finally:
        db.close()


@app.before_request
def prepare_request():
    # Also initializes the database under WSGI/test servers, not only python app.py.
    init_db()
    user_id = session.get("user_id")
    g.user = (
        get_db().execute(
            "SELECT id, name, username FROM users WHERE id = ?", (user_id,)
        ).fetchone()
        if user_id else None
    )


@app.route("/")
def index():
    db = get_db()
    products = db.execute("""
        SELECT products.*, users.name AS seller_name
        FROM products LEFT JOIN users ON products.seller_id = users.id
        ORDER BY products.id DESC
    """).fetchall()
    balance = 0.0
    recent_transactions = []
    if g.user:
        recent_transactions = db.execute(
            "SELECT kind, amount, note, created_at FROM transactions "
            "WHERE user_id=? ORDER BY id DESC LIMIT 5",
            (g.user["id"],),
        ).fetchall()
        totals = db.execute("""
            SELECT COALESCE(
                SUM(CASE WHEN kind='deposit' THEN amount ELSE -amount END), 0
            ) AS balance
            FROM transactions WHERE user_id=?
        """, (g.user["id"],)).fetchone()
        balance = totals["balance"]
    return render_template(
        "index.html", products=products, balance=balance,
        recent_transactions=recent_transactions,
    )


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        username = request.form.get("username", "").strip().lower()
        password = request.form.get("password", "")
        if not name or not username or len(username) > 40 or len(password) < 8:
            flash("Enter a name and username. Password must contain at least 8 characters.", "error")
            return render_template("register.html"), 400
        try:
            db = get_db()
            db.execute(
                "INSERT INTO users(name, username, password_hash) VALUES (?, ?, ?)",
                (name, username, generate_password_hash(password)),
            )
            db.commit()
            flash("Account created. Please log in.", "success")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("That username is already registered.", "error")
            return render_template("register.html"), 409
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip().lower()
        password = request.form.get("password", "")
        user = get_db().execute(
            "SELECT * FROM users WHERE username=?", (username,)
        ).fetchone()
        if user and check_password_hash(user["password_hash"], password):
            session.clear()
            session["user_id"] = user["id"]
            session.permanent = True
            log_login_success(username)
            flash("Logged in successfully.", "success")
            return redirect(url_for("index"))
        log_login_failure(username or "UNKNOWN")
        flash("Invalid username or password.", "error")
    return render_template("login.html")


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("index"))


@app.route("/products/add", methods=["POST"])
def add_product():
    if not g.user:
        flash("Please log in before adding a product.", "error")
        return redirect(url_for("login"))
    name = request.form.get("name", "").strip()
    description = request.form.get("description", "").strip()
    try:
        price = float(request.form.get("price", ""))
        stock = int(request.form.get("stock", ""))
        if not name or len(name) > 100 or len(description) > 250:
            raise ValueError
        if price < 0 or stock < 0:
            raise ValueError
    except (ValueError, TypeError):
        flash("Enter a valid product name, non-negative price and non-negative stock.", "error")
        return redirect(url_for("index"))
    db = get_db()
    db.execute(
        "INSERT INTO products(name, description, price, stock, seller_id) VALUES (?, ?, ?, ?, ?)",
        (name, description, price, stock, g.user["id"]),
    )
    db.commit()
    flash("Product added to the marketplace.", "success")
    return redirect(url_for("index"))


@app.route("/savings/add", methods=["POST"])
def add_savings():
    if not g.user:
        flash("Please log in to record a savings transaction.", "error")
        return redirect(url_for("login"))
    kind = request.form.get("kind", "")
    note = request.form.get("note", "").strip()
    try:
        amount = float(request.form.get("amount", ""))
        if kind not in ("deposit", "withdrawal") or not (0 < amount < 1_000_000_000):
            raise ValueError
    except (ValueError, TypeError):
        flash("Choose a valid transaction type and enter an amount above zero.", "error")
        return redirect(url_for("index"))

    db = get_db()
    try:
        # Serialize balance-check + insert so simultaneous withdrawals cannot
        # both spend the same available balance.
        db.execute("BEGIN IMMEDIATE")
        current = db.execute("""
            SELECT COALESCE(
                SUM(CASE WHEN kind='deposit' THEN amount ELSE -amount END), 0
            ) AS balance
            FROM transactions WHERE user_id=?
        """, (g.user["id"],)).fetchone()["balance"]
        if kind == "withdrawal" and amount > current:
            db.rollback()
            flash("Insufficient balance. Withdrawal was not recorded.", "error")
            return redirect(url_for("index"))
        db.execute(
            "INSERT INTO transactions(user_id, kind, amount, note) VALUES (?, ?, ?, ?)",
            (g.user["id"], kind, amount, note[:120]),
        )
        db.commit()
    except Exception:
        db.rollback()
        raise
    flash("Savings transaction recorded.", "success")
    return redirect(url_for("index"))


@app.route("/health")
def health():
    try:
        get_db().execute("SELECT 1").fetchone()
        return jsonify(status="ok", database="connected"), 200
    except sqlite3.Error:
        app.logger.exception("Database health check failed")
        return jsonify(status="error", database="unavailable"), 503


if __name__ == "__main__":
    init_db()
    print("SakhiMart database:", app.config["DATABASE"])
    app.run(
        host="127.0.0.1",
        port=int(os.environ.get("PORT", "5000")),
        debug=os.environ.get("FLASK_DEBUG", "0") == "1",
    )
