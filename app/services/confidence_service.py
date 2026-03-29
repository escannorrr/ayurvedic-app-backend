from typing import List, Dict, Any, Optional

class ConfidenceService:
    """
    Enhanced Diagnostic Confidence Scoring System.
    
    Factors:
    - Vector Similarity (RAG): Weight 50%
    - Keyword Match Ratio: Weight 30%
    - Dosha/Prakriti Relevance: Weight 20%
    
    Range: 0% to 100%.
    """

    @staticmethod
    def calculate_confidence(
        similarity_score: float, 
        matched_keywords: List[str], 
        expected_keywords: List[str],
        patient_prakriti: str,
        condition_doshas: List[str]
    ) -> Dict[str, Any]:
        
        # 1. Vector Score (0.0 - 1.0)
        v_score = min(1.0, max(0.0, similarity_score))
        
        # 2. Keyword Score (Consistency with clinical definitions)
        k_score = len(matched_keywords) / max(1, len(expected_keywords))
        k_score = min(1.0, k_score)
        
        # 3. Dosha Score (Constitutional alignment)
        d_score = 1.0 if patient_prakriti in condition_doshas else 0.5
        
        # 4. Weighted Aggregate
        # (V*0.5 + K*0.3 + D*0.2) results in 0.1 to 1.0 typically
        raw_weighted = (v_score * 0.5) + (k_score * 0.3) + (d_score * 0.2)
        
        # 5. Normalize to 0-100% range
        confidence_pct = round(raw_weighted * 100)
        confidence_pct = min(100, max(0, confidence_pct))
        
        # 6. Assign Clinical Label (Requirement #4)
        if confidence_pct >= 76:
            label = "High"
            summary = "Strong alignment with clinical evidence and constitutional signs."
        elif confidence_pct >= 41:
            label = "Moderate"
            summary = "Consistent symptoms with moderate evidentiary support."
        else:
            label = "Low"
            summary = "Preliminary assessment based on initial symptom patterns."
            
        return {
            "score": confidence_pct,
            "label": label,
            "summary": summary
        }

    @staticmethod
    def get_overall_confidence(per_item_scores: List[int]) -> int:
        """
        Calculates the aggregate confidence for the entire diagnosis.
        """
        if not per_item_scores:
            return 0
        return round(sum(per_item_scores) / len(per_item_scores))
