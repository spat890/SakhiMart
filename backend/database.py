"""Small database helper for scripts that need the SakhiMart SQLite database."""
from pathlib import Path
import sqlite3

DB_PATH = Path(__file__).resolve().parents[1] / "instance" / "sakhimart.db"

def connect():
    DB_PATH.parent.mkdir(exist_ok=True)
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection
