import os
from dotenv import load_dotenv
load_dotenv()

from sqlalchemy.orm import Session
from app.db.base import SessionLocal
from app.services.auth_service import AuthService
from app.core.security import verify_password
from app.db.models import User

def test_login_direct():
    db = SessionLocal()
    email = "Nishad@abc.com"
    password = "1234"
    
    print(f"Testing direct login for {email}...")
    
    # 1. Manual check
    user = db.query(User).filter(User.email == email).first()
    if user:
        print(f"User found: {user.email}")
        is_valid = verify_password(password, user.hashed_password)
        print(f"Password '{password}' vs hash verification: {is_valid}")
        
        # 2. Case sensitivity check
        user_lower = db.query(User).filter(User.email == "nishad@abc.com").first()
        print(f"User found with lower case email: {user_lower is not None}")
        
        # 3. Service login check
        try:
            token = AuthService.login(db, email, password)
            print(f"AuthService.login Success! Token generated.")
        except Exception as e:
            print(f"AuthService.login Failed: {e}")
    else:
        print("User NOT found in database.")
    
    db.close()

if __name__ == "__main__":
    test_login_direct()
