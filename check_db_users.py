import os
from dotenv import load_dotenv

# MUST LOAD DOTENV FIRST
load_dotenv()

from sqlalchemy import create_engine, text

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

def check_users():
    with engine.connect() as conn:
        print(f"Checking database: {DATABASE_URL}")
        res = conn.execute(text("SELECT email, full_name, hashed_password FROM users")).fetchall()
        print(f"Found {len(res)} users.")
        for row in res:
            # Mask hash for semi-security in logs
            mask_hash = f"{row[2][:5]}...{row[2][-5:]}" if row[2] else "NONE"
            print(f" - Email: {row[0]}, Name: {row[1]}, Hash: {mask_hash}")

if __name__ == "__main__":
    check_users()
