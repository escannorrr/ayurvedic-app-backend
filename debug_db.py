import os
import sys
import logging
from app.db.db import get_db_connection
from app.services.embedding_service import generate_embedding
from psycopg2.extras import DictCursor
from dotenv import load_dotenv

# Ensure we can import from the app directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

load_dotenv(override=True)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def debug_retrieval(query_text):
    print(f"\n--- Debugging Retrieval for: '{query_text}' ---")
    
    # 1. Check if model is working
    query_vector = generate_embedding(query_text)
    print(f"Generated Vector Length: {len(query_vector) if query_vector else 'FAILED'}")

    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=DictCursor) as cur:
            # 2. Check total records
            cur.execute("SELECT COUNT(*) FROM conditions")
            total = cur.fetchone()[0]
            print(f"Total conditions in DB: {total}")

            # 3. Check for specific conditions
            cur.execute("SELECT condition_name, (embedding IS NOT NULL) as has_vector FROM conditions")
            rows = cur.fetchall()
            print("\nConditions present in DB:")
            for r in rows:
                print(f" - {r['condition_name']} | Vector: {r['has_vector']}")

            # 4. Check raw similarity
            # Using <=> for cosine distance, so 1 - distance = similarity
            cur.execute("""
                SELECT condition_name, 
                       1 - (embedding <=> %s::vector) AS similarity 
                FROM conditions 
                WHERE embedding IS NOT NULL
                ORDER BY similarity DESC;
            """, (query_vector,))
            results = cur.fetchall()
            print("\nSimilarity Scores (Descending):")
            for r in results:
                print(f" - {r['condition_name']}: {r['similarity']:.4f}")

    finally:
        conn.close()

if __name__ == "__main__":
    debug_retrieval("I have anxiety and fatigue")
