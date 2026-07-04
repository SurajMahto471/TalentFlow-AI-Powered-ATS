"""User authentication and profile management."""

import hashlib
import re
import secrets
from typing import Any, Optional

from database import get_user_by_email, get_user_by_id, save_user, update_user_profile

def hash_password(password: str, salt: Optional[str] = None) -> tuple[str, str]:
    """
    Hash a password using PBKDF2-HMAC-SHA256.

    Args:
        password: Plain-text password.
        salt: Optional existing salt for verification.

    Returns:
        Tuple of (password_hash, salt).
    """
    if salt is None:
        salt = secrets.token_hex(16)
    hashed = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        100_000,
    ).hex()
    return hashed, salt


def verify_password(password: str, password_hash: str, salt: str) -> bool:
    """
    Verify a plain-text password against a stored hash.

    Args:
        password: Plain-text password to check.
        password_hash: Stored password hash.
        salt: Stored salt.

    Returns:
        True if the password matches.
    """
    candidate_hash, _ = hash_password(password, salt)
    return secrets.compare_digest(candidate_hash, password_hash)


def is_valid_email(email: str) -> bool:
    """
    Validate email format.

    Args:
        email: Email address string.

    Returns:
        True if email format is valid.
    """
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email.strip()))


def register_user(
    full_name: str,
    email: str,
    password: str,
    phone: str = "",
) -> tuple[bool, str]:
    """
    Register a new user account.

    Args:
        full_name: User's display name.
        email: Unique email address.
        password: Plain-text password.
        phone: Optional phone number.

    Returns:
        Tuple of (success, message).
    """
   

    full_name = full_name.strip()
    email = email.strip().lower()
    phone = phone.strip()

    if not full_name:
        return False, "Full name is required."
    if not is_valid_email(email):
        return False, "Please enter a valid email address."
    if len(password) < 6:
        return False, "Password must be at least 6 characters."
    if get_user_by_email(email):
        return False, "An account with this email already exists."

    password_hash, salt = hash_password(password)
    save_user(full_name, email, password_hash, salt, phone)
    return True, "Account created successfully. Please log in."


def authenticate_user(email: str, password: str) -> tuple[bool, str, Optional[dict[str, Any]]]:
    """
    Authenticate a user with email and password.

    Args:
        email: Registered email address.
        password: Plain-text password.

    Returns:
        Tuple of (success, message, user_dict_or_none).
    """
    
    user = get_user_by_email(email.strip().lower())
    if not user:
        return False, "Invalid email or password.", None

    if not verify_password(password, user["password_hash"], user["salt"]):
        return False, "Invalid email or password.", None

    return True, "Login successful.", user


def update_profile(
    user_id: int,
    full_name: str,
    phone: str,
    profile_photo: Optional[str] = None,
) -> tuple[bool, str]:
    """
    Update a user's profile information.

    Args:
        user_id: User primary key.
        full_name: Updated display name.
        phone: Updated phone number.
        profile_photo: Optional base64-encoded profile photo.

    Returns:
        Tuple of (success, message).
    """
    if not full_name.strip():
        return False, "Full name cannot be empty."

    update_user_profile(
        user_id=user_id,
        full_name=full_name.strip(),
        phone=phone.strip(),
        profile_photo=profile_photo,
    )
    return True, "Profile updated successfully."


def get_user_profile(user_id: int) -> Optional[dict[str, Any]]:
    """
    Fetch the latest user profile from the database.

    Args:
        user_id: User primary key.

    Returns:
        User dictionary or None.
    """
    return get_user_by_id(user_id)
