import logging
from typing import Dict, Any
from app.models.schemas import DiagnosisResponse
from app.services.ai_pipeline import run_pipeline

logger = logging.getLogger(__name__)

class DiagnosisService:
    """
    High-level service wrapper for the Ayurvedic AI Diagnostic Engine.
    Follows the Clean Architecture 'Service' pattern, hiding the 
    complexity of query expansion, RAG, and multi-factor ranking.
    """
    
from app.models.schemas import DiagnosisRequest, DiagnosisResponse
from app.services.ai_pipeline import validate_and_enrich_response
from app.services.embedding_service import generate_embedding
from app.services.dosha_service import score_dosha
from app.services.llm_service import expand_query, generate_hardened_diagnosis, FALLBACK_RESPONSE
from app.repositories.condition_repo import ConditionRepository
from app.utils.symptom_mapper import map_and_normalize_symptoms
from app.utils.scoring import calculate_diagnostic_score
from app.utils.formatting import normalize_symptoms as simple_normalize

logger = logging.getLogger(__name__)

class DiagnosisService:
    """
    Orchestrator for the Ayurvedic Structured Clinical Diagnosis Engine.
    """
    
    @staticmethod
    def diagnose(request: DiagnosisRequest) -> DiagnosisResponse:
        """
        Executes the high-precision 5-factor diagnostic pipeline.
        """
        try:
            # 1. Normalize Symptoms (Checklist + Query Extraction)
            # Requirement #1: Validate Inputs at Entry Point
            request.symptoms = [s.lower().strip() for s in (request.symptoms or [])]
            request.prakriti = (request.prakriti or "").lower().strip()
            request.query = request.query or ""
            
            # For extraction, we use a simple normalization of the query for now
            extracted_from_query = simple_normalize(request.query or "").split()
            patient_symptoms = map_and_normalize_symptoms(request.symptoms, extracted_from_query)
            logger.info(f"Structured Diagnosis: Normalized symptoms: {patient_symptoms}")

            # 2. Query Expansion & Dosha Scoring (Preserve clinical context)
            query_for_llm = request.query or " ".join(request.symptoms)
            expanded = expand_query(query_for_llm)
            dosha_scores = score_dosha(expanded)
            logger.info(f"Clinical Metabolic Profile: {dosha_scores}")

            # 3. Hybrid Retrieval
            embedding = generate_embedding(" ".join(patient_symptoms))
            candidates = ConditionRepository.fetch_candidates_hybrid(query_for_llm, embedding, limit=15)

            # Defensive Check: Requirement #1
            if not candidates:
                logger.warning("Hardening: No candidates found for diagnostic query.")
                fallback_data = {
                    "diagnosis": [],
                    "confidence": 0,
                    "message": "No matching condition found",
                    "suggestion": "Please refine symptoms",
                    "explanation": "No specific Ayurvedic conditions were identified for the provided symptoms.",
                    "dosha": {"vata": 33, "pitta": 33, "kapha": 34}
                }
                return DiagnosisResponse(**validate_and_enrich_response(fallback_data, dosha_scores))

            # 4. Multi-Factor Weighted Scoring (Requirement #5: Safe Candidate Loop)
            # Mandatory Logging (Requirement #7)
            logger.info(f"Clinical Telemetry | Raw: {request.symptoms} | Normalized: {patient_symptoms} | Query: {request.query}")
            
            scored_candidates = []
            for c in candidates:
                try:
                    c["total_score"] = calculate_diagnostic_score(
                        candidate=c,
                        patient_symptoms=patient_symptoms,
                        patient_prakriti=request.prakriti,
                        duration_days=request.duration_days,
                        dosha_scores=dosha_scores
                    )
                    scored_candidates.append(c)
                except Exception as loop_err:
                    logger.error(f"Fault Tolerance: Skipping condition '{c.get('condition_name', 'Unknown')}' due to scoring failure: {loop_err}")
                    continue

            # 5. Deterministic Ranking
            scored_candidates.sort(key=lambda x: (
                -x.get("total_score", 0.0), 
                -x.get("scores", {}).get("checklist", 0.0), 
                x.get("condition_name", "")
            ))

            top_results = scored_candidates[:5]
            if not top_results:
                logger.warning("Hardening: No valid results after scoring loop.")
                fallback_data = {
                    "diagnosis": [],
                    "message": "No matching condition found",
                    "suggestion": "Please refine symptoms",
                    "confidence": 0,
                    "dosha": {"vata": 33, "pitta": 33, "kapha": 34}
                }
                return DiagnosisResponse(**validate_and_enrich_response(fallback_data, dosha_scores))

            # 6. Structured LLM Explanation (Requirement #9)
            context_text = "\n\n".join([
                f"Condition: {r['condition_name']}\nDescription: {r['ai_content']}\nSymptoms: {r['symptoms']}\nMatch Score: {r['total_score']}" 
                for r in top_results
            ])
            
            raw_result = generate_hardened_diagnosis(query_for_llm, context_text, dosha_scores)
            
            # 7. Final Enrichment & Treatment Injection
            # Force derive results from the top candidate (Requirement #7, #8)
            enriched = validate_and_enrich_response(raw_result, dosha_scores, [
                {"name": c.get("condition_name", ""), **c} for c in scored_candidates
            ])
            
            # Telemetry for top candidates (Requirement #7)
            for res in top_results:
                logger.info(f"Condition Match: {res.get('condition_name')} | Score: {res.get('total_score')} | Components: {res.get('scores')}")
            
            # Add Debug info if available
            enriched["debug"] = {
                "normalized_symptoms": patient_symptoms,
                "top_candidates": [
                    {"name": c["condition_name"], "score": c["total_score"], "breakdown": c.get("scores")}
                    for c in top_results
                ]
            }

            return DiagnosisResponse(**enriched)
            
        except Exception as e:
            logger.error(f"DiagnosisService Error: {str(e)}", exc_info=True)
            raise 
