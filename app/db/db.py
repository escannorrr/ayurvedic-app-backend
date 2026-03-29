import os
import psycopg2
from typing import List, Dict, Any

def get_db_connection():
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        db_user = os.getenv("DB_USER")
        db_password = os.getenv("DB_PASSWORD")
        db_host = os.getenv("DB_HOST", "localhost")
        db_port = os.getenv("DB_PORT", "5432")
        db_name = os.getenv("DB_NAME")
        if not all([db_user, db_password, db_name]):
            raise ValueError("Database credentials not fully provided in environment variables.")
        db_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    
    return psycopg2.connect(db_url)

def ensure_session(session_id: str):
    """
    Ensures a chat session exists in the database.
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO chat_sessions (id) VALUES (%s) ON CONFLICT (id) DO NOTHING",
                (session_id,)
            )
        conn.commit()
    finally:
        conn.close()

def update_session_state(session_id: str, state: str):
    """
    Updates the clinical state of a session.
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE chat_sessions SET state = %s, updated_at = CURRENT_TIMESTAMP WHERE id = %s",
                (state, session_id)
            )
        conn.commit()
    finally:
        conn.close()

def get_session_state(session_id: str) -> str:
    """
    Retrieves the current clinical state of a session.
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT state FROM chat_sessions WHERE id = %s", (session_id,))
            row = cur.fetchone()
            return row[0] if row else "INITIAL"
    finally:
        conn.close()

def save_message(session_id: str, role: str, content: str):
    """
    Saves a message to the database for persistent history.
    """
    ensure_session(session_id)
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO chat_messages (session_id, role, content) VALUES (%s, %s, %s)",
                (session_id, role, content)
            )
        conn.commit()
    finally:
        conn.close()

def get_chat_history(session_id: str, limit: int = 10) -> List[Dict[str, str]]:
    """
    Retrieves the recent chat history for a session.
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT role, content FROM chat_messages WHERE session_id = %s ORDER BY created_at ASC LIMIT %s",
                (session_id, limit)
            )
            rows = cur.fetchall()
            return [{"role": row[0], "content": row[1]} for row in rows]
    finally:
        conn.close()
