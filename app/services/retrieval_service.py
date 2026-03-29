import os
import logging
import psycopg2
from psycopg2.extras import DictCursor
from typing import List, Dict, Any
from app.db.db import get_db_connection

logger = logging.getLogger(__name__)

# Configurable Weights
WEIGHT_VECTOR = 0.4
WEIGHT_KEYWORD = 0.3
WEIGHT_DOSHA = 0.3

def calculate_dosha_relevance(text: str, dosha_scores: Dict[str, float]) -> float:
    """
    Calculates how relevant a condition text is to the user's analyzed doshas.
    Checks for keywords like 'Vata', 'Pitta', 'Kapha', 'Hot', 'Dry', etc.
    """
    if not text or not dosha_scores:
        return 0.0
    
    relevance = 0.0
    text_lower = text.lower()
    
    # Simple Dosha keyword groups
    keywords = {
        "vata": ["vata", "dry", "cold", "anxiety", "pain", "movement", "air", "wind"],
        "pitta": ["pitta", "heat", "burning", "inflammation", "acid", "sour", "fire"],
        "kapha": ["kapha", "heavy", "lethargy", "mucoid", "stagnation", "cold", "water", "earth"]
    }
    
    for dosha, score in dosha_scores.items():
        if score <= 0.1: continue
        
        # Check for dosha name and associated quality keywords
        matches = 0
        for kw in keywords.get(dosha, []):
            if kw in text_lower:
                matches += 1
        
        # Relevance is a factor of the user's score and the frequency of keyword matches
        # Capped at 1.0 per dosha
        dosha_relevance = min(1.0, (matches * 0.2)) * score
        relevance += dosha_relevance
        
    return min(1.0, relevance)

def rank_diseases(candidates: List[Dict[str, Any]], query_dosha_scores: Dict[str, float]) -> List[Dict[str, Any]]:
    """
    Weighted scoring system:
    - 40% Vector Similarity
    - 30% Keyword Score
    - 30% Dosha Relevance
    """
    logger.info(f"Reranking {len(candidates)} candidates using 40/30/30 model...")
    
    ranked = []
    for c in candidates:
        dosha_rel = calculate_dosha_relevance(
            f"{c['name']} {c['description']} {c['symptoms']}", 
            query_dosha_scores
        )
        
        # Combine scores
        final_score = (
            (WEIGHT_VECTOR * c.get("vector_score", 0)) +
            (WEIGHT_KEYWORD * c.get("keyword_score", 0)) +
            (WEIGHT_DOSHA * dosha_rel)
        )
        
        c["dosha_relevance"] = round(dosha_rel, 4)
        c["vector_score"] = round(c.get("vector_score", 0), 4)
        c["keyword_score"] = round(c.get("keyword_score", 0), 4)
        c["final_ranking_score"] = round(final_score, 4)
        ranked.append(c)
        
    # Deterministic Sort:
    # 1. Final Score (DESC)
    # 2. Keyword Score (DESC)
    # 3. Name (ASC - alphabetical)
    ranked.sort(key=lambda x: (-x["final_ranking_score"], -x["keyword_score"], x["name"]))
    return ranked

def hybrid_search(query_text: str, query_embedding: List[float], limit: int = 10) -> List[Dict[str, Any]]:
    """
    Initial hybrid search to gather candidates for reranking.
    """
    if not query_embedding or not query_text:
        return []

    sanitized_text = query_text.replace("'", "''")
    query_sql = """
        SELECT 
            condition_name, 
            ai_content,
            symptoms,
            herbs,
            formulations,
            treatment_principles,
            diet,
            lifestyle,
            (1 - (embedding <=> %s::vector)) AS vector_score,
            ts_rank_cd(to_tsvector('english', COALESCE(search_text, '')), plainto_tsquery('english', %s), 32) AS keyword_score
        FROM conditions
        WHERE (1 - (embedding <=> %s::vector)) > 0.1
           OR to_tsvector('english', COALESCE(search_text, '')) @@ plainto_tsquery('english', %s)
        ORDER BY vector_score DESC
        LIMIT %s
    """
    
    results = []
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            embedding_str = "[" + ",".join(map(str, query_embedding)) + "]"
            cursor.execute(query_sql, (embedding_str, sanitized_text, embedding_str, sanitized_text, limit))
            rows = cursor.fetchall()
            
            for row in rows:
                results.append({
                    "name": row["condition_name"],
                    "description": row["ai_content"],
                    "symptoms": row["symptoms"],
                    "herbs": row["herbs"] or [],
                    "formulations": row["formulations"] or [],
                    "principles": row["treatment_principles"] or [],
                    "diet": row["diet"] or [],
                    "lifestyle": row["lifestyle"] or [],
                    "vector_score": float(row["vector_score"]),
                    "keyword_score": float(row["keyword_score"])
                })
    except Exception as e:
        logger.error(f"Search candidates retrieval failure: {e}")
    finally:
        if conn: conn.close()
            
    return results
