import logging
from enum import Enum
from typing import Dict, Any, List

class ClinicalState(str, Enum):
    INITIAL = "INITIAL"           # Brand new conversation
    FOLLOW_UP = "FOLLOW_UP"       # Collecting more info
    ANALYSIS = "ANALYSIS"         # Deep reasoning with enough data
    DIAGNOSIS = "DIAGNOSIS"       # Providing final assessment

class FlowService:
    """
    Manages the clinical state machine for a session.
    Ensures that the AI stays in a structured path from discovery to diagnosis.
    """
    
    # Thresholds for state transitions
    MIN_MSGS_FOR_ANALYSIS = 3
    CONFIDENCE_DIAGNOSIS_THRESHOLD = 70  # Higher confidence needed for final state

    def determine_next_state(self, current_state: str, history_len: int, confidence: int) -> ClinicalState:
        """
        Implements transition logic based on conversation depth and clinical confidence.
        """
        if current_state == ClinicalState.INITIAL:
            return ClinicalState.FOLLOW_UP
        
        if current_state == ClinicalState.FOLLOW_UP:
            if history_len >= self.MIN_MSGS_FOR_ANALYSIS:
                return ClinicalState.ANALYSIS
            return ClinicalState.FOLLOW_UP
            
        if current_state == ClinicalState.ANALYSIS:
            if confidence >= self.CONFIDENCE_DIAGNOSIS_THRESHOLD:
                return ClinicalState.DIAGNOSIS
            return ClinicalState.ANALYSIS
            
        return ClinicalState.DIAGNOSIS  # Once in Diagnosis, stay there unless state is reset

flow_service = FlowService()
