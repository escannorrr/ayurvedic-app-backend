import logging
from typing import Any, Optional
from app.api.deps import get_db, get_model, get_optional_user
from fastapi import APIRouter, HTTPException, Depends
from psycopg2.extensions import connection as DBConnection
from sqlalchemy.orm import Session
from app.services.case_service import CaseService
from app.db.models import User
from fastapi.concurrency import run_in_threadpool
from app.models.schemas import DiagnosisRequest, DiagnosisResponse
from app.services.diagnosis_service import DiagnosisService

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/diagnose", response_model=DiagnosisResponse)
async def diagnose(
    request: DiagnosisRequest,
    db_session: Session = Depends(get_db), # Injected for SQLAlchemy tasks
    model: Any = Depends(get_model),
    current_user: Optional[User] = Depends(get_optional_user)
):
    """
    Diagnostic Endpoint.
    If authenticated, the result is saved as a 'Case' for the user's history.
    """
    logger.info(f"API: Received diagnosis request")
    
    try:
        # Offload sync AI work
        result = await run_in_threadpool(DiagnosisService.diagnose, request)
        
        # PERSISTENCE LAYER: Save the case if user is logged in
        if current_user:
            logger.info(f"API: Saving case for user {current_user.email}")
            # Mock structured data for legacy endpoint compatibility
            patient_info = {"patient_name": "Practitioner Consultation", "age": 0, "gender": "Unknown"}
            consultation = {"symptoms": [], "duration": "Unknown", "notes": request.query}
            
            CaseService.create_case(
                db=db_session,
                user_id=current_user.id,
                patient_info=patient_info,
                consultation=consultation,
                ai_analysis=result.dict() if hasattr(result, "dict") else result,
                status="complete" # Direct AI diagnosis usually complete in this context
            )
            
        return result
        
    except Exception as e:
        logger.error(f"API Endpoint Error: {str(e)}", exc_info=True)
        # Production error handling: Do not leak internal details.
        raise HTTPException(
            status_code=500, 
            detail="The diagnostic engine could not complete your request at this time."
        )
