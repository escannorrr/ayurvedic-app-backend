import os
from dotenv import load_dotenv

# Load .env file automatically
load_dotenv()

class Settings:
    """
    Centralized configuration for the diagnostic engine.
    Uses 'python-dotenv' for local environment variable loading.
    """
    
    # Environment (development/production)
    ENV: str = os.getenv("ENV", "development")
    
    # Core Infrastructure
    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "Ayurvedic AI Diagnosis Engine")
    API_V1_STR: str = os.getenv("API_V1_STR", "/api/v1")
    DEBUG: bool = os.getenv("DEBUG", "False").lower() in ("true", "1", "t")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    
    # Pipeline Settings
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    LLM_MODEL: str = "llama-3.3-70b-versatile"

# Global settings instance
settings = Settings()

# Validation for critical production keys
if settings.ENV == "production" and not settings.GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY must be set in production.")

if not settings.DATABASE_URL:
    # Optional logic to build URL from pieces if DATABASE_URL is missing
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "5432")
    db_name = os.getenv("DB_NAME")
    if all([db_user, db_password, db_name]):
        settings.DATABASE_URL = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
