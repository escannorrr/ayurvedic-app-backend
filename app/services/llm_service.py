import os
import json
import logging
import re
from typing import List, Dict, Any, Optional
from groq import Groq

logger = logging.getLogger(__name__)

FALLBACK_RESPONSE: Dict[str, Any] = {
    "diagnosis": [],
    "confidence": 0,
    "dosha": {"vata": 0, "pitta": 0, "kapha": 0},
    "explanation": "Insufficient clinical evidence found.",
    "follow_up_question": "To clarify, could you describe the duration and severity of your symptoms?",
    "dosha_analysis": "No clear imbalance detected.",
    "treatment": {"principles": [], "herbs": [], "formulations": [], "diet": [], "lifestyle": []},
    "precautions": [],
    "when_to_consult": ["If symptoms persist for 48 hours."]
}

def generate_hardened_diagnosis(query: str, context: str, dosha_scores: Dict[str, float] = None) -> Dict[str, Any]:
    """
    Hardened engine with Improved Explanation Clarity.
    Enforces symptom mapping and dosha-logic transparency.
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key: return FALLBACK_RESPONSE

    try:
        client = Groq(api_key=api_key)
        
        system_prompt = """You are a senior Ayurvedic clinical expert (Vaidya). 
        Conduct a precise clinical analysis. Avoid generic AI phrasing.
        Speak directly as an expert physician providing a clinical report.

        ## 📋 Explanation Guidelines (DETERMINISTIC STRUCTURE)
        Your 'explanation' field must follow this EXACT structure:
        - CHECKLIST SYMPTOMS: {List symptoms from the patient's checklist}
        - PRIMARY DIAGNOSIS: {Name of top matched condition}
        - CLINICAL RATIONALE: {Explain how symptoms match the condition's pathogenesis/Samprapti}
        - MATCH SCORE: {Final % score}
        - DOMINANT DOSHA: {Dominant Ayurvedic energy}
        - SUPPORTING CONDITIONS: {List top 2 and 3 candidates if applicable}
        
        ## 🛡️ Clinical Rules
        - **Deterministic Reasoning**: Base your logic on the provided Knowledge Base Context.
        - **Exclusion**: If a symptom doesn't fit the primary condition, mention it under differential diagnosis.
        - **JSON Enforcement**: Return ONLY valid JSON.

        ## 📋 Response Schema
        {
            "diagnosis": [{"condition": "string", "confidence": "Low | Moderate | High"}],
            "confidence": 0-100,
            "dosha": {"vata": 0-100, "pitta": 0-100, "kapha": 0-100},
            "explanation": "Follow the structured guidelines above.",
            "dosha_analysis": "Concise summary of cumulative dosha evidence",
            "treatment": {
                "principles": [], "herbs": [], "formulations": [], "diet": [], "lifestyle": []
            },
            "precautions": [],
            "when_to_consult": []
        }
        """
        
        dosha_info = f"\nAnalyzed dosha scores: {json.dumps(dosha_scores)}" if dosha_scores else ""
        user_prompt = f"Patient Input: {query}\n{dosha_info}\n\nRetrieved Knowledge Base Context:\n{context}\n\nConduct the clinical assessment in JSON format."

        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.1,
            top_p=0.9,
            max_tokens=1024,
            response_format={"type": "json_object"}
        )
        
        raw_content = completion.choices[0].message.content.strip()
        if raw_content.startswith("```"):
            raw_content = re.sub(r"```(json)?\n?", "", raw_content)
            raw_content = raw_content.rstrip("`").strip()

        try:
            result = json.loads(raw_content)
            required = ["diagnosis", "confidence", "dosha", "explanation", "treatment"]
            for field in required:
                if field not in result: return FALLBACK_RESPONSE
            return result
        except json.JSONDecodeError:
            return FALLBACK_RESPONSE

    except Exception as e:
        logger.error(f"Explanation hardening fail: {e}")
        return FALLBACK_RESPONSE

def generate_response(query: str, context: str, dosha_scores: Dict[str, float] = None, history: Any = None) -> Dict[str, Any]:
    return generate_hardened_diagnosis(query, context, dosha_scores)

def expand_query(query: str, history: Any = None) -> str:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key: return query
    try:
        client = Groq(api_key=api_key)
        prompt = f"Expand this Ayurvedic symptom query: {query}. Only return expanded text."
        completion = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}], temperature=0.1)
        return completion.choices[0].message.content.strip()
    except: return query
