"""SQLite operations for the Lab 5 user API, tested in Lab 7."""
import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path

DATABASE = Path(os.environ.get("LAB5_DATABASE", Path(__file__).with_name("database.db")))

# The sample user documented in the Lab 5 project's README and Postman examples.
INITIAL_USERS = (
    {
        "name": "John Doe",
        "email": "john@example.com",
        "phone": "067765434567",
        "address": "John Doe Street, Innsbruck",
        "country": "Austria",
    },
)


@contextmanager
def connect_to_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    try:
        with conn:
            yield conn
    finally:
        conn.close()


def create_db_table(initial_users=()):
    """Create the table; add initial users only when the table is first created."""
    with connect_to_db() as conn:
        table_exists = conn.execute(
            "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'users'"
        ).fetchone() is not None
        conn.execute("""CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL, email TEXT NOT NULL, phone TEXT NOT NULL,
            address TEXT NOT NULL, country TEXT NOT NULL
        )""")
        if not table_exists:
            conn.executemany(
                "INSERT INTO users (name, email, phone, address, country) VALUES (?, ?, ?, ?, ?)",
                [tuple(user[key] for key in ("name", "email", "phone", "address", "country"))
                 for user in initial_users],
            )


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


def patch_user(user_id, changes):
    # Column names come only from this fixed allowlist; values stay parameterized.
    fields = [key for key in ("name", "email", "phone", "address", "country") if key in changes]
    if not fields:
        raise ValueError("Provide at least one user field")
    assignments = ", ".join(f"{key} = ?" for key in fields)
    with connect_to_db() as conn:
        cur = conn.execute(f"UPDATE users SET {assignments} WHERE user_id = ?",
                           tuple(changes[key] for key in fields) + (user_id,))
        if not cur.rowcount:
            return None
        return dict(conn.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchone())


if __name__ == "__main__":
    create_db_table(INITIAL_USERS)
    print(f"Database ready: {DATABASE}")
