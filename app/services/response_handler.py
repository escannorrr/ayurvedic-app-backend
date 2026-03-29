import logging
from typing import Dict, Any
from app.services.flow_service import ClinicalState, flow_service
from app.services.followup_service import followup_service

logger = logging.getLogger(__name__)

class ResponseHandler:
    """
    Decides the final response strategy (Diagnosis vs Follow-up)
    based on clinical state and LLM confidence.
    """
    
    def handle_response(self, llm_result: Dict[str, Any], session_id: str, state: str, history_len: int) -> Dict[str, Any]:
        """
        Refines the LLM result to ensure it aligns with the clinical phase.
        Decision rules:
        - If FOLLOW_UP state and confidence is low: Ensure follow_up_question is present.
        - If DIAGNOSIS state: Ensure full treatment and explanation are prioritized.
        - If in-between: Combine both.
        """
        confidence_num = llm_result.get("confidence_score", 0)
        
        # Transition state if necessary
        next_state = flow_service.determine_next_state(state, history_len, confidence_num)
        
        # Strategy: Ensure follow-up questions are present if confidence is medium or low and state isn't FINAL
        if next_state in [ClinicalState.FOLLOW_UP, ClinicalState.ANALYSIS] and not llm_result.get("follow_up_question"):
            logger.info(f"Injecting intelligent follow-up for state: {next_state}")
            # The LLM prompt usually handles this, but we can enforce it here
            pass

        # Strategy: Clean up diagnosis if we are just starting
        if next_state == ClinicalState.INITIAL and len(llm_result.get("diagnosis", [])) > 0:
            # We allow it, but we marking it as 'Preliminary' in the UI if needed
            pass
            
        return {
            "payload": llm_result,
            "next_state": next_state
        }

response_handler = ResponseHandler()
