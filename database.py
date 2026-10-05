"""SQLite operations for the Lab 5 user API."""
import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path

DATABASE = Path(os.environ.get("LAB5_DATABASE", Path(__file__).with_name("database.db")))


@contextmanager
def connect_to_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    try:
        with conn:
            yield conn
    finally:
        conn.close()


def create_db_table():
    with connect_to_db() as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL, email TEXT NOT NULL, phone TEXT NOT NULL,
            address TEXT NOT NULL, country TEXT NOT NULL
        )""")


def insert_user(user):
    with connect_to_db() as conn:
        cur = conn.execute(
            "INSERT INTO users (name, email, phone, address, country) VALUES (?, ?, ?, ?, ?)",
            tuple(user[key] for key in ("name", "email", "phone", "address", "country")),
        )
        return dict(conn.execute("SELECT * FROM users WHERE user_id = ?", (cur.lastrowid,)).fetchone())


def get_users():
    with connect_to_db() as conn:
        return [dict(row) for row in conn.execute("SELECT * FROM users ORDER BY user_id")]


def get_user_by_id(user_id):
    with connect_to_db() as conn:
        row = conn.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchone()
        return dict(row) if row else None


def update_user(user):
    with connect_to_db() as conn:
        cur = conn.execute(
            "UPDATE users SET name = ?, email = ?, phone = ?, address = ?, country = ? WHERE user_id = ?",
            tuple(user[key] for key in ("name", "email", "phone", "address", "country", "user_id")),
        )
        if not cur.rowcount:
            return None
        return dict(conn.execute("SELECT * FROM users WHERE user_id = ?", (user["user_id"],)).fetchone())


def delete_user(user_id):
    with connect_to_db() as conn:
        return conn.execute("DELETE FROM users WHERE user_id = ?", (user_id,)).rowcount > 0


if __name__ == "__main__":
    create_db_table()
    print(f"Database ready: {DATABASE}")
