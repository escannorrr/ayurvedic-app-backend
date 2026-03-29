from fastapi import APIRouter, Depends
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.base import get_db
from app.db.models import User, Case
from app.api.deps import get_current_user
from app.schemas.saas_schemas import DashboardStats, DashboardSummary, RecentConsultation
from app.services.case_service import CaseService
from datetime import datetime, date

router = APIRouter()

@router.get("/summary", response_model=DashboardSummary)
def get_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get clinical volume summary for the dashboard.
    """
    today_start = datetime.combine(date.today(), datetime.min.time())
    
    patients_today = db.query(Case.user_id).filter(
        Case.created_at >= today_start
    ).distinct().count()
    
    ai_consultations = db.query(Case).count() # Global or per-user? Assuming user context per SaaS pattern.
    # Fixed to user context for SaaS:
    user_consultations = db.query(Case).filter(Case.user_id == current_user.id).count()
    
    return {
        "patients_today": patients_today,
        "ai_consultations": user_consultations,
        "saved_cases": user_consultations 
    }

@router.get("/recent-consultations", response_model=List[RecentConsultation])
def get_recent_consultations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a list of recent consultations with patient names and diagnosis tags.
    """
    results = db.query(Case, User.full_name).join(User).filter(
        Case.user_id == current_user.id
    ).order_by(Case.created_at.desc()).limit(10).all()
    
    consultations = []
    for case, full_name in results:
        # Extract direct primary condition from diagnosis list
        diagnosis_tag = "General"
        if case.diagnosis and len(case.diagnosis) > 0:
            diagnosis_tag = case.diagnosis[0].get("condition", "General")
            
        consultations.append({
            "id": case.id,
            "patient_name": full_name or "Anonymous",
            "date": case.created_at,
            "diagnosis_tag": diagnosis_tag
        })
        
    return consultations
