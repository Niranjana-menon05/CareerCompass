import sqlite3
import hashlib
import json
import os

DB_PATH = "users.db"


def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            email    TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS user_profiles (
            username     TEXT PRIMARY KEY,
            profile_json TEXT,
            updated_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


def _hash(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def register_user(username: str, password: str, email: str = "") -> tuple[bool, str]:
    if len(username) < 3:
        return False, "Username must be at least 3 characters."
    if len(password) < 6:
        return False, "Password must be at least 6 characters."
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute(
            "INSERT INTO users (username, password, email) VALUES (?, ?, ?)",
            (username.strip(), _hash(password), email.strip())
        )
        conn.commit()
        return True, "Account created successfully."
    except sqlite3.IntegrityError:
        return False, "Username already taken."
    finally:
        conn.close()


def login_user(username: str, password: str) -> bool:
    conn = sqlite3.connect(DB_PATH)
    row = conn.execute(
        "SELECT password FROM users WHERE username = ?", (username.strip(),)
    ).fetchone()
    conn.close()
    return row is not None and row[0] == _hash(password)


def save_profile(username: str, profile: dict):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        INSERT INTO user_profiles (username, profile_json)
        VALUES (?, ?)
        ON CONFLICT(username) DO UPDATE SET
            profile_json = excluded.profile_json,
            updated_at   = CURRENT_TIMESTAMP
    """, (username, json.dumps(profile)))
    conn.commit()
    conn.close()


def load_profile(username: str) -> dict | None:
    conn = sqlite3.connect(DB_PATH)
    row = conn.execute(
        "SELECT profile_json FROM user_profiles WHERE username = ?", (username,)
    ).fetchone()
    conn.close()
    return json.loads(row[0]) if row else None
