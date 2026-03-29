from fastapi import APIRouter
from app.api.v1.endpoints import diagnosis, auth, cases, dashboard, users, consultation, search, settings, health

api_router = APIRouter()

# Public & Optional Auth Endpoints
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(diagnosis.router, tags=["diagnosis"])

# Protected SaaS Endpoints
api_router.include_router(cases.router, prefix="/cases", tags=["saved cases"])
api_router.include_router(consultation.router, prefix="/consultation", tags=["consultation"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(users.router, prefix="/users", tags=["user profile"])
api_router.include_router(search.router, prefix="/search", tags=["global search"])
api_router.include_router(settings.router, prefix="/settings", tags=["settings"])
api_router.include_router(health.router, prefix="/system", tags=["health"])
