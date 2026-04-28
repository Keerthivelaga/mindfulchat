"""
MindfulChat — SQLite Database Module
"""

import sqlite3
import datetime
from config import DB_PATH


def get_connection():
    """Get a SQLite connection with row_factory for dict-like access."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    """Create all tables if they don't exist."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            display_name TEXT NOT NULL,
            emergency_contact_name TEXT DEFAULT '',
            emergency_contact_phone TEXT DEFAULT '',
            emergency_contact_email TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT DEFAULT 'New Conversation',
            started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id INTEGER NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('user', 'bot')),
            content TEXT NOT NULL,
            distress_level TEXT DEFAULT 'neutral',
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (conversation_id) REFERENCES conversations(id)
        );

        CREATE TABLE IF NOT EXISTS journal_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            content TEXT NOT NULL,
            mood TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS mood_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            mood TEXT NOT NULL,
            note TEXT DEFAULT '',
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS emergency_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            message_excerpt TEXT NOT NULL,
            distress_level TEXT NOT NULL,
            alert_sent_to TEXT DEFAULT '',
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
    """)

    conn.commit()
    conn.close()


# ─── User Operations ───

def create_user(username, password_hash, display_name,
                emergency_contact_name="", emergency_contact_phone="",
                emergency_contact_email=""):
    conn = get_connection()
    try:
        conn.execute(
            """INSERT INTO users (username, password_hash, display_name,
               emergency_contact_name, emergency_contact_phone, emergency_contact_email)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (username, password_hash, display_name,
             emergency_contact_name, emergency_contact_phone, emergency_contact_email)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def get_user(username):
    conn = get_connection()
    row = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    conn.close()
    return dict(row) if row else None


def update_emergency_contact(user_id, name, phone, email):
    conn = get_connection()
    conn.execute(
        """UPDATE users SET emergency_contact_name=?, emergency_contact_phone=?,
           emergency_contact_email=? WHERE id=?""",
        (name, phone, email, user_id)
    )
    conn.commit()
    conn.close()


# ─── Conversation Operations ───

def create_conversation(user_id, title="New Conversation"):
    conn = get_connection()
    cursor = conn.execute(
        "INSERT INTO conversations (user_id, title) VALUES (?, ?)",
        (user_id, title)
    )
    conv_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return conv_id


def get_user_conversations(user_id):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM conversations WHERE user_id=? ORDER BY started_at DESC",
        (user_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def save_message(conversation_id, role, content, distress_level="neutral"):
    conn = get_connection()
    conn.execute(
        """INSERT INTO messages (conversation_id, role, content, distress_level)
           VALUES (?, ?, ?, ?)""",
        (conversation_id, role, content, distress_level)
    )
    conn.commit()
    conn.close()


def get_conversation_messages(conversation_id):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM messages WHERE conversation_id=? ORDER BY timestamp ASC",
        (conversation_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ─── Journal Operations ───

def save_journal_entry(user_id, content, mood=""):
    conn = get_connection()
    conn.execute(
        "INSERT INTO journal_entries (user_id, content, mood) VALUES (?, ?, ?)",
        (user_id, content, mood)
    )
    conn.commit()
    conn.close()


def get_journal_entries(user_id):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM journal_entries WHERE user_id=? ORDER BY created_at DESC",
        (user_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def delete_journal_entry(entry_id, user_id):
    conn = get_connection()
    conn.execute(
        "DELETE FROM journal_entries WHERE id=? AND user_id=?",
        (entry_id, user_id)
    )
    conn.commit()
    conn.close()


# ─── Mood Operations ───

def log_mood(user_id, mood, note=""):
    conn = get_connection()
    conn.execute(
        "INSERT INTO mood_logs (user_id, mood, note) VALUES (?, ?, ?)",
        (user_id, mood, note)
    )
    conn.commit()
    conn.close()


def get_mood_history(user_id, days=30):
    conn = get_connection()
    cutoff = (datetime.datetime.now() - datetime.timedelta(days=days)).isoformat()
    rows = conn.execute(
        "SELECT * FROM mood_logs WHERE user_id=? AND timestamp>=? ORDER BY timestamp ASC",
        (user_id, cutoff)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ─── Emergency Log Operations ───

def log_emergency(user_id, message_excerpt, distress_level, alert_sent_to=""):
    conn = get_connection()
    conn.execute(
        """INSERT INTO emergency_logs (user_id, message_excerpt, distress_level, alert_sent_to)
           VALUES (?, ?, ?, ?)""",
        (user_id, message_excerpt, distress_level, alert_sent_to)
    )
    conn.commit()
    conn.close()


def get_emergency_logs(user_id):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM emergency_logs WHERE user_id=? ORDER BY timestamp DESC",
        (user_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]
