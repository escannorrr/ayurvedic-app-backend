from typing import Dict
import re

# Clinical Dosha Keyword Mapping
DOSHA_KEYWORDS = {
    "vata": [
        "anxiety", "restlessness", "insomnia", "dry", "cold", "bloating", 
        "constipation", "gas", "joint pain", "tremors", "rough", "light", 
        "erratic", "shimmering", "pricking pain"
    ],
    "pitta": [
        "inflammation", "burning", "acidity", "anger", "hot", "red", 
        "irritation", "thirst", "fever", "sweating", "sharp", "acidic", 
        "pungent", "ulcer", "rash"
    ],
    "kapha": [
        "lethargy", "heaviness", "congestion", "mucus", "slow", "weight gain", 
        "oily", "dull", "stable", "clinging", "swelling", "cold", "sweet", 
        "cloudy", "numbness"
    ]
}

def score_dosha(query_text: str) -> Dict[str, float]:
    """
    Analyzes expanded query text for Dosha-specific keywords and returns a 
    normalized scoring breakdown (0.0 to 1.0).
    """
    text = query_text.lower()
    scores = {"vata": 0.0, "pitta": 0.0, "kapha": 0.0}
    
    total_matches = 0
    for dosha, keywords in DOSHA_KEYWORDS.items():
        for keyword in keywords:
            # Use regex to find whole words only
            matches = len(re.findall(rf"\b{keyword}\b", text))
            scores[dosha] += matches
            total_matches += matches
            
    # Normalize scores to a 0.0 - 1.0 range
    if total_matches > 0:
        for dosha in scores:
            scores[dosha] = round(scores[dosha] / total_matches, 2)
    
    return scores
