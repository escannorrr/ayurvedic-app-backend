import os
from dotenv import load_dotenv
load_dotenv()

from app.core.security import create_access_token, verify_password
from app.api.deps import SECRET_KEY, ALGORITHM
from jose import jwt
import time

def test_jwt_cycle():
    user_id = 1
    print(f"Creating token for user_id: {user_id}")
    
    token = create_access_token(subject=user_id)
    print(f"Token: {token[:20]}...")
    
    # 1. Immediate Decode
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        decoded_id = payload.get("sub")
        print(f"Decoded sub: {decoded_id} (Type: {type(decoded_id)})")
        
        if str(user_id) == decoded_id:
            print("JWT Validation Success!")
        else:
            print("JWT Validation Mismatch!")
            
    except Exception as e:
        print(f"JWT Validation Error: {e}")

if __name__ == "__main__":
    test_jwt_cycle()
