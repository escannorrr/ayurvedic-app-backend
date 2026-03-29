from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.db.models import User
from app.api.deps import get_current_user
from app.schemas.saas_schemas import UserOut

router = APIRouter()

@router.get("/me", response_model=UserOut)
def get_profile(current_user: User = Depends(get_current_user)):
    """
    Get the profile of the currently authenticated user.
    """
    return current_user

@router.put("/me", response_model=UserOut)
def update_profile(
    full_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update basic profile information.
    """
    current_user.full_name = full_name
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return current_user
