"""SQLite persistence for user accounts and profiles."""

import sqlite3
from contextlib import contextmanager
from datetime import datetime
from typing import Any, Generator, Optional

from config import DB_PATH


def _get_connection() -> sqlite3.Connection:
    """Create a SQLite connection with row factory enabled."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@contextmanager
def _get_db() -> Generator[sqlite3.Connection, None, None]:
    """Context manager yielding a database connection."""
    conn = _get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_user_db() -> None:
    """Create the users table if it does not exist."""
    with _get_db() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                phone TEXT DEFAULT '',
                profile_photo TEXT DEFAULT '',
                created_at TEXT NOT NULL
            )
            """
        )


def save_user(
    full_name: str,
    email: str,
    password_hash: str,
    salt: str,
    phone: str = "",
) -> int:
    """
    Create a new user account.

    Args:
        full_name: User display name.
        email: Unique email address.
        password_hash: Hashed password.
        salt: Password salt.
        phone: Optional phone number.

    Returns:
        Inserted user ID.
    """
    init_user_db()
    with _get_db() as conn:
        cursor = conn.execute(
            """
            INSERT INTO users (full_name, email, password_hash, salt, phone, profile_photo, created_at)
            VALUES (?, ?, ?, ?, ?, '', ?)
            """,
            (full_name, email, password_hash, salt, phone, datetime.utcnow().isoformat()),
        )
        return int(cursor.lastrowid)


def get_user_by_email(email: str) -> Optional[dict[str, Any]]:
    """
    Fetch a user by email address.

    Args:
        email: User email.

    Returns:
        User dictionary or None.
    """
    init_user_db()
    with _get_db() as conn:
        row = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        return dict(row) if row else None


def get_user_by_id(user_id: int) -> Optional[dict[str, Any]]:
    """
    Fetch a user by primary key.

    Args:
        user_id: User ID.

    Returns:
        User dictionary or None.
    """
    init_user_db()
    with _get_db() as conn:
        row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        return dict(row) if row else None


def update_user_profile(
    user_id: int,
    full_name: str,
    phone: str,
    profile_photo: Optional[str] = None,
) -> None:
    """
    Update user profile fields.

    Args:
        user_id: User primary key.
        full_name: Updated name.
        phone: Updated phone number.
        profile_photo: Base64 photo string; if None, photo is not changed.
    """
    init_user_db()
    with _get_db() as conn:
        if profile_photo is not None:
            conn.execute(
                """
                UPDATE users SET full_name = ?, phone = ?, profile_photo = ?
                WHERE id = ?
                """,
                (full_name, phone, profile_photo, user_id),
            )
        else:
            conn.execute(
                """
                UPDATE users SET full_name = ?, phone = ?
                WHERE id = ?
                """,
                (full_name, phone, user_id),
            )
