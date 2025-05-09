from fastapi import APIRouter

from api.login import login_router
from api.organization import organization_router
from api.jwks import router as jwks_router


api_router = APIRouter()

api_router.include_router(login_router, prefix="/login", tags=["login"])
api_router.include_router(
    organization_router, prefix="/organization", tags=["organization"]
)
api_router.include_router(jwks_router, tags=["jwks"])
