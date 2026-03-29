import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

# Generic Dosha-based treatment presets
DOSHA_PRESETS = {
    "pitta": {
        "condition": "Pitta Vitiation (Excess Heat)",
        "explanation": "Your symptoms indicate an aggravation of the Pitta Dosha, characterized by excess heat, acidity, or inflammation in the body.",
        "treatment": {
            "principles": ["Cooling (Sheeta)", "Soothing", "Oleation"],
            "herbs": ["Amalaki", "Shatavari", "Guduchi"],
            "formulations": ["Avipattikar Churna", "Kamadudha Rasa"],
            "diet": ["Sweet fruits", "Coconut water", "Ghee", "Avoid spicy/sour foods"],
            "lifestyle": ["Avoid excess sun", "Gentle yoga", "Moonlight walks"]
        },
        "precautions": ["Avoid pungent, salty, and sour foods.", "Minimize exposure to direct heat."],
        "when_to_consult": ["If burning sensations persist or digestive discomfort worsens."]
    },
    "vata": {
        "condition": "Vata Vitiation (Excess Dryness/Mobility)",
        "explanation": "Your symptoms suggest a Vata imbalance, often manifesting as dryness, anxiety, or irregular digestion/sleep patterns.",
        "treatment": {
            "principles": ["Grounding", "Warming", "Deep Oleation"],
            "herbs": ["Ashwagandha", "Bala", "Dashamoola"],
            "formulations": ["Mahanarayan Oil", "Ashwagandharishta"],
            "diet": ["Warm, moist foods", "Healthy fats (Ghee, Sesame Oil)", "Sweet, sour, and salty tastes"],
            "lifestyle": ["Establish a routine", "Abhyanga (Oil Massage)", "Restorative sleep"]
        },
        "precautions": ["Avoid cold/raw foods.", "Minimize travel and excessive physical/mental stimulation."],
        "when_to_consult": ["If sleep issues or structural stiffness persists."]
    },
    "kapha": {
        "condition": "Kapha Vitiation (Excess Heaviness/Stagnation)",
        "explanation": "Your symptoms align with a Kapha imbalance, typically involving congestion, lethargy, or slow metabolism.",
        "treatment": {
            "principles": ["Stimulating", "Heating", "Drying (Rookshana)"],
            "herbs": ["Trikatu (Ginger, Pepper, Long Pepper)", "Punarnava", "Tulsi"],
            "formulations": ["Trikatu Churna", "Kanchanar Guggulu"],
            "diet": ["Warm, spicy, and bitter foods", "Light grains (Millets)", "Avoid dairy and heavy sweets"],
            "lifestyle": ["Vigorous exercise", "Dry massage", "Staying active"]
        },
        "precautions": ["Avoid cold drinks and excessive sleep (especially during the day)."],
        "when_to_consult": ["If lethargy or congestion impacts daily breathing or energy."]
    }
}

def get_dosha_fallback(dosha_scores: Dict[str, float]) -> Dict[str, Any]:
    """
    Generates a high-quality clinical fallback based on the dominant Dosha score.
    Ensures the system never returns an empty diagnosis.
    """
    if not dosha_scores:
        # Absolute fallback if scores are missing
        return DOSHA_PRESETS["vata"] # Default to Vata as it's common

    # Find the dominant dosha
    dominant = max(dosha_scores, key=dosha_scores.get)
    score = dosha_scores[dominant]
    
    logger.info(f"Generating fallback for dominant Dosha: {dominant} (Score: {score})")
    
    preset = DOSHA_PRESETS.get(dominant.lower(), DOSHA_PRESETS["vata"])
    
    return {
        "diagnosis": [{"condition": preset["condition"], "confidence": "Medium-High (Dosha Match)"}],
        "confidence": int(score * 100) if score > 0 else 50,
        "dosha": {k: int(v * 100) for k, v in dosha_scores.items()},
        "explanation": preset["explanation"],
        "follow_up_question": "To give a more specific diagnosis, could you mention any other digestive or sleep symptoms?",
        "dosha_analysis": f"A keyword-based analysis suggests a significant {dominant.capitalize()} imbalance.",
        "treatment": preset["treatment"],
        "precautions": preset["precautions"],
        "when_to_consult": preset["when_to_consult"]
    }
