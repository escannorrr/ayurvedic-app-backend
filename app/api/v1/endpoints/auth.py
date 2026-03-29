from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.schemas.saas_schemas import UserOut, UserCreate, Token
from app.services.auth_service import AuthService
from app.api.deps import get_current_user
from app.db.models import User

router = APIRouter()

@router.post("/signup", response_model=UserOut)
def signup(user_in: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user.
    """
    return AuthService.signup(db, user_in)

@router.post("/login", response_model=Token)
def login(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Standard OAuth2 password flow login.
    """
    access_token = AuthService.login(db, form_data.username, form_data.password)
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    """
    Get the profile of the currently authenticated user.
    """
    return current_user
