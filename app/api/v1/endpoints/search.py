from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.base import get_db
from app.api.deps import get_current_user
from app.db.models import User
from app.schemas.saas_schemas import CaseListOut
from app.services.case_service import CaseService

router = APIRouter()

@router.get("/", response_model=List[CaseListOut])
def global_search(
    q: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Unified search across all patient records and consultation history.
    """
    items = CaseService.search_cases(db, current_user.id, q)
    
    # Map to CaseListOut for consistent summary view
    case_list = []
    for item in items:
        p_name = "Patient"
        if item.patient_info and isinstance(item.patient_info, dict):
            p_name = item.patient_info.get("patient_name", item.patient_info.get("name", "Patient"))
            
        diag_summary = "General Consultation"
        if item.diagnosis and len(item.diagnosis) > 0:
            diag_summary = item.diagnosis[0].get("condition", "General Consultation")

        case_list.append({
            "id": item.id,
            "case_identifier": item.case_identifier,
            "patient_name": p_name,
            "diagnosis_summary": diag_summary,
            "date": item.created_at,
            "status": item.status
        })

    return case_list
