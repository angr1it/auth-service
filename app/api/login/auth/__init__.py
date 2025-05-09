from fastapi import APIRouter

from api.login.auth.logout import router as logout_route
from api.login.auth.password import router as password_route
from api.login.auth.refresh import router as refresh_route


auth_router = APIRouter()

auth_router.include_router(logout_route, tags=["auth"])
auth_router.include_router(password_route, tags=["auth"])
auth_router.include_router(refresh_route, tags=["auth"])
