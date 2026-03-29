import logging
from typing import List, Dict, Any
from datetime import datetime
from app.db.db import get_db_connection, ensure_session

logger = logging.getLogger(__name__)

def save_user_turn(session_id: str, query: str):
    """
    Saves the user's latest query to the chat history.
    """
    ensure_session(session_id)
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO chat_messages (session_id, role, content) VALUES (%s, %s, %s)",
                (session_id, "user", query)
            )
        conn.commit()
    finally:
        conn.close()

def save_ai_turn(session_id: str, response: Dict[str, Any]):
    """
    Saves the AI's clinical assessment or follow-up to the history.
    """
    # Prefer follow-up question as the primary conversational bridge
    msg_content = response.get("follow_up_question") or response.get("explanation")
    
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO chat_messages (session_id, role, content) VALUES (%s, %s, %s)",
                (session_id, "assistant", msg_content)
            )
        conn.commit()
    finally:
        conn.close()

def get_history(session_id: str, limit: int = 10) -> List[Dict[str, str]]:
    """
    Retrieves the chronological context for a session.
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
