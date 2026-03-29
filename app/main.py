import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.api import api_router
from app.core.config import settings
from dotenv import load_dotenv
from app.db.base import Base, engine
import app.db.models # Ensure models are registered

# Initialize Environment
load_dotenv()

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_application() -> FastAPI:
    """
    Application Factory Pattern for production-grade FastAPI.
    """
    # Create tables automatically (Simple alternative to Alembic for now)
    Base.metadata.create_all(bind=engine)
    
    application = FastAPI(
        title=settings.PROJECT_NAME,
        debug=settings.DEBUG
    )
    
    # Configure CORS
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"], # In production, replace with specific origins
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include API Routers
    application.include_router(api_router, prefix=settings.API_V1_STR)
    
    @application.get("/health", tags=["monitoring"])
    async def health_check():
        """
        Standard health check endpoint.
        Used for orchestration (Kubernetes, AWS ECS) and monitoring.
        """
        return {"status": "ok"}
        
    return application

app = create_application()
