import json
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

def build_context(retrieved_conditions: List[Dict[str, Any]]) -> str:
    """
    Parses the JSONB ai_content safely and extracts relevant fields.
    Builds a clean, readable context string for the LLM.
    """
    if not retrieved_conditions:
        return ""

    context_parts = []
    
    for i, condition in enumerate(retrieved_conditions, start=1):
        name = condition.get("condition_name", "Unknown Condition")
        ai_content = condition.get("ai_content")
        
        # Handle if ai_content is returned as string instead of dict
        if isinstance(ai_content, str):
            try:
                ai_content = json.loads(ai_content)
            except Exception as e:
                logger.warning(f"Failed to parse ai_content for {name}: {e}")
                ai_content = {}
        
        if not ai_content:
            ai_content = {}
            
        # Flexible key extraction based on prompt instructions
        symptoms = ai_content.get("symptoms", ai_content.get("rupa_symptoms", []))
        causes = ai_content.get("causes", ai_content.get("nidana_causes", []))
        dosha = ai_content.get("dosha", ai_content.get("dosha_involvement", ""))
        treatment = ai_content.get("treatment_principles", [])
        diet = ai_content.get("diet", [])
        lifestyle = ai_content.get("lifestyle", [])
        
        def format_list(item_list):
            if isinstance(item_list, list) and item_list:
                return ", ".join(str(item).strip() for item in item_list if item)
            elif isinstance(item_list, str) and item_list.strip():
                return item_list.strip()
            return "N/A"

        condition_text = f"Condition {i}: {name}\n"
        condition_text += f"Dosha Involvement: {dosha if dosha else 'N/A'}\n"
        condition_text += f"Symptoms (Rupa): {format_list(symptoms)}\n"
        condition_text += f"Causes (Nidana): {format_list(causes)}\n"
        condition_text += f"Treatment Principles: {format_list(treatment)}\n"
        condition_text += f"Diet: {format_list(diet)}\n"
        condition_text += f"Lifestyle: {format_list(lifestyle)}\n"
        
        context_parts.append(condition_text)

    context_str = "\n\n".join(context_parts)
    short_context = context_str[:150] + "..." if len(context_str) > 150 else context_str
    logger.info(f"Constructed context (preview): {short_context}")
    return context_str
