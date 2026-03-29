import re
from typing import List, Set

# Ayurvedic Symptom Synonym Map
SYMPTOMS_MAP = {
    "fatigue": "weakness",
    "tiredness": "weakness",
    "lassitude": "weakness",
    "klama": "weakness",
    "fever": "jwara",
    "high temperature": "jwara",
    "pyrexia": "jwara",
    "burning sensation": "daha",
    "heartburn": "amlapitta",
    "acidity": "amlapitta",
    "acid reflux": "amlapitta",
    "stiffness": "stambha",
    "joint pain": "sandhishoola",
    "arthralgia": "sandhishoola",
    "anxiety": "chinta",
    "restlessness": "manas roga",
    "insomnia": "nidranasha",
    "sleeplessness": "nidranasha",
    "constipation": "vibandha",
    "diarrhea": "atisara",
    "loose motions": "atisara",
    "loss of appetite": "agnimandya",
    "indigestion": "ajirna"
}

def normalize_single_symptom(symptom: str) -> str:
    """Normalize a single symptom string."""
    s = symptom.lower().strip()
    s = re.sub(r'[^\w\s]', '', s)
    # Map synonyms if found
    return SYMPTOMS_MAP.get(s, s)

def map_and_normalize_symptoms(checklist: List[str], extracted: List[str] = None) -> List[str]:
    """
    Combines checklist symptoms with extracted ones, normalizes, 
    and deduplicates.
    """
    all_symptoms: Set[str] = set()
    
    # Process Checklist (Primary)
    for s in checklist:
        normalized = normalize_single_symptom(s)
        if normalized:
            all_symptoms.add(normalized)
            
    # Process Extracted (Secondary)
    if extracted:
        for s in extracted:
            normalized = normalize_single_symptom(s)
            if normalized:
                all_symptoms.add(normalized)
                
    return sorted(list(all_symptoms))
