import logging
from typing import Any, Optional
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from fastapi.concurrency import run_in_threadpool

from app.api.deps import get_db, get_optional_user
from app.models.schemas import DiagnosisRequest, DiagnosisResponse
from app.services.diagnosis_service import DiagnosisService
from app.services.case_service import CaseService
from app.db.models import User

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/diagnose", response_model=DiagnosisResponse)
async def diagnose(
    request: DiagnosisRequest,
    db_session: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user)
):
    """
    Structured Ayurvedic Consultation Endpoint.
    Orchestrates patient metadata into a clinical query for the improved AI pipeline.
    """
    patient_name = request.patient_name or "Anonymous Patient"
    logger.info(f"Consultation: Received structured request for {patient_name}")
    
    try:
        # The DiagnosisService.diagnose now handles the full structured logic
        result = await run_in_threadpool(DiagnosisService.diagnose, request)
        
        # PERSISTENCE: Save as a case if authenticated
        if current_user:
            CaseService.create_case(
                db=db_session,
                user_id=current_user.id,
                patient_info={
                    "patient_name": patient_name,
                    "age": request.age,
                    "gender": request.gender
                },
                consultation={
                    "symptoms": request.symptoms,
                    "duration_days": request.duration_days,
                    "prakriti": request.prakriti,
                    "query": request.query
                },
                ai_analysis=result.dict() if hasattr(result, "dict") else result,
                status="draft" # Default to draft for consultations
            )
            
        return result
        
    except Exception as e:
        logger.error(f"Consultation Error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500, 
            detail="The consultation engine is currently unavailable."
        )
