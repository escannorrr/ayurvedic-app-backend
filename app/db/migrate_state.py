import logging
from app.db.db import get_db_connection

logger = logging.getLogger(__name__)

# Add 'state' column to the chat_sessions table
ADD_STATE_COLUMN_SQL = """
ALTER TABLE chat_sessions ADD COLUMN IF NOT EXISTS state VARCHAR(20) DEFAULT 'INITIAL';
"""

def run_state_migration():
    """
    Adds state management support to existing chat sessions.
    """
    logger.info("Running state migration for Clinical Flow...")
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(ADD_STATE_COLUMN_SQL)
        conn.commit()
        logger.info("State migration completed.")
    except Exception as e:
        conn.rollback()
        logger.error(f"State migration failed: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    logging.basicConfig(level=logging.INFO)
    run_state_migration()
