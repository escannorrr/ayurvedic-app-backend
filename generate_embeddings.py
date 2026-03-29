import os
import logging
from typing import Dict, Any, List
import psycopg2
from psycopg2.extras import DictCursor
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load model globally (singleton pattern) as per Performance Rules
MODEL_NAME = 'all-MiniLM-L6-v2'
logger.info(f"Loading embedding model '{MODEL_NAME}'...")
try:
    embedding_model = SentenceTransformer(MODEL_NAME)
    logger.info("Model loaded successfully.")
except Exception as e:
    logger.error(f"Failed to load embedding model: {e}")
    raise

def build_embedding_text(row: Dict[str, Any]) -> str:
    """
    Construct meaningful text for embedding from a database row.
    Ignores empty fields to avoid unnecessary verbosity or string "None".
    """
    parts = []
    
    def add_section(label: str, value: Any):
        if not value:
            return
        if isinstance(value, list):
            # For arrays like symptoms, causes
            cleaned_vals = [str(v).strip() for v in value if v]
            if not cleaned_vals:
                return
            formatted_val = ", ".join(cleaned_vals)
            parts.append(f"{label}: {formatted_val}")
        else:
            val_str = str(value).strip()
            if val_str:
                parts.append(f"{label}: {val_str}")

    add_section("Disease", row.get("condition_name"))
    add_section("Category", row.get("category"))
    add_section("Symptoms", row.get("symptoms"))
    add_section("Causes", row.get("causes"))
    add_section("Dosha", row.get("dosha"))
    add_section("Samprapti", row.get("samprapti"))
    add_section("Diagnosis Logic", row.get("diagnosis_logic"))
    add_section("Treatment Principles", row.get("treatment_principles"))
    add_section("Diet", row.get("diet"))
    add_section("Lifestyle", row.get("lifestyle"))
    add_section("Search Text", row.get("search_text"))

    return "\n".join(parts)

def generate_embedding(text: str) -> List[float]:
    """
    Generate embedding for the given text using the globally loaded model.
    Returns a list of floats (size matches VECTOR(384)).
    """
    embedding = embedding_model.encode(text)
    return embedding.tolist()

def main():
    """
    Main execution loop: connect to DB, fetch rows, generate embeddings,
    and update rows sequentially with safe error handling.
    """
    # Get database credentials safely from environment variables
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        db_user = os.getenv("DB_USER")
        db_password = os.getenv("DB_PASSWORD")
        db_host = os.getenv("DB_HOST", "localhost")
        db_port = os.getenv("DB_PORT", "5432")
        db_name = os.getenv("DB_NAME")
        
        if not all([db_user, db_password, db_name]):
            logger.error("Database credentials not fully provided in environment variables.")
            return
            
        db_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

    logger.info("Connecting to the database...")
    try:
        conn = psycopg2.connect(db_url)
    except Exception as e:
        logger.error(f"Failed to connect to the database: {e}")
        return

    try:
        with conn.cursor(cursor_factory=DictCursor) as fetch_cursor:
            # Read all rows from the conditions table
            # Adding category, samprapti, diagnosis_logic per the embedding text strategy
            fetch_cursor.execute("""
                SELECT 
                    id, condition_name, symptoms, causes, dosha, 
                    treatment_principles, diet, lifestyle, search_text,
                    category, samprapti, diagnosis_logic
                FROM conditions
            """)
            
            rows = fetch_cursor.fetchall()
            total_rows = len(rows)
            logger.info(f"Fetched {total_rows} rows from 'conditions' table.")

            for index, row in enumerate(rows, start=1):
                condition_id = row["id"]
                try:
                    # 1. Construct text
                    text_for_embedding = build_embedding_text(row)
                    
                    if not text_for_embedding.strip():
                        logger.warning(f"[{index}/{total_rows}] Skipping ID {condition_id}: Generated text is empty.")
                        continue
                        
                    # 2. Generate embedding (returns List[float])
                    embedding = generate_embedding(text_for_embedding)
                    
                    # 3. parameterized query to prevent SQL injection
                    with conn.cursor() as update_cursor:
                        update_cursor.execute(
                            """
                            UPDATE conditions 
                            SET embedding = %s 
                            WHERE id = %s
                            """,
                            (embedding, condition_id)
                        )
                    
                    # 4. Commit after each update
                    conn.commit()
                    logger.info(f"[{index}/{total_rows}] Successfully updated embedding for ID: {condition_id}")
                    
                except Exception as row_error:
                    logger.error(f"[{index}/{total_rows}] Error processing ID {condition_id}: {row_error}")
                    # Rollback the specific failed row transaction and continue
                    conn.rollback() 

    except Exception as e:
        logger.error(f"A fatal error occurred during execution: {e}")
    finally:
        if conn:
            conn.close()
            logger.info("Database connection closed.")

if __name__ == "__main__":
    main()
