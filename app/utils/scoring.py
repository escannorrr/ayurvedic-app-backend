import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

# Weight Configuration (Requirement #3)
WEIGHT_CHECKLIST = 0.4
WEIGHT_EMBEDDING = 0.3
WEIGHT_DOSHA = 0.1
WEIGHT_PRAKRITI = 0.1
WEIGHT_DURATION = 0.1

def calculate_checklist_match(patient_symptoms: List[str], condition_symptoms: List[str]) -> float:
    """Requirement 4A: % of condition symptoms matched with selected checklist."""
    # Normalize inputs for matching
    p_set = set(s.lower().strip() for s in (patient_symptoms or []))
    c_set = set(s.lower().strip() for s in (condition_symptoms or []))
    
    if not c_set:
        return 0.0
        
    matches = p_set.intersection(c_set)
    return float(len(matches) / len(c_set))

def calculate_prakriti_alignment(condition_doshas: List[str], patient_prakriti: str) -> float:
    """Requirement 4D: boost if condition aligns with patient's prakriti."""
    p_prakriti = (patient_prakriti or "").lower().strip()
    c_doshas = [d.lower().strip() for d in (condition_doshas or [])]
    
    if not p_prakriti or not c_doshas:
        return 0.0
        
    return 1.0 if any(p_prakriti in d for d in c_doshas) else 0.0

def calculate_duration_factor(duration_days: int, is_chronic: bool = False) -> float:
    """Requirement 4E: short duration -> boost acute, long -> boost chronic."""
    if duration_days is None:
        return 0.5 # Neutral
        
    # Heuristic: acute <= 14 days, chronic >= 15 days
    is_acute_case = duration_days <= 14
    
    if is_acute_case and not is_chronic:
        return 1.0 # Acute boost
    elif not is_acute_case and is_chronic:
        return 1.0 # Chronic boost
    
    return 0.0

def calculate_diagnostic_score(
    candidate: Dict[str, Any],
    patient_symptoms: List[str],
    patient_prakriti: str,
    duration_days: int,
    dosha_scores: Dict[str, float]
) -> float:
    """
    Combines 5 components into a single deterministic score.
    """
    try:
        # 1. Checklist Match (40%)
        checklist_score = float(calculate_checklist_match(patient_symptoms, candidate.get("symptoms", [])) or 0.0)
        
        # 2. Embedding Similarity (30%)
        # Requirement #4: If query missing, similarity is 0.0
        embedding_score = float(candidate.get("vector_score") or 0.0)
        
        # 3. Dosha Match (10%)
        dosha_score = float(candidate.get("dosha_relevance") or 0.0)
        
        # 4. Prakriti Alignment (10%)
        prakriti_score = float(calculate_prakriti_alignment(candidate.get("dosha", []), patient_prakriti) or 0.0)
        
        # 5. Duration Factor (10%)
        is_chronic = "chronic" in (candidate.get("category") or "").lower()
        duration_val = duration_days if duration_days is not None else 0
        duration_score = float(calculate_duration_factor(duration_val, is_chronic) or 0.0)
        
        # Weighted Sum
        total = (
            (WEIGHT_CHECKLIST * checklist_score) +
            (WEIGHT_EMBEDDING * embedding_score) +
            (WEIGHT_DOSHA * dosha_score) +
            (WEIGHT_PRAKRITI * prakriti_score) +
            (WEIGHT_DURATION * duration_score)
        )
        
        # Requirements logging (Mandatory per Requirement #7)
        candidate["scores"] = {
            "checklist": round(checklist_score, 4),
            "embedding": round(embedding_score, 4),
            "dosha": round(dosha_score, 4),
            "prakriti": round(prakriti_score, 4),
            "duration": round(duration_score, 4)
        }
        
        return round(total, 4)
    except Exception as e:
        logger.error(f"Score Calculation Failure for {candidate.get('condition_name', 'Unknown')}: {str(e)}")
        # Requirement #3: Default to 0.0 on error
        candidate["scores"] = {"error": str(e), "default": 0.0}
        return 0.0
