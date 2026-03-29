from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.api.deps import get_current_user
from app.db.models import User
from app.schemas.saas_schemas import ProfileOut, ProfileUpdate, PasswordUpdate
from app.services.auth_service import AuthService

router = APIRouter()

@router.get("/profile", response_model=ProfileOut)
def get_profile(current_user: User = Depends(get_current_user)):
    """
    Retrieve clinical profile and preferences for the practitioner.
    """
    return current_user

@router.patch("/profile", response_model=ProfileOut)
def update_profile(
    profile_in: ProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update practitioner details, clinic info, and UI preferences.
    """
    return AuthService.update_profile(db, current_user, profile_in)

@router.patch("/password")
def update_password(
    password_in: PasswordUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Secure password rotation for the authenticated user.
    """
    AuthService.update_password(db, current_user, password_in)
    return {"message": "Password updated successfully"}
