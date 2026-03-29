import logging
import os
from typing import Dict, Any, List
from app.services.embedding_service import generate_embedding
from app.services.retrieval_service import hybrid_search, rank_diseases
from app.services.dosha_service import score_dosha
from app.services.llm_service import expand_query, generate_hardened_diagnosis, FALLBACK_RESPONSE
from app.services.fallback_service import get_dosha_fallback
from app.services.logging_service import log_clinical_event, summarize_candidates
from app.services.confidence_service import ConfidenceService
from app.utils.formatting import format_string_percentages, normalize_symptoms

logger = logging.getLogger(__name__)

RETRY_LIMIT = 2
ENV = os.getenv("ENV", "production")

# Global In-Memory Cache for Deterministic Responses
# Key: normalized_symptoms_string, Value: enriched_response_dict
QUERY_CACHE: Dict[str, Any] = {}

def normalize_dosha_scores(dosha_data: Any) -> Dict[str, int]:
    """Requirement #8: Normalize to 100% and round to integer."""
    normalized = {"vata": 0, "pitta": 0, "kapha": 0}
    if not dosha_data:
        return normalized
    
    # Handle list input (from DB) or dict input (from LLM)
    raw_scores = {"vata": 0.0, "pitta": 0.0, "kapha": 0.0}
    if isinstance(dosha_data, list):
        for d in dosha_data:
            d_low = d.lower().strip()
            if d_low in raw_scores: raw_scores[d_low] = 1.0
    elif isinstance(dosha_data, dict):
        for k, v in dosha_data.items():
            key = k.lower()
            if key in raw_scores: raw_scores[key] = float(v)

    total = sum(raw_scores.values())
    if total == 0:
        return {"vata": 33, "pitta": 33, "kapha": 34}
        
    # Scale to 100%
    temp_total = 0
    keys = ["vata", "pitta", "kapha"]
    for i, k in enumerate(keys):
        if i == len(keys) - 1:
            normalized[k] = 100 - temp_total
        else:
            val = int(round((raw_scores[k] / total) * 100))
            normalized[k] = val
            temp_total += val
            
    return normalized

def is_structurally_sound(result: Dict[str, Any]) -> bool:
    if not result.get("diagnosis"): return False
    treatment = result.get("treatment", {})
    total_items = 0
    for key in ["principles", "herbs", "formulations", "diet", "lifestyle"]:
        total_items += len(treatment.get(key, []))
    return total_items >= 2

def validate_and_enrich_response(
    result: Dict[str, Any], 
    dosha_scores: Dict[str, float],
    ranked_results: List[Dict[str, Any]] = None
) -> Dict[str, Any]:
    # --- Defensive Type Casting for Frontend Stability ---
    def to_str(val: Any) -> str:
        if isinstance(val, list): return " ".join(map(str, val))
        return str(val) if val is not None else ""

    # Ensure textual fields are strictly strings (Fixes Flutter JSArray error)
    result["explanation"] = to_str(result.get("explanation", ""))
    result["dosha_analysis"] = to_str(result.get("dosha_analysis", ""))
    result["follow_up_question"] = to_str(result.get("follow_up_question", ""))

    # --- Percentage Formatting for Clinician Readability ---
    result["explanation"] = format_string_percentages(result["explanation"])
    result["dosha_analysis"] = format_string_percentages(result["dosha_analysis"])
    
    # Ensure precaution/consult are lists
    for list_field in ["precautions", "when_to_consult"]:
        val = result.get(list_field)
        if isinstance(val, str): result[list_field] = [val]
        elif not isinstance(val, list): result[list_field] = []

    # --- Structured Treatment Overwrite ---
    # We use data from the top retrieval candidate to ensure medical consistency
    if ranked_results and len(ranked_results) > 0:
        top = ranked_results[0]
        treatment = result.setdefault("treatment", {})
        
        # Mapping from DB fields to API fields
        treatment["principles"] = top.get("principles") or treatment.get("principles") or ["General Balancing"]
        treatment["herbs"] = top.get("herbs") or treatment.get("herbs") or ["Guduchi", "Tulsi"]
        treatment["formulations"] = top.get("formulations") or treatment.get("formulations") or ["General Ayurvedic Preparation"]
        treatment["diet"] = top.get("diet") or treatment.get("diet") or ["Light, warm food"]
        treatment["lifestyle"] = top.get("lifestyle") or treatment.get("lifestyle") or ["Adequate rest"]
        
        # Requirement #8: Derive dosha from selected condition
        if top.get("dosha"):
            result["dosha"] = normalize_dosha_scores(top["dosha"])
            logger.info(f"Structured Dosha Derived for {top['name']}")
        
        logger.info(f"Structured Treatment Injected for {top['name']}")

    if not is_structurally_sound(result):
        fallback = get_dosha_fallback(dosha_scores)
        if not result.get("diagnosis"):
            result["diagnosis"] = fallback["diagnosis"]
            result["explanation"] = fallback["explanation"]
        
        # Fallback values for principles if still empty
        treatment = result.setdefault("treatment", {})
        if not treatment.get("principles"):
            treatment["principles"] = ["Samana Chikitsa"]
    
    # 1. Normalize Doshas
    result["dosha"] = normalize_dosha_scores(result.get("dosha", dosha_scores))
    
    # 2. Advanced Confidence Scoring (Per Diagnosis)
    diagnosis_list = result.get("diagnosis", [])
    per_item_scores = []
    
    # Simple patient prakriti prediction from scores
    patient_prakriti = "Vata"
    if dosha_scores:
        sorted_doshas = sorted(dosha_scores.items(), key=lambda x: x[1], reverse=True)
        patient_prakriti = sorted_doshas[0][0].capitalize()

    for item in diagnosis_list:
        # Match LLM findings to retrieval candidates
        match = next((r for r in (ranked_results or []) if r["name"].lower() in item["condition"].lower()), None)
        
        if match:
            # Calculate multi-factor confidence
            conf_data = ConfidenceService.calculate_confidence(
                similarity_score=match.get("vector_score", 0.5),
                matched_keywords=[], # Simplified: use ratio from keyword_score
                expected_keywords=[], 
                patient_prakriti=patient_prakriti,
                condition_doshas=[patient_prakriti] # Simplified alignment
            )
            # Override with weighted reality
            item["confidence"] = conf_data["score"]
            item["label"] = conf_data["label"]
        else:
            # Default lower confidence for "out-of-knowledge" or "synthesized" findings
            item["confidence"] = 65
            item["label"] = "Preliminary"
        
        per_item_scores.append(item["confidence"])

    # 3. Overall System Confidence
    result["confidence"] = ConfidenceService.get_overall_confidence(per_item_scores)
    
    return result

def run_pipeline(query: str) -> Dict[str, Any]:
    """
    Hardened pipeline: Single-request architecture (Session-less).
    """
    logger.info(f"Pipeline execution: {query}")
    clean_query = query.strip()
    if len(clean_query) < 3:
        return validate_and_enrich_response(FALLBACK_RESPONSE, {"vata":0.33, "pitta":0.33, "kapha":0.33})

    try:
        # 1. Preprocessing & Normalization
        normalized_query = normalize_symptoms(clean_query)
        
        # --- CACHE CHECK ---
        if normalized_query in QUERY_CACHE:
            logger.info(f"Cache Hit: {normalized_query}")
            return QUERY_CACHE[normalized_query]

        # 2. Expansion & Dosha Scoring (Preserve original query for LLM)
        expanded = expand_query(clean_query)
        log_clinical_event("QUERY_EXPANSION", clean_query, {"expanded": expanded, "normalized": normalized_query})
        dosha_scores = score_dosha(expanded)

        # 3. Hybrid Retrieval & Reranking (Deterministic)
        embedding = generate_embedding(normalized_query)
        candidates = hybrid_search(normalized_query, embedding, limit=10)
        ranked_results = rank_diseases(candidates, dosha_scores)
        
        # 4. Top Candidate Freeze Logic & Context
        if len(ranked_results) >= 2:
            diff = abs(ranked_results[0]["final_ranking_score"] - ranked_results[1]["final_ranking_score"])
            if diff < 0.01:
                logger.info(f"Stability Trigger: Selecting {ranked_results[0]['name']} over {ranked_results[1]['name']} (diff: {diff})")

        top_results = ranked_results[:5]
        context_text = "\n\n".join([
            f"Condition: {r['name']}\nDescription: {r['description']}\nSymptoms: {r['symptoms']}\nMatch Score: {r['final_ranking_score']}" 
            for r in top_results
        ]) if top_results else "No specific matching disease profiles found."

        # 5. Diagnostic Loop (Retry Logic)
        final_result = {}
        for attempt in range(RETRY_LIMIT + 1):
            result = generate_hardened_diagnosis(clean_query, context_text, dosha_scores)
            if is_structurally_sound(result):
                final_result = result
                break
        
        if not final_result: final_result = result

        # 6. Final Enrichment & Cache
        # Note: validate_and_enrich_response handles dosha integer rounding
        enriched = validate_and_enrich_response(final_result, dosha_scores, ranked_results)
        
        # Cache Result
        QUERY_CACHE[normalized_query] = enriched
        
        log_clinical_event("PIPELINE_COMPLETE", clean_query, {
            "status": "success",
            "normalized_input": normalized_query,
            "selected_condition": enriched.get("diagnosis", [{}])[0].get("condition", "N/A"),
            "final_response": enriched
        })
        
        return enriched

    except Exception as e:
        logger.error(f"Pipeline Error: {e}")
        error_resp = validate_and_enrich_response(FALLBACK_RESPONSE, {})
        log_clinical_event("PIPELINE_ERROR", clean_query, {"error": str(e)})
        return error_resp
