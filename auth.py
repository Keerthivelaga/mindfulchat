"""
MindfulChat — Authentication Module (bcrypt)
"""

import bcrypt
import database as db


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    """Verify a password against its bcrypt hash."""
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))


def register_user(username: str, password: str, display_name: str,
                  emergency_contact_name: str = "",
                  emergency_contact_phone: str = "",
                  emergency_contact_email: str = "") -> dict:
    """
    Register a new user. Returns dict with 'success' and 'message'.
    Emergency contact is MANDATORY.
    """
    if not username or not password:
        return {"success": False, "message": "Username and password are required."}

    if len(password) < 6:
        return {"success": False, "message": "Password must be at least 6 characters."}

    if len(username) < 3:
        return {"success": False, "message": "Username must be at least 3 characters."}

    # Emergency contact is REQUIRED
    if not emergency_contact_name or not emergency_contact_name.strip():
        return {"success": False, "message": "⚠️ Emergency contact name is required for your safety."}

    if not emergency_contact_phone or not emergency_contact_phone.strip():
        return {"success": False, "message": "⚠️ Emergency contact phone number is required."}

    # Check if user already exists
    existing = db.get_user(username)
    if existing:
        return {"success": False, "message": "Username already taken."}

    password_hash = hash_password(password)
    created = db.create_user(
        username=username,
        password_hash=password_hash,
        display_name=display_name or username,
        emergency_contact_name=emergency_contact_name.strip(),
        emergency_contact_phone=emergency_contact_phone.strip(),
        emergency_contact_email=emergency_contact_email.strip(),
    )

    if created:
        return {"success": True, "message": "Account created successfully!"}
    else:
        return {"success": False, "message": "Could not create account. Try a different username."}


def login_user(username: str, password: str) -> dict:
    """
    Authenticate a user. Returns dict with 'success', 'message', and 'user' (if successful).
    """
    if not username or not password:
        return {"success": False, "message": "Please enter both username and password.", "user": None}

    user = db.get_user(username)
    if not user:
        return {"success": False, "message": "Invalid username or password.", "user": None}

    if verify_password(password, user["password_hash"]):
        # Return user data without the password hash
        safe_user = {k: v for k, v in user.items() if k != "password_hash"}
        return {"success": True, "message": "Login successful!", "user": safe_user}
    else:
        return {"success": False, "message": "Invalid username or password.", "user": None}
