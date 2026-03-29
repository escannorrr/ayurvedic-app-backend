import logging
import functools
from typing import List
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

# Singleton pattern for the embedding model
MODEL_NAME = 'all-MiniLM-L6-v2'
_model = None

def get_model() -> SentenceTransformer:
    """
    Returns the singleton instance of the embedding model.
    Loads it lazily on first call.
    """
    global _model
    if _model is None:
        logger.info(f"Loading embedding model '{MODEL_NAME}'...")
        try:
            _model = SentenceTransformer(MODEL_NAME)
            logger.info("Embedding model loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            raise
    return _model

@functools.lru_cache(maxsize=128)
def generate_embedding(text: str) -> List[float]:
    """
    Generates an embedding for a given text string.
    Uses @lru_cache and the singleton model.
    """
    if not text or not text.strip():
        logger.error("Text for embedding is empty.")
        return []
    
    model = get_model()
    embedding = model.encode(text)
    return embedding.tolist()
