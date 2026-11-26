
"""Shared database connection helper for SakhiMart."""

import os
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]

DB_PATH = Path(
    os.environ.get(
        "SAKHIMART_DATABASE",
        str(BASE_DIR / "instance" / "sakhimart.db")
    )
)


def connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(str(DB_PATH), timeout=10)
    connection.row_factory = sqlite3.Row

    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute("PRAGMA busy_timeout = 10000")

    return connection

