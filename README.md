# Backend

Flask app with SQLite tables for users, products and transactions.

Routes: `/`, `/register`, `/login`, `/logout`, `/products`, `/transactions`, `/health`.

Run from the repository root:

```
python backend/app.py
```

Open http://127.0.0.1:5000 and login with phone `9000000000` and password `sakhi123`.

Tests:

```
python -m pytest backend
```

Database file: `backend/instance/sakhimart.db`.

Set `SAKHIMART_SECRET` to a private value before any shared or public deployment.
