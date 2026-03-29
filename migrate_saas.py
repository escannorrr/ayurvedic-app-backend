import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Load environment before creating engine
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL not found in environment")

engine = create_engine(DATABASE_URL)

def migrate():
    """
    Manually add missing columns to the users table.
    """
    with engine.connect() as conn:
        print(f"Connecting to {DATABASE_URL}...")
        print("Checking for missing columns in 'users' and 'cases' tables...")
        
        try:
            # Postgres specific ALTER TABLE to add missing columns
            # We use try-except to avoid errors if columns already exist
            conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS clinic_name VARCHAR;"))
            conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS preferences JSONB;"))
            
            # Record migrations for cases table
            conn.execute(text("ALTER TABLE cases ADD COLUMN IF NOT EXISTS status VARCHAR DEFAULT 'Complete';"))
            conn.execute(text("ALTER TABLE cases ADD COLUMN IF NOT EXISTS clinical_notes TEXT;"))
            conn.execute(text("ALTER TABLE cases ADD COLUMN IF NOT EXISTS timeline JSONB;"))
            conn.execute(text("ALTER TABLE cases ADD COLUMN IF NOT EXISTS attachments JSONB;"))
            
            conn.commit()
            print("Migration successful! Columns synced.")
        except Exception as e:
            print(f"Migration error: {e}")

if __name__ == "__main__":
    migrate()
