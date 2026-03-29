from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.base import get_db
from app.db.models import User
from app.api.deps import get_current_user
from app.schemas.saas_schemas import (
    CaseOut, CaseCreate, PaginatedCases, CaseDetailOut, NotesUpdate, CaseCreateResponse
)
from app.services.case_service import CaseService

router = APIRouter()

@router.post("/", response_model=CaseCreateResponse)
def create_case(
    case_in: CaseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Manually save a consultation result as a permanent clinical case.
    Supports both NEW clinical workflow and LEGACY AI-only format.
    """
    # 1. Backward Compatibility Mapping
    ai_analysis = case_in.ai_analysis
    if not ai_analysis and case_in.diagnosis_result:
        # Map old 'diagnosis_result' to new 'ai_analysis'
        ai_analysis = case_in.diagnosis_result

    # 2. Extract Consultation Data (handle empty notes/duration)
    # If legacy symptoms sent (not possible with new CaseCreate but good to be safe if schema allowed)
    
    # 3. Create via Service
    new_case = CaseService.create_case(
        db=db,
        user_id=current_user.id,
        patient_info=case_in.patient_info.dict(),
        consultation=case_in.consultation.dict(),
        ai_analysis=ai_analysis.dict() if ai_analysis else None,
        doctor_input=case_in.doctor_input.dict() if case_in.doctor_input else None,
        status=case_in.status
    )
    
    return {
        "case_id": new_case.case_identifier,
        "status": new_case.status,
        "created_at": new_case.created_at
    }

@router.get("/", response_model=PaginatedCases)
def list_cases(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    page: int = 1,
    limit: int = 20,
    status: Optional[str] = None
):
    """
    Retrieve paginated clinical history for the authenticated user.
    """
    skip = (page - 1) * limit
    items, total = CaseService.list_cases(db, current_user.id, skip, limit, status)
    
    # Map to CaseListOut
    case_list = []
    for item in items:
        # Extract patient name from info or query
        p_name = "Patient"
        if item.patient_info and isinstance(item.patient_info, dict):
            p_name = item.patient_info.get("patient_name", item.patient_info.get("name", "Patient"))
            
        # Summary is the primary diagnosis condition
        diag_summary = "General Consultation"
        # Try legacy field first
        if item.diagnosis and len(item.diagnosis) > 0:
            diag_summary = item.diagnosis[0].get("condition", "General Consultation")
        # Fallback to new structured field
        elif item.ai_analysis and "diagnosis" in item.ai_analysis:
            diags = item.ai_analysis["diagnosis"]
            if diags and len(diags) > 0:
                diag_summary = diags[0].get("condition", "General Consultation")

        case_list.append({
            "id": item.id,
            "case_identifier": item.case_identifier,
            "patient_name": p_name,
            "diagnosis_summary": diag_summary,
            "date": item.created_at,
            "status": item.status
        })

    return {
        "items": case_list,
        "total": total,
        "page": page,
        "limit": limit
    }

@router.get("/search", response_model=List[CaseOut])
def search_cases(
    query: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Search through saved cases by query text.
    """
    return CaseService.search_cases(db, current_user.id, query)

@router.get("/{case_id}", response_model=CaseDetailOut)
def get_case(
    case_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get comprehensive breakdown of a single clinical consultation.
    """
    case = CaseService.get_case(db, current_user.id, case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
        
    # New Clinical Schema
    return {
        "id": case.id,
        "case_identifier": case.case_identifier,
        "status": case.status,
        "patient_info": case.patient_info or {},
        "consultation": case.consultation or {},
        "ai_analysis": case.ai_analysis or {},
        "doctor_input": case.doctor_input or {},
        "timeline": case.timeline or [],
        "attachments": case.attachments or [],
        "created_at": case.created_at
    }

@router.patch("/{case_id}/notes")
def update_notes(
    case_id: int,
    notes_in: NotesUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    case = CaseService.update_notes(db, current_user.id, case_id, notes_in.notes)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
        
    notes = ""
    if case.doctor_input:
        notes = case.doctor_input.get("clinical_notes", "")
        
    return {"notes": notes}
