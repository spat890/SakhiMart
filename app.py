from pathlib import Path
from flask import Flask, render_template, request, redirect, url_for, flash, session, g
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

BASE_DIR = Path(__file__).resolve().parent
INSTANCE_DIR = BASE_DIR / "instance"
INSTANCE_DIR.mkdir(exist_ok=True)
DB_PATH = INSTANCE_DIR / "sakhimart.db"

app = Flask(__name__)
app.config["SECRET_KEY"] = "replace-this-development-key-before-deployment"
app.config["DATABASE"] = str(DB_PATH)


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


@app.teardown_appcontext
def close_db(_error=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = sqlite3.connect(app.config["DATABASE"])
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
    db.close()


@app.before_request
def load_user():
    user_id = session.get("user_id")
    g.user = get_db().execute(
        "SELECT id, name, username FROM users WHERE id = ?", (user_id,)
    ).fetchone() if user_id else None


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
        rows = db.execute(
            "SELECT kind, amount, note, created_at FROM transactions WHERE user_id=? ORDER BY id DESC LIMIT 5",
            (g.user["id"],)
        ).fetchall()
        recent_transactions = rows
        totals = db.execute("""
            SELECT
              COALESCE(SUM(CASE WHEN kind='deposit' THEN amount ELSE 0 END),0) -
              COALESCE(SUM(CASE WHEN kind='withdrawal' THEN amount ELSE 0 END),0) AS balance
            FROM transactions WHERE user_id=?
        """, (g.user["id"],)).fetchone()
        balance = totals["balance"]
    return render_template("index.html", products=products, balance=balance,
                           recent_transactions=recent_transactions)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        username = request.form.get("username", "").strip().lower()
        password = request.form.get("password", "")
        if not name or not username or len(password) < 8:
            flash("Enter all fields. Password must contain at least 8 characters.", "error")
            return render_template("register.html")
        try:
            db = get_db()
            db.execute(
                "INSERT INTO users(name, username, password_hash) VALUES (?, ?, ?)",
                (name, username, generate_password_hash(password))
            )
            db.commit()
            flash("Account created. Please log in.", "success")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("That username is already registered.", "error")
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
            flash("Logged in successfully.", "success")
            return redirect(url_for("index"))
        flash("Invalid username or password.", "error")
    return render_template("login.html")


@app.route("/logout")
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
        if not name or price < 0 or stock < 0:
            raise ValueError
    except ValueError:
        flash("Enter a product name, non-negative price and non-negative stock.", "error")
        return redirect(url_for("index"))
    db = get_db()
    db.execute(
        "INSERT INTO products(name, description, price, stock, seller_id) VALUES (?, ?, ?, ?, ?)",
        (name, description, price, stock, g.user["id"])
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
        if kind not in ("deposit", "withdrawal") or amount <= 0:
            raise ValueError
    except ValueError:
        flash("Choose a valid transaction type and enter an amount above zero.", "error")
        return redirect(url_for("index"))

    db = get_db()
    current = db.execute("""
        SELECT COALESCE(SUM(CASE WHEN kind='deposit' THEN amount ELSE -amount END),0) AS balance
        FROM transactions WHERE user_id=?
    """, (g.user["id"],)).fetchone()["balance"]
    if kind == "withdrawal" and amount > current:
        flash("Insufficient balance. Withdrawal was not recorded.", "error")
        return redirect(url_for("index"))
    db.execute(
        "INSERT INTO transactions(user_id, kind, amount, note) VALUES (?, ?, ?, ?)",
        (g.user["id"], kind, amount, note)
    )
    db.commit()
    flash("Savings transaction recorded.", "success")
    return redirect(url_for("index"))


@app.route("/health")
def health():
    return {"status": "ok", "database": "connected"}


if __name__ == "__main__":
    init_db()
    print("SakhiMart database:", DB_PATH)
    app.run(debug=True)
