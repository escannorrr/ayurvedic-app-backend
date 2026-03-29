import logging
import json
import time
from typing import Any, Dict

# Create a dedicated logger for clinical traces
logger = logging.getLogger("clinical_trace")
logger.setLevel(logging.INFO)

# Ensure it doesn't duplicate to root if not needed, 
# but for now we want it in stdout for general debugging
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

def log_clinical_event(event_name: str, query: str, data: Dict[str, Any]):
    """
    Logs a structured clinical event for debugging and audit.
    """
    trace = {
        "event": event_name,
        "timestamp": time.time(),
        "query": query,
        "details": data
    }
    
    # Log as a compact JSON string for easy parsing by log aggregators
    logger.info(f"CLINICAL_TRACE: {json.dumps(trace)}")

def summarize_candidates(candidates: list) -> list:
    """Helper to log only relevant candidate info to keep logs clean."""
    return [
        {
            "name": c.get("name"),
            "vector": round(c.get("vector_score", 0), 3),
            "keyword": round(c.get("keyword_score", 0), 3),
            "dosha_rel": round(c.get("dosha_relevance", 0), 3),
            "total": round(c.get("final_ranking_score", 0), 4)
        }
        for c in candidates
    ]
