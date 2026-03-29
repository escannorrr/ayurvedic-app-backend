from sqlalchemy.orm import Session
from app.db.models import User
from app.schemas.saas_schemas import UserCreate, ProfileUpdate, PasswordUpdate
from app.core.security import get_password_hash, verify_password, create_access_token
from fastapi import HTTPException, status
from typing import Optional

class AuthService:
    @staticmethod
    def signup(db: Session, user_in: UserCreate) -> User:
        # Normalize email
        email_ln = user_in.email.lower()
        
        # Check if user already exists
        user_exists = db.query(User).filter(User.email == email_ln).first()
        if user_exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )
        
        # Create new user
        new_user = User(
            email=email_ln,
            hashed_password=get_password_hash(user_in.password),
            full_name=user_in.full_name
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user

    @staticmethod
    def login(db: Session, email: str, password: str) -> str:
        # Normalize email
        email_ln = email.lower()
        user = db.query(User).filter(User.email == email_ln).first()
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        return create_access_token(subject=user.id)

    @staticmethod
    def update_profile(db: Session, user: User, profile_in: ProfileUpdate) -> User:
        if profile_in.full_name is not None:
            user.full_name = profile_in.full_name
        if profile_in.clinic_name is not None:
            user.clinic_name = profile_in.clinic_name
        if profile_in.preferences is not None:
            user.preferences = profile_in.preferences
            
        if profile_in.email is not None and profile_in.email != user.email:
            # Check if new email is taken
            email_exists = db.query(User).filter(User.email == profile_in.email).first()
            if email_exists:
                raise HTTPException(status_code=400, detail="Email already registered")
            user.email = profile_in.email
            
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def update_password(db: Session, user: User, password_in: PasswordUpdate):
        if not verify_password(password_in.old_password, user.hashed_password):
            raise HTTPException(status_code=400, detail="Incorrect current password")
            
        user.hashed_password = get_password_hash(password_in.new_password)
        db.add(user)
        db.commit()
