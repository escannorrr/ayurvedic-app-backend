from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional, Any
from app.db.models import Case
from app.models.schemas import DiagnosisResponse
import json

class CaseService:
    @staticmethod
    def generate_case_id(db: Session) -> str:
        """
        Generates a unique clinical identifier in VA-xxxx format.
        """
        count = db.query(Case).count()
        return f"VA-{1000 + count + 1}"

    @staticmethod
    def create_case(
        db: Session, 
        user_id: int, 
        patient_info: dict,
        consultation: dict,
        ai_analysis: Optional[dict] = None,
        doctor_input: Optional[dict] = None,
        status: str = "draft"
    ) -> Case:
        """
        Creates a new clinical case with separate tracks for AI analysis and doctor input.
        """
        # 1. Generate Case ID
        case_id = CaseService.generate_case_id(db)
        
        # 2. Reconstruct a 'query' for the record (compatibility)
        query = consultation.get("notes") or f"Consultation for {patient_info.get('patient_name', 'Patient')}"
        
        # 3. Extract metadata for legacy dashboard fields (from AI or Doctor)
        # We prioritize AI analysis for these stats if available
        pitta, vata, kapha, confidence = 0, 0, 0, 0
        diagnosis_flat, treatment_flat = [], {}

        source = ai_analysis or {}
        if source:
            dosha = source.get("dosha", {})
            pitta = dosha.get("pitta", 0)
            vata = dosha.get("vata", 0)
            kapha = dosha.get("kapha", 0)
            confidence = source.get("confidence", 0)
            diagnosis_flat = source.get("diagnosis", [])
            treatment_flat = source.get("treatment", {})

        new_case = Case(
            user_id=user_id,
            case_identifier=case_id,
            query=query,
            status=status,
            patient_info=patient_info,
            consultation=consultation,
            ai_analysis=ai_analysis,
            doctor_input=doctor_input,
            # Maintain legacy columns for old dashboard compatibility
            diagnosis=diagnosis_flat,
            treatment=treatment_flat,
            confidence=confidence,
            pitta=pitta,
            vata=vata,
            kapha=kapha
        )
        
        db.add(new_case)
        db.commit()
        db.refresh(new_case)
        return new_case

    @staticmethod
    def list_cases(
        db: Session, 
        user_id: int, 
        skip: int = 0, 
        limit: int = 20,
        status: Optional[str] = None
    ) -> tuple[List[Case], int]:
        query = db.query(Case).filter(Case.user_id == user_id)
        if status:
            query = query.filter(Case.status == status)
            
        total = query.count()
        items = query.order_by(desc(Case.created_at)).offset(skip).limit(limit).all()
        return items, total

    @staticmethod
    def get_case(db: Session, user_id: int, case_id: int) -> Optional[Case]:
        return db.query(Case).filter(Case.id == case_id, Case.user_id == user_id).first()

    @staticmethod
    def search_cases(db: Session, user_id: int, search_query: str) -> List[Case]:
        """
        Robust search across patient names, identifiers, symptoms, and clinical notes.
        Uses JSON casting for portability.
        """
        pattern = f"%{search_query}%"
        from sqlalchemy import or_, cast, String
        
        return db.query(Case).filter(
            Case.user_id == user_id,
            or_(
                Case.case_identifier.ilike(pattern),
                Case.query.ilike(pattern),
                # Search within nested JSON structures
                cast(Case.patient_info, String).ilike(pattern),
                cast(Case.consultation, String).ilike(pattern),
                cast(Case.doctor_input, String).ilike(pattern)
            )
        ).order_by(desc(Case.created_at)).all()

    @staticmethod
    def update_notes(db: Session, user_id: int, case_id: int, notes: str) -> Optional[Case]:
        case = CaseService.get_case(db, user_id, case_id)
        if not case:
            return None
            
        # Update inside nested doctor_input
        if not case.doctor_input:
            case.doctor_input = {"clinical_notes": notes, "final_diagnosis": [], "is_ai_used": True}
        else:
            case.doctor_input["clinical_notes"] = notes
            
        # Flag modified for JSON
        from sqlalchemy.orm.attributes import flag_modified
        flag_modified(case, "doctor_input")
            
        db.add(case)
        db.commit()
        db.refresh(case)
        return case
