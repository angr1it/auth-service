from fastapi import APIRouter

from api.login.auth import auth_router
from api.login.user import router as user_route


login_router = APIRouter()

login_router.include_router(auth_router, tags=["auth"])
login_router.include_router(user_route, tags=["user"])
