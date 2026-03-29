import logging
from app.db.db import get_db_connection

logger = logging.getLogger(__name__)

# Use VARCHAR for session_id to support flexible identifiers (UUIDs, custom strings, etc.)
CREATE_SESSION_TABLES_SQL = """
CREATE TABLE IF NOT EXISTS chat_sessions (
    id VARCHAR(128) PRIMARY KEY,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS chat_messages (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(128) REFERENCES chat_sessions(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_chat_messages_session_id ON chat_messages(session_id);
"""

# Migration to convert UUID to VARCHAR if tables already exist
ALTER_SESSION_TABLES_SQL = """
DO $$ 
BEGIN 
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='chat_sessions' AND column_name='id' AND data_type='uuid') THEN
        ALTER TABLE chat_messages DROP CONSTRAINT IF EXISTS chat_messages_session_id_fkey;
        ALTER TABLE chat_sessions ALTER COLUMN id TYPE VARCHAR(128);
        ALTER TABLE chat_messages ALTER COLUMN session_id TYPE VARCHAR(128);
        ALTER TABLE chat_messages ADD CONSTRAINT chat_messages_session_id_fkey FOREIGN KEY (session_id) REFERENCES chat_sessions(id) ON DELETE CASCADE;
    END IF;
END $$;
"""

def run_migrations():
    """
    Executes the database migrations to support multi-turn conversational AI.
    Handles both fresh installations and UUID-to-VARCHAR conversions.
    """
    logger.info("Running database migrations for Session Management...")
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(CREATE_SESSION_TABLES_SQL)
            cur.execute(ALTER_SESSION_TABLES_SQL)
        conn.commit()
        logger.info("Migrations completed successfully.")
    except Exception as e:
        conn.rollback()
        logger.error(f"Migration failed: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    load_dotenv()
    logging.basicConfig(level=logging.INFO)
    run_migrations()
