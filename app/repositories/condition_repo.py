import logging
from typing import List, Dict, Any, Optional
from psycopg2.extras import DictCursor
from app.db.db import get_db_connection

logger = logging.getLogger(__name__)

class ConditionRepository:
    """
    Handles all database interactions for Ayurvedic conditions.
    """
    
    @staticmethod
    def get_all_conditions_for_search() -> List[Dict[str, Any]]:
        """
        Retrieves conditions with essential fields for similarity/keyword matching.
        """
        query = """
            SELECT 
                condition_name, 
                category,
                symptoms, 
                dosha,
                treatment_principles,
                diet,
                lifestyle,
                herbs,
                formulations,
                ai_content,
                embedding,
                search_text
            FROM conditions
        """
        results = []
        conn = None
        try:
            conn = get_db_connection()
            with conn.cursor(cursor_factory=DictCursor) as cursor:
                cursor.execute(query)
                rows = cursor.fetchall()
                for row in rows:
                    results.append(dict(row))
        except Exception as e:
            logger.error(f"ConditionRepository Error: {e}")
        finally:
            if conn: conn.close()
        return results

    @staticmethod
    def fetch_candidates_hybrid(query_text: str, query_embedding: List[float], limit: int = 15) -> List[Dict[str, Any]]:
        """
        Executes hybrid vector + keyword search.
        """
        if not query_embedding:
            return []
            
        sanitized_text = query_text.replace("'", "''")
        embedding_str = "[" + ",".join(map(str, query_embedding)) + "]"
        
        query = """
            SELECT 
                condition_name, 
                ai_content,
                symptoms,
                dosha,
                category,
                treatment_principles,
                diet,
                lifestyle,
                herbs,
                formulations,
                (1 - (embedding <=> %s::vector)) AS vector_score,
                ts_rank_cd(to_tsvector('english', COALESCE(search_text, '')), plainto_tsquery('english', %s), 32) AS keyword_score
            FROM conditions
            WHERE (1 - (embedding <=> %s::vector)) > 0.05
               OR to_tsvector('english', COALESCE(search_text, '')) @@ plainto_tsquery('english', %s)
            ORDER BY vector_score DESC
            LIMIT %s
        """
        
        results = []
        conn = None
        try:
            conn = get_db_connection()
            with conn.cursor(cursor_factory=DictCursor) as cursor:
                cursor.execute(query, (embedding_str, sanitized_text, embedding_str, sanitized_text, limit))
                rows = cursor.fetchall()
                for row in rows:
                    results.append(dict(row))
        except Exception as e:
            logger.error(f"ConditionRepository Hybrid Search Error: {e}")
        finally:
            if conn: conn.close()
        return results
